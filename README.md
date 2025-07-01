# AI-Powered Scheduling Agent POC

A proof-of-concept for an intelligent scheduling agent that can coordinate meetings across multiple participants using AI to understand preferences and constraints.

## 🔒 Security & Public Repo Checklist
- **Never commit your real `.env` files, API keys, or secrets.**
- `.env.example` is safe to share and should be used as a template for others.
- Your `.gitignore` is set up to protect secrets, local DBs, and development files—double-check it before pushing.
- For more, see [12-Factor App: Config](https://12factor.net/config) and [GitHub's secret scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning).

## 🎯 Business Goal

Build a smart Scheduling Agent that can:
- Collect preferences, constraints, and availability from multiple users
- Use LLMs to reason over conflicts and preferences
- Propose ideal time slots for meetings, interviews, or group events
- Simulate personalized conversation to refine user needs and scheduling goals

## 🏗️ System Architecture

### Core Components

#### Inputs
- User preferences and constraints
- Calendar availability data
- Meeting requirements and duration
- Participant information

#### AI Functionalities
- Natural language understanding of scheduling requests
- Conflict resolution and optimization
- Preference learning and memory
- Multi-user coordination

#### Outputs
- Proposed meeting time slots
- Conflict resolution suggestions
- Personalized scheduling recommendations

### Technology Stack

**Backend:**
- Python 3.9+
- FastAPI for REST API
- LangChain for agent framework
- OpenAI/Claude for LLM integration
- SQLite for data persistence

**Frontend:**
- React 18 with TypeScript
- Tailwind CSS for styling
- React Query for state management
- React Hook Form for form handling

## 🚀 Features

### Core Features
- [x] Multi-user scheduling coordination
- [x] AI-powered preference understanding
- [x] Conflict resolution and optimization
- [x] Agent memory for user preferences
- [x] Natural language scheduling requests
- [x] Real-time availability checking

### Bonus Features
- [x] Voice AI integration (text-to-speech)
- [x] Hallucination detection and validation
- [x] Dynamic preference learning
- [x] Modern, responsive UI
- [x] Real-time collaboration

## 📁 Project Structure

```
Scheduling-Agent/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── agents/         # LangChain agents
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── api/           # API routes
│   ├── requirements.txt
│   └── main.py
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API services
│   │   └── types/        # TypeScript types
│   ├── package.json
│   └── index.html
├── docs/                  # Documentation
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key (or Claude API key)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Environment Variables
Create `.env` files in both backend and frontend directories **by copying from the provided `env.example` files and filling in your secrets**:

**Backend (.env):**
```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./scheduling_agent.db
```

**Frontend (.env):**
```
REACT_APP_API_URL=http://localhost:8000
```

### Running the Application
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm start
```

## 🎥 Demo Features

The demo showcases:
1. **Natural Language Scheduling**: Users can describe meeting requirements in plain English
2. **Multi-User Coordination**: Agent coordinates schedules across multiple participants
3. **Preference Learning**: Agent remembers and learns from user preferences
4. **Conflict Resolution**: Intelligent handling of scheduling conflicts
5. **Voice Interface**: Text-to-speech for accessibility
6. **Real-time Updates**: Live availability and scheduling updates

## 🔧 Technical Implementation

### Agent Framework (LangChain)
- **Scheduling Agent**: Main orchestrator for scheduling logic
- **Preference Agent**: Handles user preference learning
- **Conflict Resolution Agent**: Manages scheduling conflicts
- **Memory System**: Persistent storage of user preferences

### AI Integration
- **OpenAI GPT-4**: Primary LLM for natural language understanding
- **Claude**: Alternative LLM for complex reasoning tasks
- **Embeddings**: For preference similarity matching

### Data Pipeline
- **Calendar Parsing**: Integration with calendar APIs
- **Preference Learning**: ML pipeline for user preference analysis
- **Validation**: Hallucination detection and preference accuracy testing

## 🧪 Testing Strategy

### LLM Evaluation
- **Hallucination Detection**: Cross-validation with calendar data
- **Preference Accuracy**: A/B testing of scheduling suggestions
- **Performance Metrics**: Response time and accuracy tracking

### Integration Testing
- **Multi-user Scenarios**: Testing coordination across participants
- **Edge Cases**: Handling unusual scheduling constraints
- **Error Recovery**: Graceful handling of API failures

## 🚀 Innovation Highlights

1. **Adaptive Learning**: Agent improves scheduling accuracy over time
2. **Voice Integration**: Accessibility through text-to-speech
3. **Real-time Collaboration**: Live updates and notifications
4. **Smart Conflict Resolution**: AI-powered optimization of meeting times
5. **Personalization Engine**: Dynamic adaptation to user preferences

## 📊 Evaluation Criteria Alignment

### Solution Proposal (40%)
- ✅ **Creativity**: Innovative voice integration and adaptive learning
- ✅ **System Relevance**: Comprehensive scheduling coordination
- ✅ **Personalization**: Dynamic preference learning and memory

### Code & Demo Quality (60%)
- ✅ **Technical Depth**: Full-stack implementation with modern technologies
- ✅ **Agent Performance**: Multi-agent architecture with specialized roles
- ✅ **UI/UX Clarity**: Modern, responsive interface with excellent UX
- ✅ **Integration Quality**: Seamless backend-frontend integration

## 🎯 Next Steps

Potential enhancements for production:
- Slack/Teams integration
- Google Meet/Zoom auto-scheduling
- Advanced analytics and reporting
- Mobile app development
- Enterprise SSO integration

## Environment Setup

### 1. Backend Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# API Keys (choose one or more)
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Security (CHANGE THIS IN PRODUCTION!)
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Server Configuration
HOST=0.0.0.0
PORT=8000
REDIS_URL=redis://localhost:6379

# Frontend URLs (update for production)
FRONTEND_URL=http://localhost:3000
FRONTEND_LOGIN_URL=http://localhost:3000/login
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback/google
GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback/github
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# LLM Configuration
LLM_PROVIDER=gemini
```

### 2. Frontend Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_FRONTEND_URL=http://localhost:3000
```

## Security Considerations

⚠️ **IMPORTANT SECURITY NOTES:**

1. **Never commit `.env` files to version control**
2. **Change the SECRET_KEY in production** - use a strong, random key
3. **Use HTTPS in production** for all OAuth redirects
4. **Set up proper CORS origins** for your production domain
5. **Use environment-specific API keys** for different deployments
6. **Regularly rotate API keys and secrets**

## Production Deployment Checklist

Before deploying to production:

- [ ] Generate a strong SECRET_KEY (use `openssl rand -hex 32`)
- [ ] Update all OAuth redirect URIs to your production domain
- [ ] Set up HTTPS certificates
- [ ] Configure proper CORS origins
- [ ] Use production database (PostgreSQL/MySQL instead of SQLite)
- [ ] Set up Redis for caching (if needed)
- [ ] Configure proper logging
- [ ] Set up monitoring and error tracking

## CI/CD & Quality

This repo is ready for GitHub Actions. You can use workflows for:
- Linting and formatting
- Running backend and frontend tests
- Deploying to cloud or static hosts

A sample workflow is provided in `.github/workflows/ci.yml` (customize as needed).

## Contributing

Contributions are welcome! To contribute:
- Open an issue for bugs, feature requests, or questions
- Fork the repo and submit a pull request (PR)
- Follow clear commit messages and code style (see CONTRIBUTING.md if present)
- For help, open an issue or contact the maintainer via GitHub

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

If you wish to use a different license, replace the LICENSE file and update this section accordingly. 