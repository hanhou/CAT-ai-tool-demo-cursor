import panel as pn
import pandas as pd
import numpy as np
import holoviews as hv
from holoviews import opts
import param

# Enable Panel extensions
pn.extension('tabulator')
hv.extension('bokeh')

from data_generator import generate_example_data
from filter_manager import FilterManager
from scatter_plot_manager import ScatterPlotManager

class DataVisualizationApp(param.Parameterized):
    """Main Panel app for dynamic data visualization"""
    
    # Parameters for reactive updates
    filtered_data = param.DataFrame(default=pd.DataFrame())
    
    def __init__(self, **params):
        super().__init__(**params)
        
        # Generate example data
        self.data = generate_example_data()
        self.filtered_data = self.data.copy()
        
        # Initialize managers
        self.filter_manager = FilterManager(self.data)
        self.scatter_manager = ScatterPlotManager()
        
        # Set up reactive dependencies
        self._setup_dependencies()
        
        # Create layout
        self.layout = self._create_layout()
    
    def _setup_dependencies(self):
        """Set up reactive dependencies between components"""
        # Set up a manual update method that the filter manager can call
        self.filter_manager.set_update_callback(self._update_from_filters)
        
    def _update_from_filters(self, new_data):
        """Update filtered data when filters change"""
        self.filtered_data = new_data
        
    @pn.depends('filtered_data')
    def data_table(self):
        """Create reactive data table"""
        return pn.widgets.Tabulator(
            self.filtered_data,
            pagination='remote',
            page_size=10,
            sizing_mode='stretch_width',
            height=300
        )
    
    @pn.depends('filtered_data', 'scatter_manager.plot_update_trigger')
    def scatter_plot(self):
        """Create reactive scatter plot"""
        return self.scatter_manager.create_plot(self.filtered_data)
    
    def _create_layout(self):
        """Create the main app layout"""
        # Sidebar with filters and scatter plot controls
        sidebar = pn.Column(
            "## Dynamic Filters",
            self.filter_manager.filter_controls,
            "---",
            "## Scatter Plot Settings", 
            self.scatter_manager.plot_controls,
            width=400,
            scroll=True
        )
        
        # Main content area
        main_content = pn.Column(
            "## Data Table",
            self.data_table,
            "## Scatter Plot",
            self.scatter_plot,
            sizing_mode='stretch_width'
        )
        
        # Complete layout
        return pn.template.MaterialTemplate(
            title="Dynamic Data Visualization",
            sidebar=[sidebar],
            main=[main_content],
            header_background='#2596be',
        )
    
    def servable(self):
        """Return servable layout"""
        return self.layout

def create_app():
    """Create and return the app instance"""
    app = DataVisualizationApp()
    return app.servable()

if __name__ == "__main__":
    # Create app
    app = create_app()
    
    # Serve the app in debug mode
    pn.serve(app, debug=True, show=True, port=5009) 