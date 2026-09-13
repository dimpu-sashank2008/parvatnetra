ï»¿# PARVAT NETRA / PAHAD AI ? PHASE 11A DEPLOYMENT RUNBOOK
**Standard Operating Procedure for Cloud Staging & Production Hosting**

---

## 1. Quick Launch Deployment Links

The repository is equipped with Infrastructure-as-Code manifests for instantaneous deployment across the leading cloud container and serverless providers:

### Option A: Railway (Preferred Platform ? CP15 & CP16)
1. Navigate to [**railway.com/new**](https://railway.com/new).
2. Select **"Deploy from GitHub repo"** and choose **`dimpu-sashank2008/parvatnetra`**.
3. Select the **`staging`** branch for the staging ring (or `main` for production).
4. Railway will automatically detect `railway.json` and `Dockerfile`.
5. Under service **Settings ? Networking**, click **"Generate Domain"** to produce an HTTPS public URL (`https://<app>.up.railway.app`).
6. Set the Environment Variables under service **Variables** (refer to Section 3 below).

Alternatively via CLI:
```bash
npx @railway/cli login
npx @railway/cli link
npx @railway/cli up
```

---

### Option B: Render (Automated Alternative ? CP15)
1. Click the 1-click Blueprint deploy link:  
   ?? [**Deploy to Render**](https://render.com/deploy?repo=https://github.com/dimpu-sashank2008/parvatnetra)
2. Render reads `render.yaml` automatically and provisions the `parvatnetra-app` web service using the multi-stage Docker container.
3. Click **"Apply"** to trigger the build and launch.

---

### Option C: Vercel
1. Run from the terminal:
```bash
npx vercel --prod
```
2. Or use the 1-click import URL:  
   ?? [**Deploy with Vercel**](https://vercel.com/new/clone?repository-url=https://github.com/dimpu-sashank2008/parvatnetra)

---

## 2. Staging vs. Production Environment Variables (CP27)

| Environment Variable | Staging Setting (Mandatory) | Production Setting | Purpose |
|---|---|---|---|
| `PORT` | `8080` (or injected dynamically by host) | `8080` | Web server listening port |
| `FLASK_ENV` | `staging` | `production` | Framework mode |
| `ENABLE_PUBLIC_DISPATCH` | `0` (Strictly Disabled) | `1` (When formally authorized) | Civilian broadcast gate |
| `SIREN_DRY_RUN` | `1` (Dry-Run Emulation) | `0` (Hardware relay armed) | Acoustic siren lock |
| `CAP_PRODUCTION_DISPATCH` | `0` | `1` | OASIS CAP national dispatch |
| `PUBLIC_DEMO_TEST_ONLY` | `1` | `0` | Demo session isolation |
| `PAHAD_DEMO_MODE` | `0` | `0` | Prioritize live physics |
| `SECRET_KEY` | *(Auto-generated 64-char string)* | *(Secure random secret)* | Session signature encryption |

---

## 3. Post-Deployment Smoke Verification (CP22, CP23, CP24)

Once the public domain is live (e.g., `https://<app>.up.railway.app`):

1. **Verify Health Endpoint:**
   ```bash
   curl -i https://<public-domain>/health
   ```
   *Expected: HTTP 200 with `"status": "UP"`, `"application": "PARVAT NETRA"`*

2. **Verify Public Evaluator Geofence Demo:**
   - Open `https://<public-domain>/demo` in Chrome / Mobile browser.
   - Click **"Acquire GPS via HTTPS"** to test browser geolocation permissions.
   - Click **"Simulate Inside (35m)"** &rarr; Verify badge turns **`INSIDE 50M GEOFENCE [ALERT]`** with evacuation advisory.
   - Click **"Simulate Outside (180m)"** &rarr; Verify badge returns to **`OUTSIDE 50M GEOFENCE [SAFE]`**.

3. **Verify Responsive Layouts:**
   Test using Chrome DevTools Device Mode at:
   - `360x800` (Standard Android)
   - `390x844` (iPhone 12/13/14/15)
   - `412x915` (Samsung Galaxy S20+)

---

## 4. Rollback Procedure (CP28)

If an issue occurs on staging or production:

1. **Instant Cloud Rollback:**
   - On Railway: Go to **Deployments**, select the previous green deployment, and click **"Redeploy"**.
   - On Render: Go to **Deploys**, find the last successful commit, and click **"Rollback to this deploy"**.
   - On Vercel: Run `npx vercel rollback <deployment-url>` or use the dashboard.

2. **Git Revert Strategy:**
   ```bash
   git checkout staging
   git revert HEAD
   git push origin staging
   ```
   *Continuous deployment will immediately deploy the reverted commit.*
