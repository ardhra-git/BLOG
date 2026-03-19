# The Daily Read — Blog Website

Full-stack blog with HTML, CSS, JavaScript, Python FastAPI, and PostgreSQL.

## Project Structure
```
blog/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── main.js
├── backend/
│   ├── main.py
│   └── requirements.txt
├── database/
│   └── schema.sql
└── README.md
```

## Tech Stack
| Layer    | Technology              |
|----------|-------------------------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend  | Python 3 + FastAPI      |
| Database | PostgreSQL              |
| Server   | Uvicorn                 |

## Setup

### 1 — Install PostgreSQL
Download from https://www.postgresql.org/download/windows/
Set root password to: 1234567

### 2 — Create Database
Open pgAdmin or psql and run:
```sql
CREATE DATABASE blog_db;
```
Then import schema:
```
psql -U postgres -f D:\blog\database\schema.sql
```

### 3 — Install Python dependencies
```bash
cd backend
python -m pip install -r requirements.txt
```

### 4 — Run the server
```bash
python -m uvicorn main:app --reload
```

### 5 — Open browser
http://localhost:8000

## API Endpoints
| Method | Route         | Description       |
|--------|---------------|-------------------|
| GET    | /posts        | Get all posts     |
| GET    | /posts/{id}   | Get single post   |
| POST   | /posts        | Create post       |
| PUT    | /posts/{id}   | Update post       |
| DELETE | /posts/{id}   | Delete post       |
| POST   | /contact      | Submit contact    |
