# אלגוריתם זימון תורים

## סקירה כללית

מערכת זימון התורים מבוססת על אלגוריתם אופטימיזציה מתקדם המשלב מספר פרמטרים: זמינות רופאים, העדפות מטופלים, דחיפות רפואית, ומניעת כפילויות. המערכת מיועדת לניצול מיטבי של משאבי המרפאה תוך מתן שירות איכותי למטופלים.

## ארכיטקטורת המערכת

### רכיבים עיקריים

```
┌─────────────────────────────────────────┐
│     Scheduling Engine Core              │
├─────────────────────────────────────────┤
│  - Availability Manager                 │
│  - Conflict Detector                    │
│  - Optimization Algorithm               │
│  - Priority Queue Handler               │
└─────────────────────────────────────────┘
         ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Calendar    │ │  Constraint  │ │  Notification│
│  Service     │ │  Validator   │ │  Service     │
└──────────────┘ └──────────────┘ └──────────────┘
```

## מודל נתונים

### ישויות מרכזיות

#### Appointment (תור)
```typescript
interface Appointment {
  id: string;
  patientId: string;
  providerId: string;
  appointmentType: AppointmentType;
  scheduledStart: DateTime;
  scheduledEnd: DateTime;
  duration: number; // minutes
  status: AppointmentStatus;
  priority: PriorityLevel;
  room: string;
  notes: string;
  createdAt: DateTime;
  updatedAt: DateTime;
}
```

#### Provider Schedule (לוח זמנים של רופא)
```typescript
interface ProviderSchedule {
  providerId: string;
  dayOfWeek: number; // 0-6
  workingHours: TimeSlot[];
  breaks: TimeSlot[];
  maxAppointmentsPerDay: number;
  appointmentTypes: string[];
  effectiveFrom: Date;
  effectiveTo: Date;
}
```


#### Time Slot (חלון זמן)
```typescript
interface TimeSlot {
  start: Time; // HH:MM
  end: Time;   // HH:MM
}

interface AvailableSlot extends TimeSlot {
  providerId: string;
  date: Date;
  isAvailable: boolean;
  conflictReason?: string;
}
```

## אלגוריתם זימון תורים

### שלב 1: בדיקת זמינות (Availability Check)

#### תהליך בדיקה

```typescript
function checkAvailability(
  providerId: string,
  requestedDate: Date,
  duration: number
): AvailableSlot[] {
  
  // 1. טעינת לוח זמנים של הרופא
  const schedule = getProviderSchedule(providerId, requestedDate);
  
  // 2. טעינת תורים קיימים
  const existingAppointments = getAppointments(providerId, requestedDate);
  
  // 3. חישוב חלונות זמן פנויים
  const availableSlots = calculateFreeSlots(
    schedule.workingHours,
    schedule.breaks,
    existingAppointments,
    duration
  );
  
  // 4. סינון לפי אילוצים
  return filterByConstraints(availableSlots, {
    minBufferTime: 5, // דקות בין תורים
    maxDailyAppointments: schedule.maxAppointmentsPerDay,
    appointmentType: requestedType
  });
}
```

#### אילוצי זמן

- **Buffer Time**: 5 דקות מינימום בין תורים (לניקוי חדר, תיעוד)
- **Lunch Break**: חסימה אוטומטית של 30-60 דקות
- **End of Day Buffer**: 15 דקות לפני סיום יום עבודה
- **Minimum Slot Duration**: 15 דקות (ניתן להגדרה)

### שלב 2: מניעת כפילויות (Conflict Detection)

#### סוגי קונפליקטים


**1. Time Overlap (חפיפת זמנים)**
```typescript
function detectTimeOverlap(
  newAppointment: Appointment,
  existingAppointments: Appointment[]
): boolean {
  return existingAppointments.some(existing => {
    const newStart = newAppointment.scheduledStart;
    const newEnd = newAppointment.scheduledEnd;
    const existingStart = existing.scheduledStart;
    const existingEnd = existing.scheduledEnd;
    
    // בדיקת חפיפה
    return (newStart < existingEnd && newEnd > existingStart);
  });
}
```

**2. Double Booking (זימון כפול למטופל)**
```typescript
function detectDoubleBooking(
  patientId: string,
  requestedDateTime: DateTime
): Conflict | null {
  const patientAppointments = getPatientAppointments(
    patientId,
    requestedDateTime.date
  );
  
  // מטופל לא יכול להיות בשני מקומות בו זמנית
  const conflict = patientAppointments.find(apt => 
    isTimeOverlapping(apt, requestedDateTime)
  );
  
  return conflict ? {
    type: 'DOUBLE_BOOKING',
    message: 'למטופל כבר קיים תור באותו זמן',
    conflictingAppointment: conflict
  } : null;
}
```

