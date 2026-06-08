import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "signals.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find duplicates by title
cursor.execute("SELECT id, title, slug FROM blog_posts ORDER BY id DESC")
rows = cursor.fetchall()

seen_titles = set()
duplicates_to_delete = []

for r in rows:
    post_id, title, slug = r[0], r[1], r[2]
    if title in seen_titles:
        duplicates_to_delete.append(post_id)
    else:
        seen_titles.add(title)

if duplicates_to_delete:
    print(f"Deleting duplicates: {duplicates_to_delete}")
    cursor.execute(f"DELETE FROM blog_posts WHERE id IN ({','.join(map(str, duplicates_to_delete))})")
    conn.commit()
    print("Duplicates removed successfully.")
else:
    print("No duplicates found.")

conn.close()
