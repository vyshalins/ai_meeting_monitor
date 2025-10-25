# AI Meeting Monitor

This project, "AI Meeting Monitor," is designed to facilitate the monitoring and analysis of meetings using artificial intelligence. The backend is built with FastAPI and Uvicorn, providing a robust and scalable solution for handling various functionalities related to meetings.

## Project Structure

The project is organized into several key directories and files:

- **app/**: Contains the main application code.
  - **main.py**: Entry point of the application, initializes FastAPI and sets up routes.
  - **api/**: Contains the API routes organized by version.
    - **v1/**: Version 1 of the API, including routes for meetings, uploads, transcriptions, and processing.
  - **core/**: Core configuration and utility files.
  - **models/**: Pydantic models for data validation.
  - **schemas/**: Schemas for request and response validation.
  - **services/**: Business logic and service layer for handling complex operations.
  - **db/**: Database-related files, including session management and migrations.
  - **utils/**: Utility functions and helpers.
  - **tests/**: Unit tests for the application.

- **scripts/**: Contains shell scripts for starting the application and initializing the database.

- **alembic.ini**: Configuration file for database migrations.

- **Dockerfile**: Docker configuration for containerizing the application.

- **docker-compose.yml**: Docker Compose configuration for managing multi-container applications.

- **pyproject.toml**: Project metadata and dependencies.

- **requirements.txt**: Lists the dependencies required for the project.

- **.env.example**: Example environment variables for configuration.

- **.gitignore**: Specifies files and directories to be ignored by Git.

## Getting Started

To get started with the AI Meeting Monitor project, follow these steps:

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd AI-Meeting-Monitor/backend
   ```

2. **Set up a virtual environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the API documentation**: Open your browser and navigate to `http://localhost:8000/docs` to view the interactive API documentation.

## Future Development

This project is designed to be modular and extensible. Future enhancements may include:

- Integration with external AI services for advanced transcription and analysis.
- Improved error handling and logging mechanisms.
- Additional features for meeting management and reporting.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.