**3. Resource Conflicts (קונפליקטים במשאבים)**
```typescript
function detectResourceConflict(
  room: string,
  equipment: string[],
  requestedTime: TimeSlot
): boolean {
  // בדיקת זמינות חדר
  const roomAvailable = isRoomAvailable(room, requestedTime);
  
  // בדיקת זמינות ציוד
  const equipmentAvailable = equipment.every(item =>
    isEquipmentAvailable(item, requestedTime)
  );
  
  return roomAvailable && equipmentAvailable;
}
```

**4. Provider Constraints (אילוצי רופא)**
- מקסימום תורים ביום
- סוגי טיפולים מורשים
- הפסקות חובה
- זמני נסיעה בין מתקנים

### שלב 3: אופטימיזציה (Optimization)

#### מטרות אופטימיזציה

המערכת מבצעת אופטימיזציה רב-מטרתית:

1. **מקסום ניצול זמן**: מילוי מקסימלי של לוח הזמנים
2. **מזעור זמני המתנה**: הקטנת פערים בין תורים
3. **איזון עומסים**: חלוקה שווה של תורים לאורך היום
4. **עדיפות לדחיפות**: תעדוף מקרים דחופים

#### אלגוריתם תעדוף

```typescript
enum PriorityLevel {
  EMERGENCY = 1,    // חירום - תוך שעה
  URGENT = 2,       // דחוף - תוך 24 שעות
  ROUTINE = 3,      // רגיל - תוך שבוע
  FOLLOW_UP = 4     // מעקב - גמיש
}

function calculatePriority(
  appointmentType: string,
  patientHistory: PatientHistory,
  requestedDate: Date
): number {
  let score = 0;
  
  // משקל לפי סוג תור
  const typeWeight = {
    'emergency': 100,
    'urgent_care': 80,
    'new_patient': 60,
    'follow_up': 40,
    'routine_checkup': 20
  };
  score += typeWeight[appointmentType] || 0;
  
  // משקל לפי היסטוריה
  if (patientHistory.missedAppointments > 2) {
    score -= 10; // הורדת עדיפות למטופלים שמפספסים תורים
  }
  
  if (patientHistory.chronicCondition) {
    score += 15; // העלאת עדיפות למטופלים כרוניים
  }
  
  // משקל לפי זמן המתנה
  const waitingDays = daysBetween(new Date(), requestedDate);
  if (waitingDays > 14) {
    score += waitingDays * 2; // העלאת עדיפות ככל שהמתנה ארוכה יותר
  }
  
  return score;
}
```

#### אלגוריתם Bin Packing

לאופטימיזציה של מילוי לוח הזמנים:

```typescript
function optimizeSchedule(
  availableSlots: TimeSlot[],
  pendingAppointments: Appointment[]
): ScheduleOptimization {
  
  // מיון תורים לפי עדיפות ומשך
  const sorted = pendingAppointments.sort((a, b) => {
    if (a.priority !== b.priority) {
      return a.priority - b.priority;
    }
    return b.duration - a.duration; // ארוכים קודם
  });
  
  const assignments: AppointmentAssignment[] = [];
  
  for (const appointment of sorted) {
    // חיפוש החלון המתאים ביותר
    const bestSlot = findBestFitSlot(
      availableSlots,
      appointment.duration,
      appointment.preferredTimes
    );
    
    if (bestSlot) {
      assignments.push({
        appointment,
        slot: bestSlot
      });
      
      // עדכון זמינות
      removeSlot(availableSlots, bestSlot);
    }
  }
  
  return {
    assignments,
    utilizationRate: calculateUtilization(assignments),
    unscheduled: sorted.length - assignments.length
  };
}
```

### שלב 4: ניהול יומן רופאים

#### מבנה יומן

```typescript
interface DoctorCalendar {
  providerId: string;
  date: Date;
  slots: CalendarSlot[];
  statistics: DayStatistics;
}

interface CalendarSlot {
  time: TimeSlot;
  status: 'available' | 'booked' | 'blocked' | 'break';
  appointment?: Appointment;
  blockReason?: string;
}

interface DayStatistics {
  totalSlots: number;
  bookedSlots: number;
  availableSlots: number;
  utilizationRate: number;
  averageWaitTime: number;
}
```

#### עדכון דינמי

המערכת מעדכנת את היומן בזמן אמת:

