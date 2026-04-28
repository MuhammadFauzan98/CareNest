# CareNest

A healthcare management and analysis application built with Flask and machine learning.

## Features

- User authentication and registration
- Health data input and tracking
- Dashboard for health analytics
- Admin panel for user management
- Multi-language support (Bengali, Hindi, Tamil, Telugu)
- ML-based health analysis

## Project Structure

```
CareNest/
├── app.py              # Main Flask application
├── models.py           # Database models
├── ml_model.py         # Machine learning functionality
├── train_model.py      # Model training script
├── requirements.txt    # Python dependencies
├── static/             # Static files (CSS, JS, images)
├── templates/          # HTML templates
├── translations/       # Multi-language support
└── instance/           # Instance-specific files
```

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Features

- **User Management**: Register, login, and manage user accounts
- **Health Tracking**: Input and monitor health data
- **Analytics**: View health analytics on the dashboard
- **Admin Panel**: Manage users and view system statistics
- **Multi-language**: Support for multiple languages

## License

This project is licensed under the MIT License.
