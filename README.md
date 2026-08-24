# Task API — SQLite Edition (W3 · A1)

A simple CRUD (Create, Read, Update, Delete) API for managing tasks, built with
**Python + Flask**, now backed by a real **SQLite** database instead of an
in-memory array. This means your tasks survive server restarts.

## Why SQLite?

SQLite was chosen because it requires **no separate database server** — it's a
single file (`tasks.db`) that lives right in the project folder. This makes it
perfect for learning and small projects: no installation, no configuration,
no background service to start. Python's built-in `sqlite3` module talks to it
directly, so there are zero extra dependencies beyond Flask itself.

## Where the database lives

The database file is created automatically the first time you run the app:

```
task-api/
├── app.py
├── requirements.txt
├── tasks.db      <- created automatically on first run
└── README.md
```

It contains a single table, `tasks`, with columns `id`, `title`, and `done`.

## How to run the project

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Start the server:
   ```
   python app.py
   ```
3. On first run, the app automatically:
   - creates `tasks.db` if it doesn't exist
   - creates the `tasks` table if it doesn't exist
   - inserts 3 example tasks (only if the table is empty)
4. Visit `http://127.0.0.1:5000/tasks` in your browser to see the tasks.

Restarting the server does **not** reset your data — only the very first run
seeds the 3 example tasks.

## API Endpoints

| Method | Endpoint          | Description                     |
|--------|-------------------|----------------------------------|
| GET    | `/tasks`          | List all tasks                  |
| GET    | `/tasks/<id>`     | Get a single task               |
| POST   | `/tasks`          | Create a new task               |
| PUT    | `/tasks/<id>`     | Update an existing task         |
| DELETE | `/tasks/<id>`     | Delete a task                   |
| GET    | `/stats`          | Task counts (total/done/not done) |

Optional query params on `GET /tasks`:
- `?search=milk` — search tasks by title (SQL `LIKE`)
- `?done=true` — filter by completion status

## Example SQL query

Opened in [DB Browser for SQLite](https://sqlitebrowser.org/), this query
lists every completed task directly from the database:

```sql
SELECT * FROM tasks WHERE done = 1;
```



## What changed from Assignment 1

Only the storage layer. The API's URLs, request bodies, and response formats
are all identical to the in-memory version — proving that persistence is an
implementation detail behind the API, not a change to the API's contract.
