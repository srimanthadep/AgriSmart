# AgriSmart - Deployment Guide

## Project Structure

```
AgriSmart/
├── backend/          ← Deploy to Render
│   ├── app.py
│   ├── create_model.py
│   ├── Crop_recommendation.csv
│   ├── crop_recommendation_model.pkl
│   ├── scaler.pkl
│   ├── requirements.txt
│   ├── render.yaml
│   └── .env.example
│
└── frontend/         ← Deploy to Vercel
    ├── index.html
    └── vercel.json
```

---

## Step 1 — Deploy Backend to Render

1. Push the `backend/` folder to a GitHub repo (or the full project).
2. Go to [https://render.com](https://render.com) → **New Web Service**.
3. Connect your GitHub repo and set **Root Directory** to `backend`.
4. Render will auto-detect `render.yaml`. Confirm these settings:
   - **Build Command:** `pip install -r requirements.txt && python create_model.py`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python
5. Under **Environment Variables**, add:
   - `WEATHER_API_KEY` = your OpenWeatherMap API key (get free at https://openweathermap.org/api)
6. Click **Create Web Service**.
7. Wait for the deploy. Your backend URL will be something like:
   `https://agrismart-backend.onrender.com`

---

## Step 2 — Deploy Frontend to Vercel

1. Open `frontend/index.html` and update line ~718:
   ```js
   const BACKEND_URL = 'https://YOUR-RENDER-APP-NAME.onrender.com';
   ```
2. Push the `frontend/` folder to a GitHub repo.
3. Go to [https://vercel.com](https://vercel.com) → **New Project**.
4. Import your GitHub repo and set **Root Directory** to `frontend`.
5. Framework Preset: **Other** (static site).
6. Click **Deploy**.
7. Your frontend will be live at `https://your-project.vercel.app`.

---

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
python create_model.py        # only needed once
cp .env.example .env          # add your API key
python app.py
```
Backend runs at: http://localhost:5000

### Frontend
Just open `frontend/index.html` in a browser, or serve with any static server:
```bash
cd frontend
npx serve .
```

> **Tip:** For local dev, set `BACKEND_URL = 'http://localhost:5000'` in `frontend/index.html`.
