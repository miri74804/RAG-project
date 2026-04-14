# Inventory & Logistics API — v1 Reference

**Base URL:** `https://api.inventory.example.com/v1`  
**Auth:** Bearer token (JWT, RS256). כל endpoint דורש `Authorization: Bearer <token>`.  
**Format:** JSON בלבד. `Content-Type: application/json` חובה ב-POST/PUT/PATCH.  
**Versioning:** ה-URL כולל `/v1/`; גרסאות ישנות נתמכות 6 חודשים לאחר פרסום גרסה חדשה.

---

## Items — פריטי מלאי

### `GET /items`

מחזיר רשימה מדורגת של פריטי מלאי.

**Query Parameters**

| פרמטר         | סוג     | ברירת מחדל | תיאור                                      |
|---------------|---------|------------|--------------------------------------------|
| `page`        | integer | `1`        | מספר עמוד                                   |
| `limit`       | integer | `50`       | פריטים לעמוד (מקסימום: 200)                 |
| `category`    | string  | —          | סינון לפי קטגוריה (`electronics`, `raw_material`, …) |
| `alert_level` | string  | —          | סינון: `warning`, `critical`, `stockout`  |
| `supplier_id` | string  | —          | סינון לפי ספק                              |

**Response 200**

```json
{
  "data": [
    {
      "item_id": "ITM-00456",
      "sku": "XB-9900-BLK",
      "name": "כבל USB-C 2m שחור",
      "category": "electronics",
      "unit": "pcs",
      "physical_stock": 340,
      "reserved_stock": 45,
      "damaged_stock": 3,
      "available_stock": 292,
      "reorder_point": 120,
      "eoq": 200,
      "days_of_stock": 18.5,
      "alert_level": "info",
      "primary_supplier_id": "SUP-00123",
      "updated_at": "2026-03-12T10:45:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 50,
    "total": 1240
  }
}
```

---

### `GET /items/{item_id}`

מחזיר פרט מלא עבור פריט בודד, כולל היסטוריית תנועות.

**Path Parameters:** `item_id` — מזהה פריט (פורמט `ITM-{5 ספרות}`).

**Response 200** — זהה לאובייקט בתוך `data` לעיל, בתוספת:

```json
{
  "movements": [
    {
      "movement_id": "MVT-20260312-001",
      "type": "inbound",
      "quantity": 200,
      "reference": "PO-2026-000088",
      "created_at": "2026-03-10T08:00:00Z"
    }
  ]
}
```

**Errors**

| קוד | מצב                        |
|-----|----------------------------|
| 404 | פריט לא נמצא               |
| 403 | אין הרשאה לצפות בפריט זה   |

---

### `POST /items`

יצירת פריט מלאי חדש.

**Request Body**

```json
{
  "sku": "XB-9901-WHT",
  "name": "כבל USB-C 2m לבן",
  "category": "electronics",
  "unit": "pcs",
  "reorder_point": 100,
  "safety_stock": 50,
  "primary_supplier_id": "SUP-00123"
}
```

**שדות חובה:** `sku`, `name`, `category`, `unit`, `primary_supplier_id`.

**Response 201** — האובייקט המלא שנוצר.

**Errors**

| קוד | מצב                        |
|-----|----------------------------|
| 400 | שדה חובה חסר / SKU לא תקין |
| 409 | SKU כבר קיים במערכת         |

---

### `PATCH /items/{item_id}/stock`

עדכון כמויות מלאי (inbound/outbound/adjustment).

```json
{
  "type": "adjustment",
  "quantity": -5,
  "reason": "damaged_on_inspection",
  "reference": "QC-2026-0234"
}
```

| `type`       | תיאור                                          |
|--------------|------------------------------------------------|
| `inbound`    | קבלת סחורה ממחסן/ספק (quantity חיובי)          |
| `outbound`   | שליחה ללקוח / העברה (quantity שלילי)           |
| `adjustment` | תיקון ידני (חיובי או שלילי) — מחייב `reason`  |

**Response 200**

```json
{
  "item_id": "ITM-00456",
  "available_stock": 287,
  "movement_id": "MVT-20260312-002"
}
```

---

## Orders — הזמנות לקוחות

### `GET /orders`

**Query Parameters:** `status`, `customer_id`, `from_date`, `to_date`, `page`, `limit`.

