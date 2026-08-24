"""
W3 - A1: Task CRUD API backed by SQLite
----------------------------------------
Same API as Assignment 1 (in-memory version), but now every task
is stored in a SQLite database file called tasks.db, so data
survives server restarts.
"""

from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_FILE = "tasks.db"


# ---------------------------------------------------------
# STAGE 0: Database setup
# ---------------------------------------------------------

def get_db():
    """Open a connection to the SQLite database file."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """
    Create the tasks table if it doesn't exist yet,
    and insert 3 example tasks only if the table is empty.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        example_tasks = [
            ("Buy milk", 0),
            ("Walk the dog", 0),
            ("Finish homework", 1),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            example_tasks
        )
        print("Inserted 3 example tasks (first run).")

    conn.commit()
    conn.close()


def row_to_dict(row):
    """Convert a sqlite3.Row into a plain dict, with done as a bool."""
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


# ---------------------------------------------------------
# STAGE 1: Read
# ---------------------------------------------------------

@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    # ★ optional extra: search
    search = request.args.get("search")
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    # ★ optional extra: filter by done
    done_param = request.args.get("done")
    if done_param is not None:
        query += " AND done = ?"
        params.append(1 if done_param.lower() == "true" else 0)

    query += " ORDER BY id"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    tasks = [row_to_dict(r) for r in rows]
    return jsonify(tasks), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(row_to_dict(row)), 200


# ---------------------------------------------------------
# STAGE 2: Create
# ---------------------------------------------------------

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if not title or not isinstance(title, str) or title.strip() == "":
        return jsonify({"error": "Title is required"}), 400

    done = bool(data.get("done", False))

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (title, int(done))
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    new_task = {"id": new_id, "title": title, "done": done}
    return jsonify(new_task), 201


# ---------------------------------------------------------
# STAGE 3: Update and delete
# ---------------------------------------------------------

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()

    if row is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True) or {}
    title = data.get("title", row["title"])
    done = data.get("done", bool(row["done"]))

    if not title or not isinstance(title, str) or title.strip() == "":
        conn.close()
        return jsonify({"error": "Title is required"}), 400

    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (title, int(bool(done)), task_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"id": task_id, "title": title, "done": bool(done)}), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()

    if row is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return "", 204


# ---------------------------------------------------------
# ★ optional extra: stats endpoint
# ---------------------------------------------------------

@app.route("/stats", methods=["GET"])
def stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    done_count = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE done = 1"
    ).fetchone()[0]
    conn.close()

    return jsonify({
        "total": total,
        "done": done_count,
        "not_done": total - done_count
    }), 200


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    init_db()
    print(f"Database ready at: {os.path.abspath(DB_FILE)}")
    app.run(debug=True, port=5000)
