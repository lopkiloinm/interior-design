# Quick Deploy Guide - 5 Minutes to Production! 🚀

## Fastest Option: Railway + Vercel

### 1. Deploy Backend to Railway (2 min)

```bash
# One-command deploy!
./deploy-railway.sh
```

Then add your environment variables in Railway dashboard:
- `OPENAI_API_KEY`
- `ARCADE_API_KEY` 
- `USER_ID`

Copy your Railway backend URL (e.g., `https://your-app.railway.app`)

### 2. Deploy Frontend to Vercel (2 min)

```bash
cd frontend
vercel
```

When prompted, add environment variable:
- `VITE_API_URL` = your Railway backend URL

### 3. Test Your Deployment (1 min)

```bash
./test-deployment.sh
```

## That's it! Your app is live! 🎉

---

## Alternative: All-in-One on Render

1. Fork this repo to your GitHub
2. Go to [render.com](https://render.com)
3. New > Blueprint > Connect your repo
4. Render will auto-deploy using `render.yaml`
5. Add environment variables in Render dashboard

---

## Local Development

```bash
# Start everything locally
./start.sh

# Or manually:
cd backend && source .venv/bin/activate && python main.py
cd frontend && npm run dev
``` 