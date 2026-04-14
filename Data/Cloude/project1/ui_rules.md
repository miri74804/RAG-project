# UI Rules & Design System

## כיווניות
- **RTL מלא** — `<html dir="rtl" lang="he">`
- כל flexbox/grid תומך בכיווניות עברית
- padding/margin משתמשים ב-`inline-start` / `inline-end` לעקביות

## פלטת צבעים

```css
--bg-base:       #0f0f13;   /* רקע ראשי כהה */
--bg-surface:    #1a1a24;   /* כרטיסים ועמודות */
--bg-elevated:   #252535;   /* hover states */
--accent-primary:#6c63ff;   /* סגול-כחול — CTA ראשי */
--accent-success:#22c55e;   /* done / success */
--accent-warn:   #f59e0b;   /* in_progress / אזהרה */
--accent-danger: #ef4444;   /* מחיקה / שגיאה */
--text-primary:  #f0f0f5;   /* טקסט ראשי */
--text-secondary:#8b8ba8;   /* מטא-מידע, תאריכים */
--border:        #2e2e42;   /* גבולות עדינים */
```

## טיפוגרפיה
- **Font ראשי**: `'Heebo'` (Google Fonts) — קריא ומשלב RTL/LTR
- **Font משני / mono**: `'JetBrains Mono'` — IDs, תאריכים
- גדלים: base 14px, כותרות 18-24px, meta 12px

## רכיבי Status

| Status       | צבע              | אייקון |
|-------------|------------------|--------|
| todo        | --text-secondary | ○      |
| in_progress | --accent-warn    | ◑      |
| done        | --accent-success | ✓      |

## Priority Badges

| Priority | צבע              |
|---------- |------------------|
| low       | --text-secondary |
| medium    | --accent-warn    |
| high      | --accent-danger  |

## Layout

- **Kanban Board**: 3 עמודות בפריסת grid, scroll אנכי לכל עמודה
- עמודות: min-width 280px, max 360px
- כרטיסי משימה: border-radius 12px, box-shadow עדין
- Form Modal: overlay עם backdrop blur

## אנימציות
- כרטיסים: `transition: transform 0.15s ease, box-shadow 0.15s ease`
- Modal: fade-in + slide-up קל
- Status change: צבע עם `transition: color 0.2s`

## נגישות
- כל כפתורי פעולה עם `aria-label`
- Focus ring גלוי: `outline: 2px solid var(--accent-primary)`
- Contrast ratio עומד ב-WCAG AA
