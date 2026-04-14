# דרישות מערכת וסביבת הפעלה

## סקירה כללית

מסמך זה מפרט את דרישות החומרה, התוכנה והתשתית הנדרשות להפעלה מיטבית של מערכת ניהול המרפאה. המערכת מתוכננת כפתרון Cloud-Native עם יכולות גיבוי אוטומטיות ומדרגיות גבוהה.

## דרישות חומרה

### שרת ייצור (Production Server)

#### תצורה מינימלית
- **CPU**: 4 cores (Intel Xeon או AMD EPYC)
- **RAM**: 16 GB
- **Storage**: 500 GB SSD
- **Network**: 1 Gbps
- **Concurrent Users**: עד 50 משתמשים במקביל

#### תצורה מומלצת
- **CPU**: 8+ cores (Intel Xeon Scalable או AMD EPYC)
- **RAM**: 32 GB
- **Storage**: 1 TB NVMe SSD (RAID 10)
- **Network**: 10 Gbps
- **Concurrent Users**: 100-200 משתמשים במקביל

#### תצורה ארגונית (Enterprise)
- **CPU**: 16+ cores
- **RAM**: 64 GB+
- **Storage**: 2 TB+ NVMe SSD (RAID 10)
- **Network**: 10 Gbps redundant
- **Concurrent Users**: 200+ משתמשים במקביל
- **High Availability**: Cluster של 3+ nodes

### תחנות עבודה (Client Workstations)

#### דרישות מינימליות
- **CPU**: Intel Core i3 / AMD Ryzen 3 (דור 8 ומעלה)
- **RAM**: 4 GB
- **Storage**: 128 GB
- **Display**: 1366x768
- **Network**: 10 Mbps

#### דרישות מומלצות
- **CPU**: Intel Core i5 / AMD Ryzen 5 (דור 10 ומעלה)
- **RAM**: 8 GB
- **Storage**: 256 GB SSD
- **Display**: 1920x1080 (Full HD)
- **Network**: 50 Mbps


### התקנים ניידים (Mobile Devices)

#### iOS
- **OS Version**: iOS 14.0 ומעלה
- **Device**: iPhone 8 ומעלה, iPad (דור 6 ומעלה)
- **Storage**: 200 MB פנויים
- **Network**: WiFi או 4G/5G

#### Android
- **OS Version**: Android 9.0 (Pie) ומעלה
- **RAM**: 3 GB מינימום
- **Storage**: 200 MB פנויים
- **Network**: WiFi או 4G/5G

## דרישות תוכנה

### דפדפנים נתמכים

#### Desktop Browsers

| דפדפן | גרסה מינימלית | גרסה מומלצת | הערות |
|-------|---------------|-------------|-------|
| **Google Chrome** | 90+ | Latest | תמיכה מלאה, ביצועים מיטביים |
| **Mozilla Firefox** | 88+ | Latest | תמיכה מלאה |
| **Microsoft Edge** | 90+ (Chromium) | Latest | תמיכה מלאה |
| **Safari** | 14+ | Latest | macOS בלבד, תמיכה מלאה |
| **Opera** | 76+ | Latest | תמיכה מלאה |

#### Mobile Browsers

| דפדפן | פלטפורמה | גרסה מינימלית |
|-------|----------|---------------|
| **Safari Mobile** | iOS | 14+ |
| **Chrome Mobile** | Android/iOS | 90+ |
| **Samsung Internet** | Android | 14+ |
| **Firefox Mobile** | Android/iOS | 88+ |

#### דפדפנים לא נתמכים
- Internet Explorer (כל הגרסאות)
- דפדפנים ישנים ללא תמיכה ב-ES6
- דפדפנים ללא תמיכה ב-WebSocket

### תכונות דפדפן נדרשות

המערכת דורשת תמיכה בטכנולוגיות הבאות:
- **JavaScript ES6+**: תמיכה מלאה ב-ECMAScript 2015 ומעלה
- **WebSocket**: לעדכונים בזמן אמת
- **Local Storage**: לשמירת העדפות משתמש
- **Session Storage**: לניהול סשנים
- **Cookies**: חובה להפעלה (first-party cookies)
- **TLS 1.3**: תמיכה בפרוטוקול הצפנה מתקדם
- **WebRTC**: לשיחות וידאו (טלה-רפואה)

### תוכנות שרת

#### Application Server
- **Node.js**: 18.x LTS או 20.x LTS
- **Runtime**: V8 Engine
- **Package Manager**: npm 9+ או yarn 1.22+

