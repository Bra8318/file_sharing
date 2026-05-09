# File Sharing App

This repository contains a simple file sharing application with a FastAPI backend and a basic HTML frontend.

## Project Structure

- `backend/` - FastAPI backend service for uploading, downloading, and managing files and folders.
- `frontend/` - Static HTML files for a basic user interface.

## Backend Overview

The backend provides endpoints to:
- upload single files
- download files by ID
- upload folders with multiple files and paths
- download folders as a ZIP archive
- automatically delete expired files and folders on a schedule

It uses:
- FastAPI
- SQLAlchemy
- a database configured through `backend/db.env`

## Frontend Overview

The frontend is static HTML and can be served locally using a simple HTTP server.

## Setup

1. Open a terminal in `backend/`.
2. Activate the Python virtual environment:

```powershell
cd backend
.\in\activate   # or .\Scripts\activate on Windows PowerShell
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Ensure `backend/db.env` is configured with the correct `db_url` and required environment values.

## Run Backend

Start the FastAPI app with Uvicorn:

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## Run Frontend

Serve the `frontend/` folder with a static server, for example:

```powershell
cd frontend
python -m http.server 5500
```

Then open `http://127.0.0.1:5500` in your browser.

## API Endpoints

- `GET /` - basic health check
- `GET /check_db` - verify database connectivity
- `POST /Upload_file` - upload a single file
- `GET /get_file/{id}` - download a file by ID
- `POST /Upload_folder` - upload a folder with files and paths
- `GET /get_folder/{id}` - download a folder as a ZIP by folder ID

## Notes

- Uploaded files are stored in the `backend/uploads/` directory.
- Single file uploads expire after 24 hours.
- Folder uploads expire after 5 hours.
- The backend automatically cleans up expired files and folders every 5 minutes.
