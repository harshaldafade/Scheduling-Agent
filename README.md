# Scheduling Agent

A full-stack, AI-powered scheduling assistant that helps you manage meetings, resolve conflicts, and coordinate with participants using natural language. Built for personal productivity, extensibility, and robust security.

---

## 🚀 Features
- Natural language scheduling (create, update, delete meetings)
- AI-powered conflict detection and resolution
- Multi-user support with OAuth (Google, GitHub)
- JWT authentication with refresh tokens
- Secure, robust backend (FastAPI, LangChain, SQLite/Postgres)
- Modern React frontend (TypeScript, Tailwind CSS)
- Voice/text interface (optional)
- Rate limiting, CSRF protection, and token blacklisting
- Extensible for new LLMs (OpenAI, Gemini, Claude, local, etc.)
- CI/CD with GitHub Actions

---

## 🛠️ Tech Stack
- **Backend:** Python 3.9+, FastAPI, LangChain, SQLite (dev) / PostgreSQL (prod)
- **Frontend:** React 18, TypeScript, Tailwind CSS, React Query
- **AI/LLM:** Gemini, OpenAI, or any LangChain-compatible LLM
- **Auth:** OAuth (Google, GitHub), JWT, refresh tokens
- **Other:** Redis (optional), Docker-ready, GitHub Actions for CI

---

## 📁 Project Structure
```
Scheduling-Agent/
├── backend/                 # FastAPI backend
│   ├── app/                 # Core backend code
│   ├── requirements.txt
│   ├── main.py
│   └── ...
├── frontend/                # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
├── docs/                    # Documentation
├── .github/                 # GitHub Actions, issue templates
├── .env.example             # Backend env template
├── README.md
└── LICENSE
```

---

## 🖼️ Screenshots

| Login & OAuth | Google Sign-In | Dashboard |
|:---:|:---:|:---:|
| ![Login](docs/screenshots/login.png) <br> _Login page with Google/GitHub OAuth_ | ![Google OAuth](docs/screenshots/oauth-google.png.png) <br> _Google account selection for OAuth_ | ![Dashboard](docs/screenshots/dashboard.png) <br> _Main dashboard with meeting stats and quick actions_ |

| AI Agent Chat | Meetings | Calendar |
|:---:|:---:|:---:|
| ![AI Agent](docs/screenshots/ai-agent.png) <br> _Conversational AI scheduling assistant_ | ![Meetings](docs/screenshots/meetings.png) <br> _List and manage all meetings_ | ![Calendar](docs/screenshots/calendar.png) <br> _Calendar view of scheduled meetings_ |

| Preferences & Learning | Team Members |
|:---:|:---:|
| ![Preferences](docs/screenshots/preferences.png) <br> _Set preferences and view AI recommendations_ | ![Users](docs/screenshots/users.png) <br> _View and manage team members_ |

**Descriptions:**
- **Login & OAuth:** Secure sign-in with Google or GitHub.
- **Google Sign-In:** OAuth flow for Google authentication.
- **Dashboard:** Overview of meetings, quick actions, and recent activity.
- **AI Agent Chat:** Conversational scheduling with the AI agent.
- **Meetings:** View, search, and manage all meetings.
- **Calendar:** Visual calendar of all scheduled meetings.
- **Preferences & Learning:** Manage your preferences and see AI recommendations.
- **Team Members:** View and coordinate with your team.

---

## ⚙️ How It Works

1. **User logs in** via Google or GitHub (OAuth).
2. **AI agent receives your request** (e.g., "Schedule a 1-hour meeting with John and Sarah next week").
3. **Backend parses the request** using LangChain and the selected LLM, with all relevant meeting context.
4. **Agent reasons about conflicts, preferences, and availability**-suggests optimal times or asks for more info if needed.
5. **Pending proposals** are held for user confirmation before any database changes.
6. **User confirms or modifies the proposal**; only then is the meeting created/updated/deleted in the database.
7. **Frontend updates in real time**-dashboard, calendar, and analytics reflect the latest state.

---

## 🧩 Extensibility

- **LLM Provider Agnostic:** Easily add or switch LLMs (Gemini, OpenAI, Claude, local, etc.) by updating environment variables and LangChain configuration.
- **Modular Backend:** Add new tools, actions, or integrations (e.g., Slack, Google Calendar) with minimal changes to the FastAPI/LangChain codebase.
- **Frontend Ready for Expansion:** Add new pages, analytics, or user roles as needed. The React codebase is modular and easy to extend.

---

## 🌍 Open Source & Community

- **MIT License:** Open for personal, academic, or commercial use.
- **CONTRIBUTING.md:** Clear guidelines for contributing code, reporting issues, and submitting pull requests.
- **Issue Templates:** Standardized templates for bug reports and feature requests to streamline collaboration.
- **Security Best Practices:** Secrets are protected, and the codebase is ready for public collaboration.

We welcome contributions, feedback, and new ideas from the community!

---

## 📝 Project Summary

The Scheduling Agent is a full-stack, AI-powered web application that acts as your intelligent assistant for seamless meeting scheduling, team coordination, and personal productivity. It leverages state-of-the-art LLMs (like Gemini, OpenAI, etc.) to understand natural language, resolve conflicts, and optimize meeting times, all while keeping your data secure and your experience smooth.

---

## ⚡ Quickstart

### 1. Clone the repo
```bash
git clone git@github.com:harshaldafade/Scheduling-Agent.git
cd Scheduling-Agent
```

### 2. Setup Environment Variables
- Copy `backend/env.example` to `backend/.env` and fill in your secrets.
- Copy `frontend/env.example` to `frontend/.env` and set your API URL.

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Frontend Setup
```bash
cd frontend
npm install
```

### 5. Run the App (Development)
- **Backend:**
  ```bash
  cd backend
  uvicorn main:app --reload
  ```
- **Frontend:**
  ```bash
  cd frontend
  npm start
  ```

---

## 🔑 Environment Variables

### Backend (`backend/.env`)
See `backend/env.example` for all options. Key variables:
- `OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.
- `SECRET_KEY` (generate securely!)
- `DATABASE_URL` (SQLite for dev, Postgres for prod)
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, etc.
- `FRONTEND_URL`, `ALLOWED_ORIGINS`

### Frontend (`frontend/.env`)
See `frontend/env.example` for all options. Key variables:
- `REACT_APP_API_URL`
- `REACT_APP_FRONTEND_URL`

---

## 🧪 Testing
- **Backend:**
  ```bash
  cd backend
  pytest
  ```
- **Frontend:**
  ```bash
  cd frontend
  npm test
  ```

---

## 🔒 Security Notes
- Never commit your real `.env` files or secrets.
- Change `SECRET_KEY` in production.
- Use HTTPS and secure cookies in production.
- Set proper CORS and OAuth redirect URIs for your deployment.
- See the README and `env.example` for more security tips.

---

## 🤝 Contributing
- Open issues for bugs, features, or questions
- Fork and submit pull requests
- See [CONTRIBUTING.md](CONTRIBUTING.md) for code style and test instructions

---

## ⚙️ CI/CD
- GitHub Actions for backend/frontend linting and tests
- See `.github/workflows/ci.yml` for details

---

## 📄 License
MIT License — see [LICENSE](LICENSE)

---

## 📬 Contact
**Harshal Dafade**  
[GitHub](https://github.com/harshaldafade)

---

*Built with ❤️ for productivity and learning.* 