#### Database
- **Primary Database**: PostgreSQL 14+ או 15+
- **Cache Layer**: Redis 7.0+
- **Search Engine**: Elasticsearch 8.x (אופציונלי)

#### Web Server / Reverse Proxy
- **NGINX**: 1.22+ (מומלץ)
- **Apache**: 2.4.50+ (חלופה)
- **Load Balancer**: HAProxy 2.6+ או AWS ALB

#### Container Runtime (אופציונלי)
- **Docker**: 20.10+
- **Kubernetes**: 1.25+ (לסביבות ארגוניות)
- **Docker Compose**: 2.x (לפיתוח)

## ארכיטקטורת Cloud

### מודל פריסה

המערכת תומכת במספר מודלי פריסה:

#### 1. Cloud-Native (מומלץ)
```
┌─────────────────────────────────────────┐
│         Load Balancer (ALB/NLB)         │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────┐      ┌────▼───┐
│  App   │      │  App   │
│ Server │      │ Server │
│  (EC2) │      │  (EC2) │
└───┬────┘      └────┬───┘
    │                │
    └────────┬───────┘
             │
    ┌────────▼────────┐
    │   RDS (Primary) │
    │   + Read Replica│
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │   S3 (Backups)  │
    └─────────────────┘
```

#### 2. Hybrid Cloud
- חלק מהשירותים ב-Cloud (גיבוי, DR)
- שרתי ייצור On-Premise
- חיבור מאובטח דרך VPN/Direct Connect

#### 3. On-Premise
- כל התשתית במתקן הארגון
- גיבוי ל-Cloud (מומלץ)
- דרישות חומרה מוגברות

### ספקי Cloud נתמכים

#### Amazon Web Services (AWS)

**שירותים מומלצים:**
- **Compute**: EC2 (t3.large ומעלה), ECS, EKS
- **Database**: RDS for PostgreSQL (Multi-AZ)
- **Cache**: ElastiCache for Redis
- **Storage**: S3 (Standard + Glacier for archives)
- **CDN**: CloudFront
- **Load Balancing**: Application Load Balancer
- **Monitoring**: CloudWatch
- **Security**: WAF, Shield, GuardDuty

**תצורה מינימלית:**
- EC2: 2x t3.large instances
- RDS: db.t3.large (Multi-AZ)
- ElastiCache: cache.t3.medium
- S3: Standard storage class
- **עלות משוערת**: $500-800/חודש

**תצורה מומלצת:**
- EC2: 3x t3.xlarge instances (Auto Scaling)
- RDS: db.r5.xlarge (Multi-AZ + Read Replica)
- ElastiCache: cache.r5.large (Cluster mode)
- S3: Standard + Intelligent-Tiering
- CloudFront: Global distribution
- **עלות משוערת**: $1,500-2,500/חודש

#### Microsoft Azure

**שירותים מומלצים:**
- **Compute**: Virtual Machines (Standard_D4s_v3+), AKS
- **Database**: Azure Database for PostgreSQL (Flexible Server)
- **Cache**: Azure Cache for Redis
- **Storage**: Blob Storage (Hot + Cool tiers)
- **CDN**: Azure CDN
- **Load Balancing**: Application Gateway
- **Monitoring**: Azure Monitor
- **Security**: Azure Firewall, DDoS Protection

#### Google Cloud Platform (GCP)

**שירותים מומלצים:**
- **Compute**: Compute Engine (n2-standard-4+), GKE
- **Database**: Cloud SQL for PostgreSQL
- **Cache**: Memorystore for Redis
- **Storage**: Cloud Storage (Standard + Nearline)
- **CDN**: Cloud CDN
- **Load Balancing**: Cloud Load Balancing
- **Monitoring**: Cloud Monitoring

## אסטרטגיית גיבוי ב-Cloud

### סוגי גיבויים

#### 1. Database Backups

**Automated Backups:**
- **תדירות**: כל 6 שעות
- **Retention**: 30 יום
- **סוג**: Full + Incremental
- **מיקום**: Multi-region replication
- **הצפנה**: AES-256

**Manual Snapshots:**
- לפני שדרוגים מרכזיים
- לפני שינויים קריטיים
- Retention: 90 יום

#### 2. File Storage Backups

**Patient Documents:**
- **תדירות**: Real-time replication
- **Versioning**: Enabled (30 versions)
- **Lifecycle**: 
  - Active: Standard storage
  - 90+ days: Intelligent-Tiering
  - 1+ year: Glacier/Archive
