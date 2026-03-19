# backend/main.py
# Run: python -m uvicorn main:app --reload
# Open: http://localhost:8000

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

# Serve frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# ─── DATABASE CONFIG ───────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "blog_db",
    "user":     "postgres",
    "password": "1234567",   # change if you set a different password
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

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

# GET /posts
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


# GET /posts/{id}
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


# POST /posts
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


# PUT /posts/{id}
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


# DELETE /posts/{id}
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


# POST /contact
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
