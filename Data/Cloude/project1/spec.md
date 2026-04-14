# Task Manager — Spec & Architecture

## טכנולוגיות

| שכבה       | טכנולוגיה              |
|------------|------------------------|
| Frontend   | React 18 + Vite        |
| Backend    | Node.js + Express      |
| DB         | SQLite (via better-sqlite3) |
| Styling    | CSS Modules + Custom Properties |
| State      | useState / useEffect   |
| HTTP       | Fetch API (native)     |

---

## מבנה נתונים (DB Schema)

### טבלה: `tasks`

| עמודה        | סוג            | הערות                            |
|-------------|----------------|----------------------------------|
| `id`        | INTEGER PK     | AUTO INCREMENT                   |
| `title`     | TEXT NOT NULL  | כותרת המשימה                    |
| `description` | TEXT         | תיאור אופציונלי                 |
| `status`    | TEXT           | 'todo' / 'in_progress' / 'done' |
| `priority`  | TEXT           | 'low' / 'medium' / 'high'       |
| `created_at` | DATETIME      | ברירת מחדל: NOW()               |
| `updated_at` | DATETIME      | מתעדכן בכל שינוי                |

---

## ארכיטקטורה

```
client/          ← React SPA (Vite dev server :5173)
  src/
    components/  ← TaskCard, TaskForm, TaskBoard, FilterBar
    hooks/       ← useTasks (custom hook לכל לוגיקת API)
    App.jsx
    main.jsx

server/          ← Express REST API (:3001)
  src/
    db.js        ← אתחול SQLite + schema
    routes/
      tasks.js   ← CRUD endpoints
    index.js     ← entry point
```

## REST API Endpoints

| Method | Path              | תיאור              |
|--------|-------------------|--------------------|
| GET    | /api/tasks        | קבלת כל המשימות    |
| GET    | /api/tasks/:id    | משימה בודדת        |
| POST   | /api/tasks        | יצירת משימה חדשה   |
| PUT    | /api/tasks/:id    | עדכון משימה        |
| DELETE | /api/tasks/:id    | מחיקת משימה        |

## החלטות ארכיטקטורה

- **SQLite** נבחר לפשטות — אין צורך ב-Docker או חיבור חיצוני.
- **Vite proxy** מנתב /api/* לשרת Express כדי להימנע מבעיות CORS בפיתוח.
- **RTL-ready** — המערכת מוגדרת עם `dir="rtl"` ו-`lang="he"`.
- Status כ-Kanban columns: todo → in_progress → done.
