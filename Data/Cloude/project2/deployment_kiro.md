# Deployment Guide — Inventory & Logistics on Azure

> מדריך זה מכסה את פריסת מערכת ניהול המלאי ב-Azure.  
> אין זיקה לפרויקט ניהול המשימות; תשתית, שירותים ותצורה שונים לחלוטין.

---

## 1. ארכיטקטורת Azure

```
Internet
    │
    ▼
Azure Front Door (WAF + CDN + Global LB)
    │
    ├──► Azure API Management (rate limiting, auth gateway)
    │         │
    │         ▼
    │    AKS Cluster (Kubernetes)
    │         ├── api-deployment     (Node.js / .NET — REST API)
    │         ├── worker-deployment  (cron jobs: alerts, EOQ calc)
    │         └── ingress-nginx
    │
    ├──► Azure PostgreSQL Flexible Server (primary DB)
    │         └── Read Replica (reporting queries)
    │
    ├──► Azure Service Bus (async messaging — PO events, alerts)
    │
    ├──► Azure Blob Storage (PDF invoices, PO documents)
    │
    └──► Azure Monitor + Application Insights (observability)
```

---

## 2. דרישות מוקדמות

- Azure CLI ≥ 2.56 (`az --version`)
- `kubectl` ≥ 1.29
- `helm` ≥ 3.14
- Docker ≥ 25 + login ל-Azure Container Registry (ACR)
- Terraform ≥ 1.7 (לניהול תשתית)
- Subscription עם מכסת vCPU מינימלית: **32 vCores** (region: `westeurope`)

---

## 3. הגדרת משאבי Azure (Terraform)

### 3.1 Resource Group

```hcl
resource "azurerm_resource_group" "inventory" {
  name     = "rg-inventory-prod"
  location = "West Europe"
  tags = {
    project     = "inventory-logistics"
    environment = "production"
    owner       = "platform-team"
  }
}
```

### 3.2 Azure Kubernetes Service (AKS)

```hcl
resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-inventory-prod"
  location            = azurerm_resource_group.inventory.location
  resource_group_name = azurerm_resource_group.inventory.name
  dns_prefix          = "inv-prod"
  kubernetes_version  = "1.29"

  default_node_pool {
    name            = "system"
    node_count      = 3
    vm_size         = "Standard_D4s_v5"
    os_disk_size_gb = 128
    type            = "VirtualMachineScaleSets"
  }

  identity { type = "SystemAssigned" }

  network_profile {
    network_plugin = "azure"
    network_policy = "calico"
  }
}
```

### 3.3 Azure PostgreSQL Flexible Server

```hcl
resource "azurerm_postgresql_flexible_server" "db" {
  name                   = "psql-inventory-prod"
  resource_group_name    = azurerm_resource_group.inventory.name
  location               = azurerm_resource_group.inventory.location
  version                = "16"
  administrator_login    = var.db_admin_user
  administrator_password = var.db_admin_password
  storage_mb             = 131072   # 128 GB
  sku_name               = "GP_Standard_D4s_v3"

  high_availability {
    mode                      = "ZoneRedundant"
    standby_availability_zone = "2"
  }

  backup_retention_days        = 35
  geo_redundant_backup_enabled = true
}
```

### 3.4 Azure Service Bus

```hcl
resource "azurerm_servicebus_namespace" "main" {
  name                = "sb-inventory-prod"
  location            = azurerm_resource_group.inventory.location
  resource_group_name = azurerm_resource_group.inventory.name
  sku                 = "Premium"
  capacity            = 1
}

resource "azurerm_servicebus_queue" "po_events" {
  name         = "purchase-order-events"
  namespace_id = azurerm_servicebus_namespace.main.id

  max_delivery_count              = 5
  dead_lettering_on_message_expiration = true
  message_ttl                     = "P7D"
}

resource "azurerm_servicebus_queue" "alert_notifications" {
  name         = "stock-alert-notifications"
  namespace_id = azurerm_servicebus_namespace.main.id
  max_delivery_count = 3
}
```

---

## 4. Build & Push — Container Images

```bash
# Login ל-ACR
ACR_NAME="acrinventoryprod"
az acr login --name $ACR_NAME

# Build API
docker build -t ${ACR_NAME}.azurecr.io/inventory-api:${GIT_SHA} \
  -f docker/api/Dockerfile .
docker push ${ACR_NAME}.azurecr.io/inventory-api:${GIT_SHA}

# Build Worker (cron jobs)
docker build -t ${ACR_NAME}.azurecr.io/inventory-worker:${GIT_SHA} \
  -f docker/worker/Dockerfile .
docker push ${ACR_NAME}.azurecr.io/inventory-worker:${GIT_SHA}
```

---

## 5. Kubernetes Manifests

### 5.1 API Deployment

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inventory-api
  namespace: inventory
spec:
  replicas: 3
  selector:
    matchLabels:
      app: inventory-api
  template:
    metadata:
      labels:
        app: inventory-api
    spec:
      containers:
        - name: api
          image: acrinventoryprod.azurecr.io/inventory-api:__TAG__
          ports:
            - containerPort: 3000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: connection-string
            - name: SERVICE_BUS_CONNECTION
              valueFrom:
                secretKeyRef:
                  name: servicebus-credentials
                  key: connection-string
            - name: NODE_ENV
              value: "production"
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          readinessProbe:
            httpGet:
              path: /v1/health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /v1/health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
