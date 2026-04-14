# Smart AI Agent: Hybrid RAG & Structured Workflow 🤖

פרויקט זה מציג סוכן בינה מלאכותית (AI Agent) מתקדם שנבנה באמצעות **LlamaIndex Workflows**. הסוכן משלב חיפוש סמנטי ממסמכים (RAG) יחד עם שליפת נתונים מובנית מקבצי JSON, תוך שימוש בניתוב חכם (Routing) המבוסס על כוונת המשתמש.

---

## 📂 מבנה הפרויקט (Project Files)

הפרויקט מורכב משתי סביבות עבודה משלימות:

* **`Smart_AI_Agent_Workflow.ipynb` (Development Notebook):** מחברת הפיתוח המלאה הכוללת את שלבי ה-Data Pipeline: טעינת מסמכים מקוריים, חילוץ מידע מובנה (Extraction), ניקוי נתונים, העלאה ל-Pinecone ובניית ה-Workflow.
* **`app.py` (Production Script):** קובץ הרצה ייעודי המפעיל את האפליקציה הסופית. הקוד טוען את המודלים ואת המאגרים המוכנים ומריץ את ממשק המשתמש (Gradio).
* **`requirements.txt`:** קובץ הגדרות להתקנה מהירה של כל ספריות הפרויקט.
* **`structured_data.json`:** מאגר הנתונים המובנה שחולץ מהמסמכים בתהליך הפיתוח.

---

## 🎯 מטרת הפרויקט
בניית עוזר חכם שמסוגל לענות על שאלות טכניות מורכבות מצד אחד (מתוך מאגר ידע סמנטי), ולספק תשובות מדויקות על חוקים והחלטות עסקיות מצד שני (מתוך מקור נתונים מובנה).

## 🧠 ארכיטקטורת ה-Workflow
הסוכן מנהל את זרימת המידע בצורה מבוזרת (Event-Driven):
- **StartEvent**: קבלת שאילתה מהמשתמש.
- **Router Step**: ניתוח השאילתה בעזרת Cohere LLM ובחירה בנתיב המתאים.
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

### 1. שיכפול הריפוזיטורי
פתחו טרמינל והריצו:

```bash
git clone https://github.com/miri74804
cd RAGPROJECT
```

### 2. התקנת הספריות הנדרשות
פתחו את הטרמינל בתיקיית הפרויקט והריצו את הפקודה הבאה להתקנת כל התשתיות בבת אחת:

```bash
pip install -r requirements.txt
```

### 3. הגדרת מפתחות API
צרו קובץ בשם `.env` בתוך תיקיית `Project`.

הוסיפו לקובץ את המפתחות שלכם בצורה הבאה:

```
COHERE_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
```

### 4. הרצת הסוכן
ניתן להריץ את הפרויקט בשתי דרכים:

* **דרך קובץ ה-Python (מומלץ):** הריצו בטרמינל את הפקודה `python app.py` להפעלת הממשק במהירות.
* **דרך המחברת:** פתחו את `Smart_AI_Agent_Workflow.ipynb` ולחצו על **Run All**. דרך זו מתאימה אם ברצונכם לראות את שלבי עיבוד הנתונים.

לאחר ההרצה, ממשק ה-**Gradio** יפתח ותוכלו להתחיל לשאול שאלות!


<br/>

---

<div align="center">

## 👩‍💻 Developed By
**מרים כ.**

**📩 ליצירת קשר:** [miri74804@gmail.com](mailto:miri74804@gmail.com)

</div>

---