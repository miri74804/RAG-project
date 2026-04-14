# Warnings & Notes למפתחים

## ⚠️ רכיבים רגישים

### 1. SQLite ו-concurrent writes
- `better-sqlite3` הוא **synchronous** — כל ה-queries חוסמות את ה-event loop.
- מתאים לפרויקט זה (single-user, low traffic). לפרודקשן עם עומס — עבור ל-PostgreSQL.

### 2. `updated_at` trigger
- מתבצע ב-SQLite trigger, לא בקוד Node — אל תנסה לעדכן ידנית בקוד.

### 3. Vite Proxy
- ה-proxy מוגדר ב-`vite.config.js` לנתב `/api/*` → `localhost:3001`.
- בפרודקשן חייבים להגדיר reverse proxy (nginx/caddy) או לשנות את כתובת ה-API.

### 4. React StrictMode
- הפרויקט רץ עם `StrictMode` — useEffect מופעל **פעמיים** ב-development.
- אל תסתמך על "רק פעם אחת" ב-useEffect בלי cleanup function.

### 5. CORS
- השרת מגדיר CORS ל-`http://localhost:5173` בלבד.
- לשינוי ה-port (למשל ב-CI) — עדכן `CORS_ORIGIN` ב-`server/src/index.js`.

---

## 📝 מגבלות טכניות

| מגבלה | פתרון מומלץ |
|-------|------------|
| אין אימות משתמשים | הוסף JWT + middleware |
| אין pagination | הוסף `?page=&limit=` ב-GET /api/tasks |
| SQLite לא scalable | מעבר ל-PostgreSQL לפרודקשן |
| אין error boundary ב-React | הוסף ErrorBoundary component |

---

## 🔧 הרצת הפרויקט

```bash
# התקנת dependencies
cd server && npm install
cd ../client && npm install

# הרצה במקביל (מ-root)
cd server && npm run dev &
cd client && npm run dev
```

שרת: http://localhost:3001  
לקוח: http://localhost:5173

---

## 📌 עדכון אחרון
נוצר בתהליך bootstrapping ראשוני. עדכן את הקובץ הזה בכל פעם שמוסיפים feature משמעותי.
