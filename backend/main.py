
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import psycopg2
import psycopg2.extras
import re, os, sys

# ─── DATABASE CONFIG ───────────────────────────────────────────
# Use DATABASE_URL for Render deployment, fallback to local for development
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"DEBUG: DATABASE_URL is set: {bool(DATABASE_URL)}")
if DATABASE_URL:
    print(f"DEBUG: Using Render database: {DATABASE_URL[:50]}...")
else:
    print("DEBUG: Using local database")

if DATABASE_URL:
    # Render deployment - use connection string
    def get_db():
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as e:
            print(f"ERROR: Failed to connect to database: {e}")
            sys.exit(1)
else:
    # Local development
    DB_CONFIG = {
        "host":     "localhost",
        "port":     5432,
        "dbname":   "blog_db",
        "user":     "postgres",
        "password": "1234567",
    }
    def get_db():
        return psycopg2.connect(**DB_CONFIG)

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

# ─── INITIALIZE TABLES ─────────────────────────────────────────
def init_db():
    """Create tables if they don't exist"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        print("DEBUG: Connected to database successfully")
        print(f"DEBUG: DATABASE_URL being used: {DATABASE_URL[:60]}...")
        
        # Check current number of posts BEFORE creating tables
        cursor.execute("SELECT COUNT(*) FROM posts;")
        count_before = cursor.fetchone()[0]
        print(f"DEBUG: Posts BEFORE init_db: {count_before}")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
              id         SERIAL PRIMARY KEY,
              tag        VARCHAR(50)  NOT NULL,
              title      VARCHAR(255) NOT NULL,
              excerpt    TEXT         NOT NULL,
              body       TEXT         NOT NULL,
              read_time  VARCHAR(20)  DEFAULT '3 min read',
              created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS contacts (
              id           SERIAL PRIMARY KEY,
              name         VARCHAR(100) NOT NULL,
              email        VARCHAR(150) NOT NULL,
              message      TEXT         NOT NULL,
              submitted_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        
        # Check after creating tables
        cursor.execute("SELECT COUNT(*) FROM posts;")
        count_after = cursor.fetchone()[0]
        print(f"✓ Database tables initialized - {count_after} posts in database")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Database init error: {e}")

# Initialize tables on startup
init_db()

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
        posts = cursor.fetchall()
        print(f"DEBUG: GET /posts returning {len(posts)} posts from database")
        return {"posts": posts}
    except Exception as e:
        print(f"ERROR in GET /posts: {e}")
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
    conn = None
    try:
        conn   = get_db()
        cursor = conn.cursor()
        print(f"DEBUG: Creating post - tag:{post.tag}, title:{post.title}")
        
        cursor.execute(
            "INSERT INTO posts (tag, title, excerpt, body, read_time) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (post.tag, post.title, post.excerpt, post.body, post.read_time)
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
        print(f"DEBUG: Post created with ID: {new_id} - committed to database")
        
        # Verify it was saved
        cursor.execute("SELECT COUNT(*) FROM posts;")
        count = cursor.fetchone()[0]
        print(f"DEBUG: Total posts in database now: {count}")
        
        return {"status": "created", "id": new_id}
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"ERROR: Failed to create post: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            cursor.close()
            conn.close()


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
