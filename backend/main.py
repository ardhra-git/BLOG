# backend/main.py
# Local: python -m uvicorn main:app --reload
# Render: uvicorn backend.main:app --host 0.0.0.0 --port $PORT

from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import psycopg2
import psycopg2.extras
import re, os

# ─── APP ──────────────────────────────────────────────────────
app = FastAPI(title="Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend — robust absolute path, works on Render & locally
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# ─── DATABASE ─────────────────────────────────────────────────
# On Render: set DATABASE_URL = Internal Database URL from Render PostgreSQL.
# Locally:   export DATABASE_URL=postgresql://postgres:1234567@localhost:5432/blog_db

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    # Local fallback using individual env vars or defaults
    return psycopg2.connect(
        host     = os.environ.get("DB_HOST",     "localhost"),
        port     = int(os.environ.get("DB_PORT", "5432")),
        dbname   = os.environ.get("DB_NAME",     "blog_db"),
        user     = os.environ.get("DB_USER",     "postgres"),
        password = os.environ.get("DB_PASSWORD", "1234567"),
    )

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))

# ─── SCHEMA ───────────────────────────────────────────────────
class PostIn(BaseModel):
    tag:       str
    title:     str
    excerpt:   str
    body:      str
    read_time: str = "3 min read"

# ─── ROUTES ───────────────────────────────────────────────────

@app.get("/posts")
def get_posts():
    try:
        conn   = get_db()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT id, tag, title, excerpt, read_time, created_at "
            "FROM posts ORDER BY created_at DESC"
        )
        return {"posts": cursor.fetchall()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close(); conn.close()


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    try:
        conn   = get_db()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close(); conn.close()


@app.post("/posts")
def create_post(post: PostIn):
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (tag, title, excerpt, body, read_time) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (post.tag, post.title, post.excerpt, post.body, post.read_time)
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        return {"status": "created", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close(); conn.close()


@app.put("/posts/{post_id}")
def update_post(post_id: int, post: PostIn):
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE posts SET tag=%s, title=%s, excerpt=%s, body=%s, read_time=%s "
            "WHERE id=%s",
            (post.tag, post.title, post.excerpt, post.body, post.read_time, post_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close(); conn.close()


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close(); conn.close()


@app.post("/contact")
def submit_contact(
    name:    str = Form(...),
    email:   str = Form(...),
    message: str = Form(...)
):
    name = name.strip(); email = email.strip(); message = message.strip()
    if not name or not email or not message:
        raise HTTPException(status_code=400, detail="All fields are required.")
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email address.")
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
            (name, email, message)
        )
        conn.commit()
        return {"status": "success", "message": "Message received!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close(); conn.close()