- **Retention**: 7 שנים (דרישה רגולטורית)

**System Files:**
- **תדירות**: Daily
- **Retention**: 14 יום
- **Compression**: Enabled

#### 3. Application State

**Configuration Backups:**
- **תדירות**: On every change
- **Version Control**: Git repository
- **Retention**: Unlimited

### Disaster Recovery (DR)

#### RTO/RPO Targets

| רמת שירות | RTO | RPO | עלות יחסית |
|-----------|-----|-----|-----------|
| **Basic** | 24 שעות | 6 שעות | 1x |
| **Standard** | 4 שעות | 1 שעה | 2x |
| **Premium** | 1 שעה | 15 דקות | 4x |
| **Mission Critical** | 15 דקות | 5 דקות | 8x |

#### Multi-Region Strategy

**Active-Passive:**
- Region ראשי: כל התעבורה
- Region משני: Standby warm
- Failover: Manual או Automatic
- **RTO**: 1-4 שעות

**Active-Active:**
- שני Regions פעילים
- Load balancing גיאוגרפי
- Automatic failover
- **RTO**: < 5 דקות

### תהליך שחזור

#### Backup Restoration

```bash
# Database Restore
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier clinic-db-restored \
  --db-snapshot-identifier clinic-db-snapshot-2024-03-14

# File Restore from S3
aws s3 sync s3://clinic-backups/2024-03-14/ /restore/path/ \
  --sse AES256
```

#### Point-in-Time Recovery (PITR)

- תמיכה בשחזור לכל נקודת זמן ב-30 הימים האחרונים
- דיוק של עד 5 דקות
- זמן שחזור: 15-60 דקות תלוי בגודל

## ניטור וביצועים

### מדדי ביצוע (KPIs)

#### Application Performance
- **Response Time**: < 200ms (p95)
- **Throughput**: 1000+ requests/second
- **Error Rate**: < 0.1%
- **Availability**: 99.9% (SLA)

#### Database Performance
- **Query Time**: < 50ms (p95)
- **Connection Pool**: 80% utilization max
- **Replication Lag**: < 1 second

#### Infrastructure
- **CPU Utilization**: 60-70% average
- **Memory Usage**: < 80%
- **Disk I/O**: < 80% capacity
- **Network Latency**: < 50ms

### כלי ניטור

#### Application Monitoring
- **APM**: New Relic, Datadog, או Dynatrace
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger או Zipkin

#### Infrastructure Monitoring
- **Metrics**: Prometheus + Grafana
- **Alerting**: PagerDuty או Opsgenie
- **Uptime**: Pingdom או StatusCake

## אבטחת רשת

### Network Architecture

```
Internet
   │
   ▼
┌──────────────┐
│     WAF      │
└──────┬───────┘
       │
┌──────▼───────┐
│  Public      │
│  Subnet      │  ← Load Balancer
└──────┬───────┘
       │
┌──────▼───────┐
│  Private     │
│  Subnet      │  ← App Servers
└──────┬───────┘
       │
┌──────▼───────┐
│  Database    │
│  Subnet      │  ← RDS (isolated)
└──────────────┘
```

### Security Groups / Firewall Rules

#### Load Balancer
- Inbound: 443 (HTTPS) from 0.0.0.0/0
- Outbound: 8080 to App Servers

#### App Servers
- Inbound: 8080 from Load Balancer
- Outbound: 5432 to Database, 443 to Internet

#### Database
- Inbound: 5432 from App Servers only
- Outbound: None

## דרישות רגולטוריות

### תאימות לתקנים

- **HIPAA**: Health Insurance Portability and Accountability Act
- **GDPR**: General Data Protection Regulation (אם רלוונטי)
- **ISO 27001**: Information Security Management
- **SOC 2 Type II**: Security and Availability

### Audit Logging

- שמירת לוגים למשך 7 שנים
- Immutable logs (WORM storage)
- Encrypted at rest and in transit
- Regular compliance audits

## סיכום

מערכת ניהול המרפאה מתוכננת כפתרון מודרני מבוסס Cloud עם דגש על זמינות גבוהה, אבטחה מקסימלית וגיבוי אוטומטי. הארכיטקטורה המודולרית מאפשרת התאמה לצרכים ספציפיים של כל ארגון, החל מקליניקות קטנות ועד בתי חולים גדולים.
