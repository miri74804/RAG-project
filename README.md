# Smart AI Agent: Hybrid RAG & Structured Workflow 🤖

פרויקט זה מציג סוכן בינה מלאכותית (AI Agent) מתקדם שנבנה באמצעות **LlamaIndex Workflows**. הסוכן משלב חיפוש סמנטי ממסמכים (RAG) יחד עם שליפת נתונים מובנית מקבצי JSON, תוך שימוש בניתוב חכם (Routing) המבוסס על כוונת המשתמש.

## 🎯 מטרת הפרויקט
בניית עוזר חכם שמסוגל לענות על שאלות טכניות מורכבות מצד אחד (מתוך מאגר ידע סמנטי), ולספק תשובות מדויקות על חוקים והחלטות עסקיות מצד שני (מתוך מקור נתונים מובנה).

## 🧠 ארכיטקטורת ה-Workflow
הסוכן מנהל את זרימת המידע בצורה מבוזרת (Event-Driven):
- **StartEvent**: קבלת שאילתה מהמשתמש.
- **Route Step**: ניתוח השאילתה בעזרת Cohere LLM ובחירה בנתיב המתאים.
- **Search Steps**: חיפוש ב-Pinecone (Semantic) או שליפה מ-JSON (Structured).
- **Synthesize Step**: בניית תשובה סופית מקצועית המבוססת על ההקשר שנמצא.

### 📊 תרשים זרימה
![Workflow Diagram](workflow_diagram.png)

## ❓ דוגמאות לשאלות שהאגנט יודע לענות
- **שאלת RAG סמנטית:** "איך ה-React SPA משתמש ב-Vite ומה היתרונות שלו?"
- **שאלת JSON מובנית:** "אילו חוקים (rules) הוגדרו במערכת לניהול משימות?"
- **שאלה על אזהרות:** "האם יש אזהרות קריטיות לגבי הסטטוס של המשימות?"

## 🛠️ טכנולוגיות
- **Framework:** LlamaIndex Workflows
- **LLM:** Cohere (Command-R)
- **Vector DB:** Pinecone
- **UI:** Gradio
- **Language:** Python

## 🚀 איך להריץ את הפרויקט
1. בצעו Clone לריפו.
2. התקינו דרישות: `pip install llama-index llama-index-llms-cohere pinecone-client gradio`.
3. הגדירו מפתחות API בקובץ `.env`.
4. הריצו את קובץ ה-Notebook או ה-Python הראשי.

---

## 👩‍💻 Developed By
**מרים כ.**
📩 ליצירת קשר: miri74804@gmail.com

---
