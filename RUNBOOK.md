# AI Cloud Cost Detective Runbook

## Overview
This runbook explains how to start the backend API and access the frontend from a browser.

## 1. Backend

### 1.1 Install Python dependencies
From the repository root:

```powershell
python -m pip install -r backend/requirements.txt
```

### 1.2 Start the backend server
From the repository root:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The backend API should be available at:

- `http://127.0.0.1:8000`
- API root: `http://127.0.0.1:8000/api`

### 1.3 Backend prerequisites

- Ensure `.env` is configured if the backend depends on environment variables.
- Ensure Azure CLI is installed and logged in if you need Azure resource scanning.
- Ensure any required OpenAI or other API keys are available to the backend.

## 2. Frontend

### Option A: Static test page (recommended if `npm` is not installed)

From the repository root:

```powershell
cd frontend
python -m http.server 3000
```

Then open in browser:

- `http://127.0.0.1:3000/test.html`

This page is already configured to call the backend at:

- `http://127.0.0.1:8000/api`

### Option B: Vite frontend dev server (if Node/npm is installed)

From the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Then open the URL printed by Vite, usually:

- `http://localhost:5173`

## 3. Using the app in the browser

1. Open the frontend page:
   - Static page: `http://127.0.0.1:3000/test.html`
   - Vite app: `http://localhost:5173`
2. Use the authentication section to sign up or log in.
3. Click `Get Resource Groups` to fetch Azure resource groups.
4. Enter a resource group name and click `Analyze`.
5. Click `Get Analysis History` to review saved results.

## 4. Troubleshooting

- If the frontend cannot reach the backend:
  - Confirm backend is running on `127.0.0.1:8000`.
  - Confirm the frontend is using the matching API URL.
- If you see CORS errors:
  - The backend is already configured for local testing. Restart the backend after any CORS change.
- If `npm` is not available, use the static server option.

## 5. Notes

- The backend uses FastAPI and runs on port `8000`.
- The frontend test page is served on port `3000` when using the Python static server.
- If using Vite, the frontend will usually run on port `5173`.
