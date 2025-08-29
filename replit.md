# SkillViz Analytics for Engineers

## Overview

This is a Streamlit-based web application for analyzing job market data specifically for engineers. The application features a complete user authentication system with role-based access control. Administrators can upload and manage job posting data in JSON format, while regular users can browse and analyze the data through comprehensive analytics including skill demand analysis, experience level distribution, and location-based hiring trends. The system provides interactive visualizations and trend analysis based on publication dates.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Authentication System
- **User Authentication**: Complete login system with SHA256 password hashing
- **Role-Based Access Control**: Admin and regular user roles with different permissions
- **User Management**: Admin can create new user accounts and manage existing users
- **Session Management**: Secure session handling with automatic logout functionality

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid development of data applications
- **Layout**: Wide layout with expandable sidebar for data input and filtering controls (admin) or viewing info (users)
- **Session State Management**: Streamlit session state for maintaining data persistence across user interactions
- **Input Methods**: Admin-only dual input options (file upload and direct JSON paste) for maximum flexibility

### Data Processing Architecture
- **Modular Design**: Separated concerns with dedicated classes for data processing (`JobDataProcessor`), visualization (`JobMarketVisualizer`), and authentication (`AuthManager`)
- **Category Management**: Data organization by user-defined categories with duplicate detection
- **Data Validation**: Built-in validation for required columns and data integrity checks
- **Data Cleaning Pipeline**: Automated normalization of city names, company names, experience levels, and skills data
- **Error Handling**: Comprehensive error handling for JSON parsing and data validation failures

### Visualization Architecture
- **Library**: Plotly for interactive charts and graphs
- **Chart Types**: Bar charts for skills demand, distribution charts for experience levels, location-based analytics, and time-series trends
- **Trend Analysis**: Skills demand over time and job posting trends based on `publishedAt` field
- **Responsive Design**: Charts adapt to different screen sizes with configurable parameters
- **Color Schemes**: Consistent color palettes using viridis scale for visual coherence

### Data Schema
The application expects JSON data with the following required fields:
- `role`: Job title/position
- `company`: Company offering the position
- `city`: Job location
- `seniority`: Required seniority level (e.g., Junior, Mid, Senior, Expert)
- `skills`: Object containing technical skills with proficiency levels (e.g., {"Python": "Senior", "SQL": "Regular"})
- `employment_type`: Type of employment (e.g., B2B, UoP)
- `job_time_type`: Working time (e.g., Full-time, Part-time)
- `remote`: Boolean indicating if position is remote
- `salary`: Salary range (e.g., "10 000 - 16 000 PLN")
- `published_date`: Publication date in DD.MM.YYYY format
- `url`: Link to job posting

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
- **hashlib**: SHA256 password hashing for authentication

### Authentication Credentials
- **Admin Account**: username: `skillviz`, password: `Skillviz^2`
- **Test User Account**: username: `testuser`, password: `test123`
- **User Registration**: Admin can create additional user accounts

### Data Requirements
- JSON format input data containing job market information
- Admin-only data upload and management capabilities
- Category-based data organization with duplicate detection
- Trend analysis based on job publication dates (`publishedAt` field)
- No external databases - operates on session-based data storage