```typescript
class CalendarManager {
  
  // עדכון בזמן אמת דרך WebSocket
  async updateCalendar(
    providerId: string,
    date: Date,
    change: CalendarChange
  ): Promise<void> {
    
    // נעילה אופטימיסטית למניעת race conditions
    const lock = await acquireLock(`calendar:${providerId}:${date}`);
    
    try {
      // ביצוע השינוי
      await applyChange(change);
      
      // שידור לכל המשתמשים המחוברים
      this.broadcastUpdate(providerId, date, change);
      
      // עדכון cache
      await this.updateCache(providerId, date);
      
    } finally {
      await lock.release();
    }
  }
  
  // מניעת overbooking
  async bookSlot(
    providerId: string,
    slot: TimeSlot,
    appointment: Appointment
  ): Promise<BookingResult> {
    
    // בדיקה אטומית של זמינות וזימון
    const result = await this.db.transaction(async (trx) => {
      
      // בדיקת זמינות עם נעילה
      const isAvailable = await trx('appointments')
        .where({ providerId, date: slot.start.date })
        .whereBetween('scheduled_start', [slot.start, slot.end])
        .forUpdate() // row-level lock
        .then(rows => rows.length === 0);
      
      if (!isAvailable) {
        throw new ConflictError('Slot no longer available');
      }
      
      // יצירת התור
      return await trx('appointments').insert(appointment);
    });
    
    return result;
  }
}
```

### שלב 5: תזמון אוטומטי (Auto-Scheduling)

#### אלגוריתם Greedy

למקרים פשוטים:

```typescript
function autoScheduleGreedy(
  appointment: Appointment,
  providers: Provider[]
): ScheduleResult {
  
  // מיון רופאים לפי התאמה
  const rankedProviders = rankProviders(
    providers,
    appointment.specialty,
    appointment.patientPreferences
  );
  
  for (const provider of rankedProviders) {
    const slots = getAvailableSlots(
      provider.id,
      appointment.preferredDates,
      appointment.duration
    );
    
    if (slots.length > 0) {
      // בחירת החלון הראשון הזמין
      return {
        success: true,
        provider: provider,
        slot: slots[0]
      };
    }
  }
  
  return { success: false, reason: 'No available slots' };
}
```

#### אלגוריתם Constraint Satisfaction Problem (CSP)

למקרים מורכבים:

```typescript
function autoScheduleCSP(
  appointments: Appointment[],
  constraints: Constraint[]
): ScheduleResult[] {
  
  // הגדרת משתנים
  const variables = appointments.map(apt => ({
    id: apt.id,
    domain: getAllPossibleSlots(apt)
  }));
  
  // הגדרת אילוצים
  const csp = new CSP(variables, constraints);
  
  // פתרון באמצעות Backtracking + Forward Checking
  const solution = csp.solve({
    algorithm: 'backtracking',
    heuristic: 'minimum-remaining-values',
    inference: 'forward-checking'
  });
  
  return solution;
}
```

### שלב 6: טיפול בביטולים ושינויים

#### מדיניות ביטול

```typescript
interface CancellationPolicy {
  minNoticeHours: number;      // הודעה מוקדמת מינימלית
  penaltyThreshold: number;     // מספר ביטולים לפני קנס
  autoReleaseMinutes: number;   // שחרור אוטומטי אם לא הגיע
}

async function cancelAppointment(
  appointmentId: string,
  reason: string,
  cancelledBy: string
): Promise<CancellationResult> {
  
  const appointment = await getAppointment(appointmentId);
  const policy = getCancellationPolicy(appointment.type);
  
  // בדיקת זמן הודעה
  const hoursUntilAppointment = hoursBetween(
    new Date(),
    appointment.scheduledStart
  );
  
  if (hoursUntilAppointment < policy.minNoticeHours) {
    // ביטול מאוחר - רישום לסטטיסטיקה
    await recordLateCancel(appointment.patientId);
  }
  
  // ביטול התור
  await updateAppointmentStatus(appointmentId, 'cancelled', reason);
  
  // שחרור החלון
  const slot = {
    start: appointment.scheduledStart,
    end: appointment.scheduledEnd
  };
  await releaseSlot(appointment.providerId, slot);
  
  // ניסיון למלא מרשימת המתנה
  await tryFillFromWaitlist(appointment.providerId, slot);
  
  // שליחת התראות
  await notifyStaff(appointment, 'cancelled');
  
  return { success: true, slotReleased: true };
}
```

#### רשימת המתנה (Waitlist)

```typescript
class WaitlistManager {
  
  async addToWaitlist(
    patientId: string,
    preferences: AppointmentPreferences
  ): Promise<WaitlistEntry> {
    
    const entry: WaitlistEntry = {
      id: generateId(),
      patientId,
      preferences,
      addedAt: new Date(),
      priority: calculatePriority(preferences),
      notificationsSent: 0
    };
    
    await this.db('waitlist').insert(entry);
    
    // ניסיון מיידי למצוא חלון
    await this.tryMatchSlot(entry);
    
    return entry;
  }
  
  async onSlotAvailable(
    providerId: string,
    slot: TimeSlot
  ): Promise<void> {
    
    // חיפוש מתאימים ברשימת המתנה
    const matches = await this.db('waitlist')
      .where('providerId', providerId)
      .where('preferredStart', '<=', slot.start)
      .where('preferredEnd', '>=', slot.end)
      .orderBy('priority', 'desc')
      .orderBy('addedAt', 'asc')
      .limit(5);
    
    // שליחת התראות
    for (const match of matches) {
      await this.sendNotification(match, slot, {
        expiresIn: 30 // דקות
      });
    }
  }
}
```

