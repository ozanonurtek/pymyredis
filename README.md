# PyMyRedis - Redis Management Web Application

PyMyRedis is a web-based Redis management tool built with Python Flask and Flask AppBuilder. It provides a user interface for managing Redis connections, viewing Redis data, and controlling access through team-based role management.

## Features

- Redis connection management
- View Redis keys and values
- Team-based access control
- Activity tracking
- Kubernetes deployment via Helm charts

## Technology Stack

- Python 3
- Flask
- Flask AppBuilder
- Redis
- SQLAlchemy (for user/role management)
- Helm (for Kubernetes deployment)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pymyredis.git
   cd pymyredis
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the application by editing `config.py`:
   ```python
   # Database settings (for user/role management)
   SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
   ```

5. Initialize the database:
   ```bash
   flask fab create-admin
   ```

6. Run the application:
   ```bash
   python run.py
   ```

## Configuration

The main configuration file is `config.py`. Key settings include:

- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `SECRET_KEY`: Application secret key
- `BABEL_DEFAULT_LOCALE`: Default language
- `FAB_ROLES`: Custom roles configuration

## Running the Application

Start the development server:
```bash
python run.py
```

The application will be available at http://localhost:5000

## Deployment

The application can be deployed to Kubernetes using the provided Helm charts:

1. Package the Helm chart:
   ```bash
   helm package helm/charts
   ```

2. Install the chart:
   ```bash
   helm install pymyredis ./pymyredis-0.1.0.tgz
   ```

Configuration values can be set in `helm/charts/values.yaml`

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
