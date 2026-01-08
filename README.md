# CovenantIQ

AI-powered loan covenant monitoring platform for European markets.

## Overview

CovenantIQ automatically extracts covenants from loan agreements using AI and provides predictive analytics to warn of potential breaches 30-90 days in advance. Designed for portfolio managers, compliance officers, and risk analysts.

## Key Features

- **AI Document Extraction**: Automatically extract covenants from PDF loan agreements using Claude AI
- **Predictive Breach Warnings**: ML-based early warning system predicts covenant breaches with confidence scoring
- **Portfolio Dashboard**: Real-time risk visibility across loan portfolio
- **Smart Alerts**: Configurable notifications for critical covenant status changes
- **Compliance Reports**: Export audit-ready reports in PDF and CSV formats

## Technology Stack

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL with SQLAlchemy
- Anthropic Claude API (claude-sonnet-4)
- scikit-learn for predictions
- Deployed on Railway

### Frontend
- React 18 + TypeScript
- Vite build system
- Tailwind CSS
- Recharts for data visualization
- Deployed on Vercel

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Anthropic API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit with your API URL

# Start development server
npm run dev
```

## Environment Variables

### Backend
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/covenantiq
ANTHROPIC_API_KEY=sk-ant-xxxxx
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:5173
```

### Frontend
```env
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
CovenantIQ/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/    # API routes
│   │   ├── models/           # Database models
│   │   ├── services/         # AI & ML services
│   │   ├── schemas/          # Pydantic schemas
│   │   └── main.py          # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── lib/            # Utilities
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## API Documentation

Once running, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment

### Railway (Backend)
1. Create new Railway project
2. Add PostgreSQL database
3. Configure environment variables
4. Deploy from GitHub repository

### Vercel (Frontend)  
1. Import GitHub repository
2. Configure build settings (Vite)
3. Add environment variables
4. Deploy

See `railway_deployment.md` for detailed deployment instructions.

## Database Schema

- **users**: User accounts and authentication
- **loan_agreements**: Loan contracts and metadata
- **covenants**: Individual covenant terms
- **covenant_measurements**: Time-series compliance data
- **alerts**: Breach warnings and notifications
- **borrower_financials**: Financial metrics for ML predictions

## Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
black app/
flake8 app/

# Frontend linting
npm run lint
```

## Contributing

For questions or collaboration inquiries, please open an issue.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Anthropic for Claude AI API
- Open source community

---

Built with care for the European loan markets.
