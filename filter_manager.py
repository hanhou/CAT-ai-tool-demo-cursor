import panel as pn
import pandas as pd
import numpy as np
import holoviews as hv
from holoviews import opts
import param
import re

class FilterManager(param.Parameterized):
    """Manages dynamic filtering with distribution visualization"""
    
    # Parameter to trigger updates when filtered data changes
    filtered_data = param.DataFrame(default=pd.DataFrame())
    
    def __init__(self, data, **params):
        super().__init__(**params)
        self.original_data = data.copy()
        self.filtered_data = data.copy()
        self.active_filters = {}
        self._filter_components = {}
        self._update_callback = None
        
        # Create initial controls
        self.filter_controls = self._create_filter_controls()
        
    def set_update_callback(self, callback):
        """Set callback function to notify when data changes"""
        self._update_callback = callback
        
    def _create_filter_controls(self):
        """Create the main filter control interface"""
        # Column selector for adding new filters
        numeric_cols = self.original_data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = [col for col in self.original_data.columns 
                          if self.original_data[col].dtype == 'object' or 
                          self.original_data[col].nunique() < 10]
        text_cols = [col for col in self.original_data.columns 
                    if self.original_data[col].dtype == 'object' and 
                    self.original_data[col].nunique() >= 10]
        
        all_cols = list(self.original_data.columns)
        
        self.column_selector = pn.widgets.Select(
            name="Select Column to Filter",
            value=all_cols[0] if all_cols else None,
            options=all_cols,
            width=200
        )
        
        self.add_filter_button = pn.widgets.Button(
            name="Add Filter",
            button_type="primary",
            width=100
        )
        self.add_filter_button.on_click(self._add_filter)
        
        # Container for active filters
        self.filters_container = pn.Column()
        
        return pn.Column(
            pn.Row(self.column_selector, self.add_filter_button),
            self.filters_container
        )
    
    def _add_filter(self, event):
        """Add a new filter for the selected column"""
        column = self.column_selector.value
        if column and column not in self.active_filters:
            filter_widget = self._create_filter_widget(column)
            self.active_filters[column] = filter_widget
            self._update_filters_display()
            self._apply_filters()
    
    def _create_filter_widget(self, column):
        """Create appropriate filter widget based on column type"""
        col_data = self.original_data[column]
        
        if pd.api.types.is_numeric_dtype(col_data):
            return self._create_numeric_filter(column, col_data)
        elif col_data.nunique() < 10:
            return self._create_categorical_filter(column, col_data)
        else:
            return self._create_text_filter(column, col_data)
    
    def _create_numeric_filter(self, column, col_data):
        """Create range slider for numeric columns"""
        min_val, max_val = col_data.min(), col_data.max()
        
        slider = pn.widgets.RangeSlider(
            name=f"{column}",
            start=min_val,
            end=max_val,
            value=(min_val, max_val),
            step=(max_val - min_val) / 100,
            width=300
        )
        
        remove_btn = pn.widgets.Button(name="✕", width=30, button_type="primary")
        
        # Create a pane that will hold the distribution plot
        dist_pane = pn.pane.HoloViews(object=None)
        
        def update_distribution():
            """Update the distribution plot with current slider values"""
            current_range = slider.value
            new_plot = self._create_distribution_plot(column, col_data, current_range)
            dist_pane.object = new_plot.object
        
        # Initialize the distribution plot
        update_distribution()
        
        def update_filter(event):
            self._apply_filters()
            # Update distribution plot with new selection
            update_distribution()
        
        def remove_filter(event):
            self._remove_filter(column)
        
        slider.param.watch(update_filter, 'value')
        remove_btn.on_click(remove_filter)
        
        filter_container = pn.Column(
            pn.Row(slider, remove_btn),
            dist_pane
        )
        
        self._filter_components[column] = filter_container
        return {'widget': slider, 'type': 'numeric', 'container': filter_container}
    
    def _create_categorical_filter(self, column, col_data):
        """Create multi-select for categorical columns"""
        unique_values = sorted(col_data.unique())
        
        multiselect = pn.widgets.MultiSelect(
            name=f"{column}",
            value=unique_values,
            options=unique_values,
            size=min(len(unique_values), 8),
            width=300
        )
        
        remove_btn = pn.widgets.Button(name="✕", width=30, button_type="primary")
        
        # Create a pane that will hold the distribution plot
        dist_pane = pn.pane.HoloViews(object=None)
        
        def update_distribution():
            """Update the distribution plot with current selection"""
            current_selection = multiselect.value
            new_plot = self._create_distribution_plot(column, col_data, current_selection)
            dist_pane.object = new_plot.object
        
        # Initialize the distribution plot
        update_distribution()
        
        def update_filter(event):
            self._apply_filters()
            # Update distribution plot
            update_distribution()
        
        def remove_filter(event):
            self._remove_filter(column)
        
        multiselect.param.watch(update_filter, 'value')
        remove_btn.on_click(remove_filter)
        
        filter_container = pn.Column(
            pn.Row(multiselect, remove_btn),
            dist_pane
        )
        
        self._filter_components[column] = filter_container
        return {'widget': multiselect, 'type': 'categorical', 'container': filter_container}
    
    def _create_text_filter(self, column, col_data):
        """Create regex text input for text columns"""
        text_input = pn.widgets.TextInput(
            name=f"{column} (regex)",
            placeholder="Enter regex pattern...",
            width=300
        )
        
        remove_btn = pn.widgets.Button(name="✕", width=30, button_type="primary")
        
        # For text columns, show word count distribution or similar
        dist_plot = self._create_text_distribution_plot(column, col_data, "")
        
        def update_filter(event):
            self._apply_filters()
        
        def remove_filter(event):
            self._remove_filter(column)
        
        text_input.param.watch(update_filter, 'value')
        remove_btn.on_click(remove_filter)
        
        filter_container = pn.Column(
            pn.Row(text_input, remove_btn),
            dist_plot
        )
        
        self._filter_components[column] = filter_container
        return {'widget': text_input, 'type': 'text', 'container': filter_container}
    
    def _create_distribution_plot(self, column, col_data, selected_range):
        """Create distribution plot with highlighted selection"""
        try:
            if pd.api.types.is_numeric_dtype(col_data):
                # Histogram for numeric data
                hist_data = np.histogram(col_data.dropna(), bins=30)
                edges = hist_data[1]
                counts = hist_data[0]
                
                # Create base histogram plot
                hist_plot = hv.Histogram((edges, counts)).opts(
                    width=350, height=150, 
                    xlabel=column, ylabel='Count',
                    title=f'{column} Distribution',
                    color='lightblue', alpha=0.7
                )
                
                # Add red shaded area for selected range
                if isinstance(selected_range, tuple):
                    min_sel, max_sel = selected_range
                    
                    # Create vertical span for the selected range
                    y_max = max(counts) if len(counts) > 0 else 1
                    
                    # Create a shaded rectangle for the selected range
                    rect = hv.Rectangles([(min_sel, 0, max_sel, y_max)]).opts(
                        color='red', alpha=0.3, line_color='red', line_width=2
                    )
                    
                    hist_plot = hist_plot * rect
                
                return pn.pane.HoloViews(hist_plot)
            
            else:
                # Bar chart for categorical data
                value_counts = col_data.value_counts()
                bar_data = [(str(k), v) for k, v in value_counts.items()]
                
                # Create base bar plot
                bar_plot = hv.Bars(bar_data).opts(
                    width=350, height=150,
                    xlabel=column, ylabel='Count',
                    title=f'{column} Distribution',
                    xrotation=45,
                    color='lightblue', alpha=0.7
                )
                
                # Highlight selected categories with red bars
                if isinstance(selected_range, list):
                    # Create overlay for selected categories
                    selected_data = [(str(k), v) for k, v in value_counts.items() 
                                   if k in selected_range]
                    if selected_data:
                        selected_bars = hv.Bars(selected_data).opts(
                            color='red', alpha=0.6
                        )
                        bar_plot = bar_plot * selected_bars
                
                return pn.pane.HoloViews(bar_plot)
                
        except Exception as e:
            return pn.pane.HTML(f"<p>Could not create distribution plot: {str(e)}</p>")
    
    def _create_text_distribution_plot(self, column, col_data, pattern):
        """Create distribution plot for text columns"""
        try:
            # Show length distribution
            lengths = col_data.astype(str).str.len()
            hist_data = np.histogram(lengths, bins=20)
            edges = hist_data[1]
            counts = hist_data[0]
            
            hist_plot = hv.Histogram((edges, counts)).opts(
                width=350, height=150,
                xlabel=f'{column} Length', ylabel='Count',
                title=f'{column} Length Distribution',
                color='lightblue', alpha=0.7
            )
            
            # If there's a pattern, we could highlight matching text lengths
            # For now, just show the basic distribution
            
            return pn.pane.HoloViews(hist_plot)
            
        except Exception as e:
            return pn.pane.HTML(f"<p>Could not create distribution plot: {str(e)}</p>")
    
    def _remove_filter(self, column):
        """Remove a filter"""
        if column in self.active_filters:
            del self.active_filters[column]
            del self._filter_components[column]
            self._update_filters_display()
            self._apply_filters()
    
    def _update_filters_display(self):
        """Update the filters container display"""
        containers = [filter_info['container'] for filter_info in self.active_filters.values()]
        self.filters_container.objects = containers
    
    def _apply_filters(self):
        """Apply all active filters to the data"""
        filtered_data = self.original_data.copy()
        
        for column, filter_info in self.active_filters.items():
            widget = filter_info['widget']
            filter_type = filter_info['type']
            
            if filter_type == 'numeric':
                min_val, max_val = widget.value
                filtered_data = filtered_data[
                    (filtered_data[column] >= min_val) & 
                    (filtered_data[column] <= max_val)
                ]
            
            elif filter_type == 'categorical':
                selected_values = widget.value
                if selected_values:  # Only filter if something is selected
                    filtered_data = filtered_data[filtered_data[column].isin(selected_values)]
            
            elif filter_type == 'text':
                pattern = widget.value
                if pattern:  # Only filter if pattern is provided
                    try:
                        mask = filtered_data[column].astype(str).str.contains(
                            pattern, case=False, regex=True, na=False
                        )
                        filtered_data = filtered_data[mask]
                    except re.error:
                        # Invalid regex, skip this filter
                        pass
        
        self.filtered_data = filtered_data
        
        # Notify the main app of the data change
        if self._update_callback:
            self._update_callback(filtered_data) 