**Response 200**

```json
{
  "data": [
    {
      "order_id": "ORD-2026-004521",
      "customer_id": "CUST-0099",
      "status": "processing",
      "lines": [
        { "item_id": "ITM-00456", "qty_ordered": 10, "qty_fulfilled": 0 }
      ],
      "created_at": "2026-03-11T14:30:00Z",
      "estimated_ship_date": "2026-03-14T00:00:00Z"
    }
  ],
  "meta": { "page": 1, "limit": 50, "total": 892 }
}
```

---

### `POST /orders`

יצירת הזמנת לקוח חדשה. המערכת מבצעת אוטומטית `reservation` על המלאי הזמין.

```json
{
  "customer_id": "CUST-0099",
  "lines": [
    { "item_id": "ITM-00456", "qty": 10 },
    { "item_id": "ITM-00789", "qty": 2 }
  ],
  "requested_ship_date": "2026-03-20"
}
```

**Response 201**

```json
{
  "order_id": "ORD-2026-004522",
  "status": "confirmed",
  "reservation_ids": ["RES-00112", "RES-00113"]
}
```

**Errors**

| קוד | מצב                                              |
|-----|--------------------------------------------------|
| 422 | `available_stock` אפסי לאחד הפריטים              |
| 400 | `customer_id` לא קיים / שדה חסר                 |

---

### `POST /orders/{order_id}/ship`

סימון הזמנה כשולחת. משחרר `reserved_stock` ומפחית `physical_stock`.

**Response 200**

```json
{
  "order_id": "ORD-2026-004521",
  "status": "shipped",
  "shipped_at": "2026-03-12T11:00:00Z",
  "tracking_number": "IL123456789"
}
```

---

## Purchase Orders — הזמנות רכש

### `GET /purchase-orders`

רשימת הזמנות רכש מספקים.

**Query Parameters:** `status`, `supplier_id`, `from_date`, `to_date`.

---

### `POST /purchase-orders`

יצירת הזמנת רכש לספק.

```json
{
  "supplier_id": "SUP-00123",
  "lines": [
    { "item_id": "ITM-00456", "qty": 200, "unit_price": 12.50 }
  ],
  "notes": "דחוף — מלאי נמוך"
}
```

**Response 201**

```json
{
  "po_id": "PO-2026-000089",
  "status": "draft",
  "total_value": 2500.00,
  "estimated_delivery": "2026-03-19"
}
```

---

## Suppliers — ספקים

### `GET /suppliers`

רשימת ספקים פעילים.

### `GET /suppliers/{supplier_id}/performance`

דו"ח ביצועי ספק.

**Response 200**

```json
{
  "supplier_id": "SUP-00123",
  "period": "last_12_months",
  "total_orders": 48,
  "on_time_rate": 0.94,
  "defect_rate": 0.02,
  "reliability_score": 0.94,
  "avg_lead_time_days": 6.8
}
```

---

## Alerts — התראות מלאי

### `GET /alerts`

**Query Parameters:** `level` (`info`/`warning`/`critical`/`stockout`), `resolved`.

**Response 200**

```json
{
  "data": [
    {
      "alert_id": "ALT-00881",
      "item_id": "ITM-00789",
      "level": "critical",
      "days_of_stock": 4.2,
      "message": "מלאי צפוי להאפס תוך 5 ימים",
      "created_at": "2026-03-12T06:00:00Z",
      "resolved": false
    }
  ]
}
```

---

## קודי שגיאה גלובליים

| קוד | משמעות                                         |
|-----|------------------------------------------------|
| 400 | Bad Request — שגיאת validation בגוף הבקשה      |
| 401 | Unauthorized — token חסר או פג תוקף           |
| 403 | Forbidden — אין הרשאה לפעולה זו               |
| 404 | Not Found — משאב לא נמצא                       |
| 409 | Conflict — כפילות (לדוג', SKU קיים)            |
| 422 | Unprocessable — לוגיקה עסקית נכשלה            |
| 429 | Too Many Requests — rate limit: 300 req/min   |
| 500 | Internal Server Error — שגיאת שרת             |

**Error envelope:**

```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "available_stock for ITM-00789 is 0",
    "request_id": "req_a8f3bc21"
  }
}
```
