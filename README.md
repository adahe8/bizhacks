# Asteria - Omni-Channel Marketing Campaign Management System

An AI-powered marketing campaign management platform that orchestrates campaigns across Facebook, Email, and Google Ads using CrewAI agents.

Watch our [short video demonstration on Youtube](https://www.youtube.com/watch?v=URq0O9-YYkI).

## Features

- **Multi-Channel Campaign Management**: Manage campaigns across Facebook, Email, and Google SEO
- **AI-Powered Agents**: Leverage CrewAI for intelligent campaign creation, execution, and optimization
- **Real-time Metrics & Analytics**: Track campaign performance with D3.js visualizations
- **Automated Budget Allocation**: Dynamic budget rebalancing based on performance
- **Compliance Checking**: Automated content validation against brand guidelines
- **Customer Segmentation**: AI-driven customer segment identification

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, D3.js
- **Backend**: FastAPI, SQLModel, SQLite
- **AI Framework**: CrewAI with Gemini API
- **Scheduling**: APScheduler
- **Task Execution**: ThreadPoolExecutor for concurrent campaigns

## Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd bizhacks
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your API keys:
# - GEMINI_API_KEY
# - Database connection details
# - External API endpoints (if using real APIs)
```

### 3. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

cd backend
# Create demo CSV files (if they don't exist)
# python -c "import sys; sys.path.append('..'); from data.demo_loader import create_demo_files; create_demo_files()"

# The database will be initialized automatically when you start the server
# If you need to manually initialize or reset the database:
python -c "import sys; sys.path.append('..'); from data.database import init_db; init_db()"
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install

# Build the application
npm run build
# or
yarn build
```

## Running the Application

### 1. Start the Backend Server

```bash
# From the backend directory
cd backend
PYTHONPATH=.. uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 2. Start the Frontend Development Server

```bash
# From the frontend directory
cd frontend
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`

## Initial Setup Flow

1. **Launch Application**: Navigate to `http://localhost:3000`
2. **Complete Setup Modals**: The application will guide you through:
   - Product selection
   - Firm details
   - Market information
   - Strategic goals
   - Budget allocation
   - Brand guardrails
3. **Upload Data**: Upload user and transaction CSV files
4. **Review Segments**: AI will generate customer segments
5. **Approve Campaigns**: Review and approve generated campaign ideas

## Project Structure

```
bizhacks/
├── frontend/          # Next.js frontend application
├── backend/           # FastAPI backend server
├── data/             # Database models and demo data
└── documentation/    # Additional documentation
```

## API Endpoints

- `POST /api/setup/initialize` - Initialize application with company data
- `GET /api/campaigns` - List all campaigns
- `POST /api/campaigns` - Create new campaign
- `GET /api/metrics/{campaign_id}` - Get campaign metrics
- `POST /api/agents/segment` - Generate customer segments
- `POST /api/agents/create-campaigns` - Generate campaign ideas
- `POST /api/schedules` - Schedule campaign execution

## Development

### Running Tests

```bash
# Backend tests
pytest backend/tests/

# Frontend tests
cd frontend && npm test
```

### Database Migrations

The application uses SQLModel with SQLite. Database schema is automatically created on first run.

### Adding New Agents

1. Create agent file in `backend/agents/`
2. Register in `crew_factory.py`
3. Add corresponding API endpoint in `backend/api/agents.py`

## Environment Variables

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key

# Database
DATABASE_URL=sqlite:///./campaign.db

# External APIs (for production)
FACEBOOK_API_KEY=your_facebook_key
GOOGLE_ADS_API_KEY=your_google_ads_key
EMAIL_SERVICE_API_KEY=your_email_service_key

# Application Settings
SCHEDULER_TIMEZONE=UTC
MAX_CONCURRENT_CAMPAIGNS=10
METRICS_REFRESH_INTERVAL=3600  # seconds
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**

   - Ensure SQLite is installed
   - Check file permissions for campaign.db

2. **Agent Execution Errors**

   - Verify GEMINI_API_KEY is set correctly
   - Check agent logs in `backend/logs/`

3. **Frontend Build Issues**
   - Clear Next.js cache: `rm -rf .next`
   - Reinstall dependencies: `rm -rf node_modules && npm install`

## License

This project is created for the BizHacks case competition.
