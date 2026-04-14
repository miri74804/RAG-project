# Inventory & Logistics — Business Logic

> קובץ זה מתעד את לוגיקת הליבה של מערכת ניהול המלאי. אין קשר לפרויקט ניהול המשימות.

---

## 1. חישובי מלאי

### 1.1 יתרת מלאי זמינה

```
available_stock = physical_stock - reserved_stock - damaged_stock
```

| משתנה             | הגדרה                                              |
|-------------------|----------------------------------------------------|
| `physical_stock`  | כמות פיזית בפועל במחסן                             |
| `reserved_stock`  | כמות שהוקצתה להזמנות פתוחות שטרם נשלחו            |
| `damaged_stock`   | יחידות שסומנו כפגומות וממתינות לסילוק             |
| `available_stock` | הכמות שניתן למכור/להזמין כרגע                      |

### 1.2 ימי מלאי (Days of Stock)

```
days_of_stock = available_stock / avg_daily_demand
```

- `avg_daily_demand` מחושב על חלון של **30 יום אחרונים** (rolling window).
- ערך מתחת ל-`reorder_threshold_days` (ברירת מחדל: 14 יום) מפעיל התראת מחסור.

### 1.3 נקודת הזמנה מחדש (Reorder Point)

```
reorder_point = (avg_daily_demand × lead_time_days) + safety_stock
safety_stock  = Z × σ_demand × √lead_time_days
```

- `Z` = מקדם רמת שירות (Z=1.65 עבור 95%, Z=2.33 עבור 99%).
- `σ_demand` = סטיית תקן ביקוש יומי (30 יום אחרונים).
- `lead_time_days` = זמן אספקה ממוצע מהספק הספציפי.

### 1.4 כמות הזמנה כלכלית (EOQ)

```
EOQ = √( (2 × D × S) / H )
```

| משתנה | הגדרה                                |
|-------|--------------------------------------|
| `D`   | ביקוש שנתי (יחידות)                  |
| `S`   | עלות הזמנה קבועה לפעולה (₪)          |
| `H`   | עלות אחזקת יחידה לשנה (₪)            |

---

## 2. התראות על חוסרים

### 2.1 רמות התראה

| רמה        | תנאי                                         | פעולה אוטומטית                          |
|------------|----------------------------------------------|-----------------------------------------|
| `INFO`     | `days_of_stock < 21`                         | לוג בלבד                                |
| `WARNING`  | `days_of_stock < 14`                         | שליחת email למנהל רכש                   |
| `CRITICAL` | `days_of_stock < 7`                          | email + SMS + פתיחת הזמנה דחופה לספק   |
| `STOCKOUT` | `available_stock <= 0`                       | חסימת יצירת הזמנות חדשות לפריט זה      |

### 2.2 מנגנון Alerting

- התראות מחושבות ב-**cron job** כל 6 שעות.
- לכל פריט נשמר `last_alert_level`; התראה חדשה נשלחת רק אם הרמה **השתנתה** (מונע spam).
- תיעוד כל התראה בטבלת `alert_log` לצורכי audit.

### 2.3 Cooldown

- `WARNING` → cooldown 12 שעות לפני שליחה חוזרת.
- `CRITICAL` → cooldown 2 שעות.
- `STOCKOUT` → ללא cooldown; התראה בכל ריצת cron עד לפתרון.

---

## 3. ניהול ספקים

### 3.1 מבנה ספק

```json
{
  "supplier_id": "SUP-00123",
  "name": "אלפא תעשיות בע\"מ",
  "contact_email": "orders@alpha-ind.co.il",
  "lead_time_days": 7,
  "min_order_value": 1500,
  "payment_terms": "NET30",
  "reliability_score": 0.94,
  "active": true
}
```

### 3.2 ציון אמינות ספק (Reliability Score)

```
reliability_score = (on_time_deliveries / total_deliveries) × 0.6
                  + (items_without_defects / total_items) × 0.4
```

- מחושב על **12 החודשים האחרונים**.
- ספק עם `reliability_score < 0.75` מסומן לבדיקה ומנהל רכש מקבל דו"ח שבועי.

### 3.3 בחירת ספק אוטומטית

בעת יצירת הזמנה אוטומטית (CRITICAL alert), המערכת בוחרת ספק לפי:

1. `reliability_score` ≥ 0.80 — תנאי סף.
2. מינימום `lead_time_days`.
3. מינימום מחיר ליחידה לכמות המבוקשת.

אם אין ספק שעומד בתנאי הסף — ההזמנה נדחית לאישור ידני.

### 3.4 הזמנת רכש (Purchase Order)

```
PO מספר  : PO-{YYYY}-{NNNNNN}   (sequential per year)
מצבים    : DRAFT → SENT → CONFIRMED → PARTIAL → RECEIVED → CLOSED
           └─────────────────────────────────────────┘
                          ניתן לביטול עד CONFIRMED
```
