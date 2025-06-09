import panel as pn
import pandas as pd
import numpy as np
import holoviews as hv
from holoviews import opts
import param

class ScatterPlotManager(param.Parameterized):
    """Manages dynamic scatter plot creation and customization"""
    
    # Parameter to trigger plot updates
    plot_update_trigger = param.Integer(default=0)
    
    def __init__(self, **params):
        super().__init__(**params)
        self.plot_controls = self._create_plot_controls()
        
        # Default values
        self.x_column = None
        self.y_column = None
        self.size_column = None
        self.color_column = None
        self.min_size = 5
        self.max_size = 20
        self.gamma_size = 1.0
        self.color_palette = 'viridis'
        
        # Set up widget callbacks
        self._setup_widget_callbacks()
        
    def _create_plot_controls(self):
        """Create the scatter plot control interface"""
        # Initially empty - will be populated when data is available
        self.x_selector = pn.widgets.Select(
            name="X Axis",
            value=None,
            options=[],
            width=180
        )
        
        self.y_selector = pn.widgets.Select(
            name="Y Axis", 
            value=None,
            options=[],
            width=180
        )
        
        self.size_selector = pn.widgets.Select(
            name="Size Mapping",
            value=None,
            options=[None],
            width=180
        )
        
        self.color_selector = pn.widgets.Select(
            name="Color Mapping",
            value=None,
            options=[None],
            width=180
        )
        
        # Size controls
        self.min_size_input = pn.widgets.IntInput(
            name="Min Size",
            value=5,
            start=1,
            end=50,
            width=80
        )
        
        self.max_size_input = pn.widgets.IntInput(
            name="Max Size", 
            value=20,
            start=1,
            end=100,
            width=80
        )
        
        self.gamma_input = pn.widgets.FloatInput(
            name="Gamma",
            value=1.0,
            start=0.1,
            end=3.0,
            step=0.1,
            width=80
        )
        
        # Color palette selector
        self.palette_selector = pn.widgets.Select(
            name="Color Palette",
            value='viridis',
            options=['viridis', 'plasma', 'inferno', 'magma', 'cividis', 
                    'Spectral', 'RdYlBu', 'RdBu', 'coolwarm', 'Set1', 'Set2', 'Set3'],
            width=120
        )
        
        return pn.Column(
            pn.Row(self.x_selector, self.y_selector),
            pn.Row(self.size_selector, self.color_selector),
            "### Size Settings",
            pn.Row(self.min_size_input, self.max_size_input, self.gamma_input),
            "### Color Settings", 
            self.palette_selector
        )
    
    def _setup_widget_callbacks(self):
        """Set up callbacks for all widgets to trigger plot updates"""
        def trigger_update(event):
            self.plot_update_trigger += 1
        
        # Add callbacks to all widgets
        self.x_selector.param.watch(trigger_update, 'value')
        self.y_selector.param.watch(trigger_update, 'value')
        self.size_selector.param.watch(trigger_update, 'value')
        self.color_selector.param.watch(trigger_update, 'value')
        self.min_size_input.param.watch(trigger_update, 'value')
        self.max_size_input.param.watch(trigger_update, 'value')
        self.gamma_input.param.watch(trigger_update, 'value')
        self.palette_selector.param.watch(trigger_update, 'value')
    
    def update_options(self, data):
        """Update selector options based on available data columns"""
        if data.empty:
            return
            
        # Get column types
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = [col for col in data.columns 
                          if data[col].dtype == 'object' or data[col].nunique() < 10]
        
        # Columns suitable for x/y axes (numeric + low cardinality categorical)
        axis_cols = numeric_cols + [col for col in categorical_cols if data[col].nunique() < 10]
        
        # Update selectors
        self.x_selector.options = axis_cols
        self.y_selector.options = axis_cols
        
        # Size mapping only for numeric columns
        self.size_selector.options = [None] + numeric_cols
        
        # Color mapping for numeric and categorical
        self.color_selector.options = [None] + numeric_cols + categorical_cols
        
        # Set default values if not already set
        if self.x_column is None and axis_cols:
            self.x_selector.value = axis_cols[0]
            self.x_column = axis_cols[0]
            
        if self.y_column is None and len(axis_cols) > 1:
            self.y_selector.value = axis_cols[1]
            self.y_column = axis_cols[1]
    
    def create_plot(self, data):
        """Create scatter plot based on current settings"""
        if data.empty:
            return pn.pane.HTML("<p>No data available</p>")
        
        # Update options based on current data
        self.update_options(data)
        
        # Get current values from widgets
        x_col = self.x_selector.value
        y_col = self.y_selector.value
        size_col = self.size_selector.value
        color_col = self.color_selector.value
        
        if not x_col or not y_col:
            return pn.pane.HTML("<p>Please select X and Y columns</p>")
        
        try:
            # Prepare data for plotting
            plot_data = data[[x_col, y_col]].copy()
            
            # Handle missing values
            plot_data = plot_data.dropna()
            
            if plot_data.empty:
                return pn.pane.HTML("<p>No valid data points to plot</p>")
            
            # Create base scatter plot
            if pd.api.types.is_numeric_dtype(data[x_col]) and pd.api.types.is_numeric_dtype(data[y_col]):
                # Both numeric - standard scatter
                points = hv.Points(plot_data, [x_col, y_col])
            else:
                # Handle categorical axes
                points = hv.Points(plot_data, [x_col, y_col])
            
            # Prepare final plot data with additional dimensions
            plot_data_final = plot_data.copy()
            plot_dimensions = [x_col, y_col]
            value_dims = []
            
            # Apply size mapping if specified
            sizes = None
            if size_col and size_col in data.columns:
                size_data = data.loc[plot_data.index, size_col]
                if pd.api.types.is_numeric_dtype(size_data):
                    # Normalize size values
                    min_val, max_val = size_data.min(), size_data.max()
                    if max_val > min_val:
                        normalized_sizes = (size_data - min_val) / (max_val - min_val)
                        # Apply gamma correction
                        gamma = self.gamma_input.value
                        normalized_sizes = normalized_sizes ** gamma
                        # Scale to size range
                        min_size = self.min_size_input.value
                        max_size = self.max_size_input.value
                        sizes = min_size + normalized_sizes * (max_size - min_size)
                        plot_data_final['size'] = sizes
                        value_dims.append('size')
            
            # Apply color mapping if specified
            if color_col and color_col in data.columns:
                color_data = data.loc[plot_data.index, color_col]
                plot_data_final['color'] = color_data
                value_dims.append('color')
            
            # Create points with appropriate dimensions
            points = hv.Points(plot_data_final, plot_dimensions, value_dims)
            
            # Configure plot options
            plot_opts = {
                'width': 600,
                'height': 400,
                'tools': ['hover', 'box_select', 'lasso_select'],
                'size': 'size' if size_col else 10,
                'alpha': 0.7,
                'xlabel': x_col,
                'ylabel': y_col,
                'title': f'{y_col} vs {x_col}'
            }
            
            # Add color options if color mapping is used
            if color_col:
                plot_opts['color'] = 'color'
                plot_opts['cmap'] = self.palette_selector.value
                
                # Use colorbar for numeric, legend for categorical
                if pd.api.types.is_numeric_dtype(data[color_col]):
                    plot_opts['colorbar'] = True
                else:
                    plot_opts['legend'] = 'right'
            
            points = points.opts(**plot_opts)
            
            return pn.pane.HoloViews(points)
            
        except Exception as e:
            return pn.pane.HTML(f"<p>Error creating plot: {str(e)}</p>")
    
    def get_current_settings(self):
        """Get current plot settings as a dictionary"""
        return {
            'x_column': self.x_selector.value,
            'y_column': self.y_selector.value,
            'size_column': self.size_selector.value,
            'color_column': self.color_selector.value,
            'min_size': self.min_size_input.value,
            'max_size': self.max_size_input.value,
            'gamma_size': self.gamma_input.value,
            'color_palette': self.palette_selector.value
        } 