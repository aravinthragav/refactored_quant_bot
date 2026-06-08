import sqlite3
import os
import datetime as dt

# Try importing pymysql for MySQL support
try:
    import pymysql
    MYSQL_SUPPORT = True
except ImportError:
    MYSQL_SUPPORT = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "signals.db")

def get_connection():
    # Check if MySQL config is set in environment
    mysql_host = os.environ.get("MYSQL_HOST")
    if mysql_host and MYSQL_SUPPORT:
        return pymysql.connect(
            host=mysql_host,
            user=os.environ.get("MYSQL_USER"),
            password=os.environ.get("MYSQL_PASSWORD"),
            database=os.environ.get("MYSQL_DB"),
            port=int(os.environ.get("MYSQL_PORT", 3306)),
            autocommit=True
        )
    else:
        # Fallback to local SQLite
        conn = sqlite3.connect(DB_FILE)
        return conn

def init_blog_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # SQLite vs MySQL text/id types
    is_mysql = not isinstance(conn, sqlite3.Connection)
    
    if is_mysql:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                created_at VARCHAR(100),
                title VARCHAR(255),
                slug VARCHAR(255) UNIQUE,
                content TEXT,
                summary TEXT,
                author VARCHAR(100),
                status VARCHAR(50) DEFAULT 'PUBLISHED'
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                title TEXT,
                slug TEXT UNIQUE,
                content TEXT,
                summary TEXT,
                author TEXT,
                status TEXT DEFAULT 'PUBLISHED'
            )
        """)
    conn.commit()
    conn.close()

def save_blog_post(title, slug, content, summary, author="AI Gold Forecast Team"):
    init_blog_db()
    conn = get_connection()
    cursor = conn.cursor()
    created_at = dt.datetime.now(dt.timezone.utc).isoformat()
    
    last_id = None
    try:
        # Try SQLite query placeholder
        cursor.execute("""
            INSERT INTO blog_posts (created_at, title, slug, content, summary, author, status)
            VALUES (?, ?, ?, ?, ?, ?, 'PUBLISHED')
        """, (created_at, title, slug, content, summary, author))
        last_id = cursor.lastrowid
    except Exception as e:
        # For MySQL placeholder format (which is %s)
        if "sqlite3" not in str(type(e)):
            cursor.execute("""
                INSERT INTO blog_posts (created_at, title, slug, content, summary, author, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'PUBLISHED')
            """, (created_at, title, slug, content, summary, author))
            last_id = cursor.lastrowid
        else:
            raise e
            
    conn.commit()
    conn.close()
    return last_id

def get_all_posts():
    init_blog_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, created_at, title, slug, summary, author, status 
        FROM blog_posts 
        WHERE status = 'PUBLISHED'
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    posts = []
    for r in rows:
        posts.append({
            "id": r[0],
            "created_at": r[1],
            "title": r[2],
            "slug": r[3],
            "summary": r[4],
            "author": r[5],
            "status": r[6]
        })
    return posts

def get_post_by_slug(slug):
    init_blog_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Try SQLite query placeholder
        cursor.execute("""
            SELECT id, created_at, title, slug, content, summary, author, status 
            FROM blog_posts 
            WHERE slug = ? AND status = 'PUBLISHED'
        """, (slug,))
    except Exception as e:
        # For MySQL placeholder format (which is %s)
        if "sqlite3" not in str(type(e)):
            cursor.execute("""
                SELECT id, created_at, title, slug, content, summary, author, status 
                FROM blog_posts 
                WHERE slug = %s AND status = 'PUBLISHED'
            """, (slug,))
        else:
            raise e
            
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "created_at": row[1],
            "title": row[2],
            "slug": row[3],
            "content": row[4],
            "summary": row[5],
            "author": row[6],
            "status": row[7]
        }
    return None