```

### 5.2 Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: inventory-api-hpa
  namespace: inventory
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: inventory-api
  minReplicas: 3
  maxReplicas: 12
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### 5.3 Worker CronJob — Alert Calculation

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: stock-alert-calculator
  namespace: inventory
spec:
  schedule: "0 */6 * * *"   # כל 6 שעות
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: worker
              image: acrinventoryprod.azurecr.io/inventory-worker:__TAG__
              command: ["node", "jobs/calculateAlerts.js"]
          restartPolicy: OnFailure
```

---

## 6. Database Migrations

```bash
# הרצת migrations לפני deploy (כחלק מ-CI/CD pipeline)
kubectl run db-migrate \
  --image=acrinventoryprod.azurecr.io/inventory-api:${GIT_SHA} \
  --namespace=inventory \
  --restart=Never \
  --env="DATABASE_URL=$(kubectl get secret db-credentials -o jsonpath='{.data.connection-string}' | base64 -d)" \
  -- node node_modules/.bin/db-migrate up

kubectl wait --for=condition=complete job/db-migrate --timeout=120s
kubectl delete pod db-migrate
```

---

## 7. Azure API Management (APIM)

```bash
# יצירת APIM instance
az apim create \
  --name apim-inventory-prod \
  --resource-group rg-inventory-prod \
  --publisher-name "Inventory Team" \
  --publisher-email "platform@company.com" \
  --sku-name Premium \
  --sku-capacity 1 \
  --location westeurope

# ייבוא OpenAPI spec
az apim api import \
  --resource-group rg-inventory-prod \
  --service-name apim-inventory-prod \
  --api-id inventory-v1 \
  --specification-format OpenApi \
  --specification-path ./docs/openapi.yaml \
  --path v1
```

### Rate Limiting Policy (APIM)

```xml
<policies>
  <inbound>
    <rate-limit-by-key calls="300" renewal-period="60"
      counter-key="@(context.Subscription.Id)" />
    <quota-by-key calls="50000" bandwidth="500000" renewal-period="86400"
      counter-key="@(context.Subscription.Id)" />
    <validate-jwt header-name="Authorization" failed-validation-httpcode="401">
      <openid-config url="https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration" />
    </validate-jwt>
  </inbound>
</policies>
```

---

## 8. Monitoring & Alerts

### 8.1 Application Insights

```bash
az monitor app-insights component create \
  --app ai-inventory-prod \
  --resource-group rg-inventory-prod \
  --location westeurope \
  --kind web \
  --application-type web \
  --retention-time 90
```

### 8.2 Azure Monitor Alerts

| התראה                       | מדד                              | סף        | פעולה            |
|-----------------------------|----------------------------------|-----------|-----------------|
| API Latency גבוה            | `requests/duration` P99          | > 2000ms  | PagerDuty alert |
| Error Rate גבוה             | `requests/failed` rate           | > 1%      | PagerDuty alert |
| Pod restarts                | AKS container restart count      | > 5 / 5m  | Slack #ops      |
| DB CPU                      | PostgreSQL CPU percentage        | > 85%     | Slack #ops      |
| Service Bus Dead Letter     | Dead-lettered messages count     | > 10      | Email           |

---

## 9. CI/CD Pipeline — GitHub Actions

```yaml
# .github/workflows/deploy-prod.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Login to ACR
        run: az acr login --name acrinventoryprod

      - name: Build & Push Images
        run: |
          docker build -t acrinventoryprod.azurecr.io/inventory-api:${{ github.sha }} .
          docker push acrinventoryprod.azurecr.io/inventory-api:${{ github.sha }}

      - name: Run DB Migrations
        run: ./scripts/run-migrations.sh ${{ github.sha }}

      - name: Deploy to AKS
        run: |
          az aks get-credentials --resource-group rg-inventory-prod --name aks-inventory-prod
          sed -i "s/__TAG__/${{ github.sha }}/g" k8s/api-deployment.yaml
          kubectl apply -f k8s/
          kubectl rollout status deployment/inventory-api -n inventory --timeout=300s

      - name: Smoke Test
        run: |
          API_URL=$(kubectl get ingress -n inventory -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')
          curl -f https://${API_URL}/v1/health
```

---

## 10. Rollback

```bash
# חזרה לגרסה קודמת
kubectl rollout undo deployment/inventory-api -n inventory

# חזרה לגרסה ספציפית
kubectl rollout undo deployment/inventory-api -n inventory --to-revision=3

# בדיקת היסטוריית revisions
kubectl rollout history deployment/inventory-api -n inventory
```

---

## 11. Checklist לפני Go-Live

- [ ] כל ה-secrets מאוחסנים ב-Azure Key Vault (לא ב-ConfigMaps)
- [ ] TLS certificate מוגדר ב-Front Door (cert auto-renewal)
- [ ] Backup PostgreSQL נבדק ושוחזר בהצלחה בסביבת staging
- [ ] APIM rate limiting נבדק בעומס (load test: 500 req/sec)
- [ ] PagerDuty rotation מוגדר לצוות on-call
- [ ] DR drill בוצע — RTO בפועל < 30 דקות
- [ ] GDPR DPA חתום עם Microsoft Azure
- [ ] Penetration test בוצע ותוצאות נוקו
