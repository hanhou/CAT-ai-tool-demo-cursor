# HoloViz Panel Data Visualization Framework Requirements

## General Requirements

Build a general framework for a HoloViz Panel app for data visualization with the following specifications:

- Use Panel's **declarative and reactive approach** for interactivity when possible (e.g., `pn.bind(...)`, `@pn.depends`)
- Use **Object-Oriented Programming (OOP) style** for the app architecture

## Detailed Requirements

### Data
- Generate example data for testing

### Dynamic Filtering

#### 1. Support Dynamic Filtering
- Enable users to add filters for **any columns** in the dataset
- Provide a flexible interface for adding/removing column filters dynamically

#### 2. Context-Aware Widget Selection
When a user adds a column to filter, automatically select the appropriate widget based on data type:

- **Range Slider**: For numeric columns
- **Multi-selector**: For categorical columns or columns with `nunique() < 10`
- **Regex Input**: For text columns

#### 3. Distribution Visualization
- Show the **distribution of the selected column** below each filter widget
- For each distribution plot, show the full range of data before the **current filter** and use a red shaded area to **highlight the selected range**.


#### 4. Reactive Data Updates
- When adding a new filter, **update the data table** immediately and **update the scatter plot**
- Evaluate filters from top to bottom, i.e., when 
- Change of filters should update the table and the scatter plot

### Dynamic Scatter Plots

#### 1. Custom Scatter Plot Creation
Enable users to create a custom scatter plot with the following options:

**a) Axis Selection**
- Choose any column as **X-axis** (numeric, categorical, or `nunique() < 10`)
- Choose any column as **Y-axis** (numeric, categorical, or `nunique() < 10`)

**b) Size Mapping**
- Choose any **numeric column** for size mapping
- Provide controls for:
  - `min_size`: Minimum point size
  - `max_size`: Maximum point size  
  - `gamma_size`: Size scaling gamma correction

**c) Color Mapping**
- Choose any column for color mapping (numeric or categorical)
- Provide **selectable color palettes**
- Support both continuous and discrete color schemes


## Miscs
- Keep the project files modular.
- Run the app in debug mode