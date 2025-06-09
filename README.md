# Dynamic Data Visualization App

A HoloViz Panel application for interactive data visualization with dynamic filtering and customizable scatter plots.

## Features

- **Dynamic Filtering**: Add filters for any column with appropriate widgets (range sliders, multi-selectors, regex inputs)
- **Distribution Visualization**: See data distributions with highlighted filter ranges
- **Custom Scatter Plots**: Create scatter plots with customizable axes, size mapping, and color mapping
- **Reactive Updates**: All components update automatically when filters change

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python app.py
```

The app will open in your browser at `http://localhost:5007` in debug mode.

## Project Structure

- `app.py` - Main application file
- `data_generator.py` - Generates example data for testing
- `filter_manager.py` - Handles dynamic filtering functionality
- `scatter_plot_manager.py` - Manages scatter plot creation and customization
- `instruction.md` - Detailed requirements specification

## Usage Guide

1. **Adding Filters**: Select a column from the dropdown and click "Add Filter"
2. **Filter Types**: 
   - Numeric columns → Range slider
   - Categorical columns → Multi-selector
   - Text columns → Regex input
3. **Scatter Plots**: Configure X/Y axes, size mapping, color mapping, and visual settings
4. **Interactive Features**: All plots support hover, box select, and lasso select tools 