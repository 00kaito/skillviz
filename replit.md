# Job Market Analytics for Engineers

## Overview

This is a Streamlit-based web application for analyzing job market data specifically for engineers. The application processes job posting data in JSON format and provides comprehensive analytics including skill demand analysis, experience level distribution, and location-based hiring trends. Users can upload job data via file upload or direct JSON input, and the system generates interactive visualizations to help understand current market trends and requirements.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid development of data applications
- **Layout**: Wide layout with expandable sidebar for data input and filtering controls
- **Session State Management**: Streamlit session state for maintaining data persistence across user interactions
- **Input Methods**: Dual input options (file upload and direct JSON paste) for maximum flexibility

### Data Processing Architecture
- **Modular Design**: Separated concerns with dedicated classes for data processing (`JobDataProcessor`) and visualization (`JobMarketVisualizer`)
- **Data Validation**: Built-in validation for required columns and data integrity checks
- **Data Cleaning Pipeline**: Automated normalization of city names, company names, experience levels, and skills data
- **Error Handling**: Comprehensive error handling for JSON parsing and data validation failures

### Visualization Architecture
- **Library**: Plotly for interactive charts and graphs
- **Chart Types**: Bar charts for skills demand, distribution charts for experience levels, and location-based analytics
- **Responsive Design**: Charts adapt to different screen sizes with configurable parameters
- **Color Schemes**: Consistent color palettes using viridis scale for visual coherence

### Data Schema
The application expects JSON data with the following required fields:
- `title`: Job title/position
- `companyName`: Company offering the position
- `city`: Job location
- `experienceLevel`: Required experience level
- `requiredSkills`: Array of technical skills required

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for the user interface
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualization library (plotly.express and plotly.graph_objects)
- **json**: JSON data parsing and handling
- **collections**: Counter and defaultdict for data aggregation
- **datetime**: Date and time handling
- **re**: Regular expressions for data cleaning
- **numpy**: Numerical computing support
- **io**: Input/output operations for file handling

### Data Requirements
- JSON format input data containing job market information
- No external databases or APIs - operates on user-provided data
- File upload capability through Streamlit's native file handling