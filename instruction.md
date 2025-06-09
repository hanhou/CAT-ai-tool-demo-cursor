# HoloViz Panel Data Visualization Framework Requirements

## General Requirements

Build a general framework for a HoloViz Panel app for data visualization with the following specifications:

- Use Panel's **declarative and reactive approach** for interactivity when possible (e.g., `pn.bind(...)`, `@pn.depends`)
- Use **Object-Oriented Programming (OOP) style** for the app architecture

## Detailed Requirements

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
- Show the **distribution of the selected column** beside each filter widget
- **Highlight the selected range** on the distribution visualization
- Ensure visual feedback shows the current filter state

#### 4. Reactive Data Updates
- When adding a new filter, **update the data table** immediately
- Ensure that all **distributions are based on currently filtered data**
- Maintain reactivity across all components when filters change

### Dynamic Scatter Plots

#### 1. Custom Scatter Plot Creation
Enable users to create any custom scatter plot with the following options:

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

#### 2. Cross-Plot Selection Synchronization
- Support **multiple scatter plots** simultaneously
- Implement **box selection** and **lasso selection** tools
- **Sync selections across all plots**: when user selects points in one plot, highlight the same data points in all other plots
- Maintain selection state across plot interactions

## Technical Implementation Notes

- Leverage Panel's reactive programming paradigm for seamless interactivity
- Design with modularity in mind for easy extension and maintenance
- Ensure efficient data handling for real-time filtering and visualization updates
- Implement proper error handling for edge cases (empty selections, invalid data types, etc.) 