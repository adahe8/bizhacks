# BizHacks Campaign Manager

An AI-powered omnichannel marketing campaign management system that leverages CrewAI agents to automate campaign creation, execution, and optimization across Facebook, Email, and Google Ads.

## 🚀 Features

- **AI-Powered Campaign Generation**: Automatically generate campaign ideas based on customer segments
- **Omnichannel Support**: Manage campaigns across Facebook, Email, and Google Ads
- **Customer Segmentation**: AI-driven customer segmentation based on transaction and demographic data
- **Automated Content Creation**: Generate channel-specific content with brand compliance checking
- **Budget Optimization**: AI-powered budget rebalancing based on campaign performance
- **Visual Dashboard**: Real-time metrics visualization and campaign performance tracking
- **Scheduled Execution**: Automated campaign execution with customizable frequencies
- **Compliance Checking**: Ensure all content adheres to brand guidelines before publishing

## 🏗️ Architecture

### Backend (FastAPI + CrewAI)
- **FastAPI**: REST API framework for backend services
- **SQLModel**: Database ORM with SQLite for data persistence
- **CrewAI**: Multi-agent framework for AI-powered automation
- **APScheduler**: Task scheduling for campaign execution
- **LangChain + OpenAI**: LLM integration for content generation

### Frontend (Next.js + TypeScript)
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **D3.js**: Data visualization for metrics
- **React Hot Toast**: User notifications

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- OpenAI API key

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd bizhacks
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or
yarn install

# Create .env.local file
cp .env.local.example .env.local
```

## 🚀 Running the Application

### Start Backend Server

```bash
# From project root
cd backend
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

### Start Frontend Development Server

```bash
# In a new terminal
cd frontend
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000`

## 📱 Usage

### Initial Setup

1. Navigate to `http://localhost:3000`
2. Complete the setup wizard:
   - Enter product details
   - Upload or enter company information
   - Define market details and strategic goals
   - Set budget and rebalancing frequency
   - Upload customer and transaction data (optional)

### Creating Campaigns

1. **Manual Creation**: 
   - Click "New Campaign" from the dashboard
   - Choose "Manual Creation"
   - Fill in campaign details
   - Save and approve

2. **AI Generation**:
   - Click "New Campaign" from the dashboard
   - Choose "AI Generation"
   - Select customer segments
   - Review and approve generated campaigns

### Managing Campaigns

- **Start/Pause**: Control campaign execution from the dashboard
- **View Metrics**: Click on any campaign to see detailed performance metrics
- **Schedule View**: Navigate to the schedule page to see upcoming executions
- **Budget Rebalancing**: Happens automatically based on your settings

## 🤖 AI Agents

The system uses specialized CrewAI agents for different tasks:

1. **Segmentation Agent**: Analyzes customer data to create meaningful segments
2. **Campaign Creation Agent**: Generates campaign ideas for each segment
3. **Orchestrator Agent**: Optimizes budget allocation across campaigns
4. **Content Generation Agents**: Channel-specific content creators (Facebook, Email, Google Ads)
5. **Compliance Agent**: Reviews content against brand guidelines
6. **Execution Agent**: Handles campaign publishing to external platforms
7. **Metrics Agent**: Gathers and analyzes performance data

## 📊 API Endpoints

### Campaign Management
- `GET /api/campaigns/` - List all campaigns
- `POST /api/campaigns/` - Create new campaign
- `GET /api/campaigns/{id}` - Get campaign details
- `PATCH /api/campaigns/{id}` - Update campaign
- `POST /api/campaigns/{id}/approve` - Approve campaign

### Scheduling
- `GET /api/schedules/` - Get all schedules
- `POST /api/schedules/{id}/schedule` - Schedule campaign
- `DELETE /api/schedules/{id}/schedule` - Unschedule campaign

### AI Operations
- `POST /api/agents/segment-customers` - Run customer segmentation
- `POST /api/agents/generate-campaigns` - Generate campaign ideas
- `POST /api/agents/rebalance-budgets` - Rebalance campaign budgets

## 🔧 Configuration

### Environment Variables

Backend (.env):
```
DATABASE_URL=sqlite:///campaign.db
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
DEBUG=True
```

Frontend (.env.local):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
# or
yarn test
```

## 📝 Project Structure

```
bizhacks/
├── frontend/                    # Next.js frontend
│   ├── app/                    # App router pages
│   ├── components/             # React components
│   ├── lib/                    # Utilities and API client
│   └── public/                 # Static assets
├── backend/                    # FastAPI backend
│   ├── api/                    # API routes
│   ├── services/               # Business logic
│   ├── agents/                 # CrewAI agents
│   ├── external_apis/          # External API integrations
│   └── core/                   # Core utilities
├── data/                       # Database and models
│   ├── models.py              # SQLModel definitions
│   └── database.py            # Database setup
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚧 Development Notes

- The external APIs (Facebook, Email, Google Ads) are currently mocked for development
- Replace mock implementations in `backend/external_apis/` with real API integrations for production
- Ensure proper API credentials are configured in the .env file
- The SQLite database is suitable for development; consider PostgreSQL for production

## 📄 License

This project is created for the BizHacks case competition.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request