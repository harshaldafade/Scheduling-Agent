# Deployment Guide

This guide covers how to deploy your AI Scheduling Agent to production with proper database setup.

## 🗄️ Database Setup

### **Development (SQLite)**
Your current setup uses SQLite, which is perfect for development but **not suitable for production hosting**.

### **Production (PostgreSQL)**
For production, you need a cloud database. Here are the best free/cheap options:

#### **1. Neon (Recommended - Free)**
```bash
# 1. Go to https://neon.tech
# 2. Sign up for free account
# 3. Create new project
# 4. Copy the connection string
```

**Environment Variables:**
```bash
DATABASE_URL=postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database
```

#### **2. Supabase (Free)**
```bash
# 1. Go to https://supabase.com
# 2. Create new project
# 3. Go to Settings > Database
# 4. Copy connection string
```

#### **3. Railway (Free tier)**
```bash
# 1. Go to https://railway.app
# 2. Create new project
# 3. Add PostgreSQL service
# 4. Copy connection string
```

## 🚀 Hosting Options

### **Frontend (React) - Easy Deployment**

#### **Netlify (Recommended)**
```bash
# 1. Push your code to GitHub
# 2. Go to netlify.com
# 3. Connect your GitHub repo
# 4. Set build settings:
#    - Build command: npm run build
#    - Publish directory: build
#    - Base directory: frontend
```

#### **Vercel**
```bash
# 1. Install Vercel CLI: npm i -g vercel
# 2. In frontend directory: vercel
# 3. Follow prompts
```

### **Backend (FastAPI) - More Complex**

#### **Railway (Recommended)**
```bash
# 1. Go to railway.app
# 2. Create new project
# 3. Connect GitHub repo
# 4. Add PostgreSQL service
# 5. Set environment variables
# 6. Deploy
```

#### **Render**
```bash
# 1. Go to render.com
# 2. Create new Web Service
# 3. Connect GitHub repo
# 4. Set build command: pip install -r requirements.txt
# 5. Set start command: uvicorn main:app --host 0.0.0.0 --port $PORT
# 6. Add PostgreSQL service
```

#### **Heroku**
```bash
# 1. Install Heroku CLI
# 2. Create Procfile in backend:
#    web: uvicorn main:app --host 0.0.0.0 --port $PORT
# 3. Add PostgreSQL addon
# 4. Deploy: git push heroku main
```

## 🔧 Environment Variables for Production

### **Backend (.env)**
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security (GENERATE NEW ONES!)
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# OAuth (Update URLs for production)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Frontend URLs (Update for your domain)
FRONTEND_URL=https://your-app.netlify.app
FRONTEND_LOGIN_URL=https://your-app.netlify.app/login
GOOGLE_REDIRECT_URI=https://your-app.netlify.app/auth/callback/google
GITHUB_REDIRECT_URI=https://your-app.netlify.app/auth/callback/github
ALLOWED_ORIGINS=https://your-app.netlify.app

# LLM
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
```

### **Frontend (.env)**
```bash
REACT_APP_API_URL=https://your-backend.railway.app
```

## 📋 Deployment Checklist

### **Before Deployment:**
- [ ] Set up PostgreSQL database
- [ ] Update OAuth redirect URLs
- [ ] Generate new SECRET_KEY
- [ ] Update frontend API URL
- [ ] Test locally with PostgreSQL

### **After Deployment:**
- [ ] Test OAuth login
- [ ] Test AI scheduling
- [ ] Check database connections
- [ ] Monitor logs for errors
- [ ] Set up custom domain (optional)

## 🐛 Common Issues

### **Database Connection Errors**
```bash
# Check if PostgreSQL is accessible
# Verify connection string format
# Ensure database exists
```

### **OAuth Errors**
```bash
# Update redirect URLs in Google/GitHub OAuth apps
# Check CORS settings
# Verify environment variables
```

### **CORS Errors**
```bash
# Update ALLOWED_ORIGINS with your frontend URL
# Check frontend API URL configuration
```

## 💰 Cost Estimates

### **Free Tier (Recommended for starting):**
- **Frontend:** Netlify/Vercel - Free
- **Backend:** Railway/Render - Free tier
- **Database:** Neon/Supabase - Free tier
- **Total:** $0/month

### **Paid Tier (When you scale):**
- **Backend:** $5-20/month
- **Database:** $5-15/month
- **Total:** $10-35/month

## 🔒 Security Notes

1. **Never commit .env files** to Git
2. **Use environment variables** for all secrets
3. **Generate new API keys** for production
4. **Update OAuth redirect URLs** for your domain
5. **Use HTTPS** in production

## 📞 Support

If you encounter issues:
1. Check the logs in your hosting platform
2. Verify environment variables
3. Test database connectivity
4. Check OAuth configuration 