### שלב 7: אופטימיזציה מתמשכת

#### למידת מכונה (Machine Learning)

המערכת לומדת מהתנהגות עבר:

```typescript
interface MLModel {
  predictNoShow(appointment: Appointment): number;
  predictDuration(appointmentType: string): number;
  suggestOptimalSlots(patient: Patient): TimeSlot[];
}

class SchedulingML {
  
  // חיזוי אי-הגעה
  predictNoShowProbability(
    patientHistory: PatientHistory,
    appointmentDetails: Appointment
  ): number {
    
    const features = {
      previousNoShows: patientHistory.noShowCount,
      dayOfWeek: appointmentDetails.scheduledStart.getDay(),
      timeOfDay: appointmentDetails.scheduledStart.getHours(),
      leadTime: daysBetween(new Date(), appointmentDetails.scheduledStart),
      appointmentType: appointmentDetails.type,
      weatherForecast: getWeatherScore(appointmentDetails.scheduledStart)
    };
    
    return this.model.predict(features);
  }
  
  // אופטימיזציה של overbooking
  calculateOverbookingFactor(
    providerId: string,
    date: Date
  ): number {
    
    const historicalNoShowRate = this.getNoShowRate(providerId, date);
    const dayOfWeek = date.getDay();
    
    // ימי שני יש יותר אי-הגעות
    const dayFactor = dayOfWeek === 1 ? 1.2 : 1.0;
    
    return historicalNoShowRate * dayFactor;
  }
}
```

#### אנליטיקה ודיווח

```typescript
interface SchedulingAnalytics {
  utilizationRate: number;        // אחוז ניצול
  averageWaitTime: number;        // זמן המתנה ממוצע
  noShowRate: number;             // אחוז אי-הגעות
  cancellationRate: number;       // אחוז ביטולים
  patientSatisfaction: number;    // שביעות רצון
  revenuePerSlot: number;         // הכנסה לחלון
}

async function generateAnalytics(
  providerId: string,
  dateRange: DateRange
): Promise<SchedulingAnalytics> {
  
  const appointments = await getAppointments(providerId, dateRange);
  
  return {
    utilizationRate: calculateUtilization(appointments),
    averageWaitTime: calculateAverageWait(appointments),
    noShowRate: calculateNoShowRate(appointments),
    cancellationRate: calculateCancellationRate(appointments),
    patientSatisfaction: getAverageSatisfaction(appointments),
    revenuePerSlot: calculateRevenue(appointments) / appointments.length
  };
}
```

## ביצועים ומדרגיות

### אופטימיזציות

#### Caching Strategy

```typescript
// Redis cache לזמינות
const cacheKey = `availability:${providerId}:${date}`;
const ttl = 300; // 5 דקות

// Cache invalidation על שינויים
await redis.setex(cacheKey, ttl, JSON.stringify(slots));
```

#### Database Indexing

```sql
-- אינדקסים קריטיים
CREATE INDEX idx_appointments_provider_date 
  ON appointments(provider_id, scheduled_start);

CREATE INDEX idx_appointments_patient_date 
  ON appointments(patient_id, scheduled_start);

CREATE INDEX idx_provider_schedule_day 
  ON provider_schedules(provider_id, day_of_week);
```

#### Query Optimization

```typescript
// שימוש ב-batch queries
async function getMultipleProviderAvailability(
  providerIds: string[],
  date: Date
): Promise<Map<string, TimeSlot[]>> {
  
  // שאילתה אחת במקום N שאילתות
  const results = await db('provider_schedules')
    .whereIn('provider_id', providerIds)
    .where('date', date)
    .select('*');
  
  return groupBy(results, 'provider_id');
}
```

### מדרגיות (Scalability)

- **Horizontal Scaling**: תמיכה במספר instances של שרת האפליקציה
- **Database Sharding**: חלוקה לפי provider_id או date range
- **Read Replicas**: שאילתות קריאה מ-replicas
- **Event-Driven**: שימוש ב-message queue (RabbitMQ/Kafka) לעדכונים אסינכרוניים

## סיכום

אלגוריתם זימון התורים משלב טכניקות מתקדמות מתחום האופטימיזציה, למידת מכונה ומערכות מבוזרות. המערכת מספקת פתרון יעיל למניעת כפילויות, אופטימיזציה של ניצול משאבים, וחוויית משתמש מעולה הן למטופלים והן לצוות הרפואי.
