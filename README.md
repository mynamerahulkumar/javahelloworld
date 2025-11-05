# Trading API with Stop Loss and Take Profit

A professional full-stack trading application with separate backend (FastAPI) and frontend (Next.js) packages.

## Project Structure

```
project-root/
├── backend/                    # Backend API (FastAPI)
│   ├── src/
│   │   ├── api/               # FastAPI routes
│   │   ├── services/         # Business logic
│   │   ├── models/            # Pydantic models
│   │   ├── auth/              # Client authentication
│   │   ├── config/            # Configuration
│   │   ├── utils/             # Utilities (logging, cleanup)
│   │   └── delta_rest_client/ # Delta Exchange client
│   ├── privatedata/           # Private data (not committed)
│   ├── logs/                  # Application logs
│   ├── main.py                # FastAPI app entry point
│   ├── pyproject.toml         # Python dependencies
│   └── *.sh                   # Management scripts
│
├── frontend/                  # Frontend (Next.js 14)
│   ├── app/                   # Next.js App Router
│   ├── components/            # React components
│   ├── lib/                   # Utilities and API client
│   ├── public/                # Static assets
│   └── package.json          # Node dependencies
│
├── scripts/                   # Individual service scripts
│   ├── start-backend.sh       # Start backend only
│   ├── stop-backend.sh        # Stop backend only
│   ├── restart-backend.sh     # Restart backend only
│   ├── start-frontend.sh      # Start frontend only
│   ├── stop-frontend.sh       # Stop frontend only
│   ├── restart-frontend.sh    # Restart frontend only
│   └── README.md              # Scripts documentation
├── logs/                      # Combined logs (backend + frontend)
├── start-all.sh               # Start both services
├── stop-all.sh                # Stop both services
├── restart-all.sh             # Restart both services
├── view-logs.sh               # View logs
└── README.md                  # This file
```

## Backend Setup

### Prerequisites

- Python 3.12+
- uv or pip

### Installation

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
uv sync
# or
pip install -e .
```

3. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

4. Configure environment variables in `.env`:
```env
DELTA_API_KEY=your_api_key_here
DELTA_API_SECRET=your_api_secret_here
DELTA_BASE_URL=https://api.india.delta.exchange
PORT=8501
HOST=0.0.0.0
```

5. Add client credentials to `privatedata/srp_client_trading.csv`:
```csv
srp_client_emailid,srp_client_id
client@example.com,123456
```

### Running the Full Stack Application

### Quick Start (Recommended)

The easiest way to run both backend and frontend together:

```bash
# Start both services
./start-all.sh

# Stop both services
./stop-all.sh

# Restart both services
./restart-all.sh

# View logs
./view-logs.sh              # View all logs
./view-logs.sh backend      # View backend logs only
./view-logs.sh frontend     # View frontend logs only
```

After running `./start-all.sh`, both services will be available at:
- Backend API: http://localhost:8501
- Backend Docs: http://localhost:8501/docs
- Frontend: http://localhost:3000

### Running Services Separately

#### Backend Only

**Option 1: Using scripts folder (Recommended)**
```bash
# Start backend
./scripts/start-backend.sh

# Stop backend
./scripts/stop-backend.sh

# Restart backend
./scripts/restart-backend.sh
```

**Option 2: Using backend scripts**
```bash
cd backend

# Start server
./start.sh

# Stop server
./stop.sh

# Restart server
./restart.sh

# View logs
./view_logs.sh
```

The API will be available at:
- API: http://localhost:8501
- Docs: http://localhost:8501/docs

#### Frontend Only

**Option 1: Using scripts folder (Recommended)**
```bash
# Start frontend
./scripts/start-frontend.sh

# Stop frontend
./scripts/stop-frontend.sh

# Restart frontend
./scripts/restart-frontend.sh
```

**Option 2: Using npm directly**

## Frontend Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8501/api/v1
```

### Running the Frontend

```bash
# Development server
npm run dev

# Production build
npm run build
npm start
```

The frontend will be available at: http://localhost:3000

## API Endpoints

### Place Limit Order (Wait)

**POST** `/api/v1/place-limit-order-wait`

Place a stop-limit order that waits for price to reach entry level, with bracket SL/TP.

**Headers:**
- `X-SRP-Client-ID` (required): Your SRP Client ID
- `X-SRP-Client-Email` (required): Your SRP Client Email
- `X-Delta-API-Key` (optional): Delta Exchange API Key
- `X-Delta-API-Secret` (optional): Delta Exchange API Secret
- `X-Delta-Base-URL` (optional): Delta Exchange Base URL

**Body:**
```json
{
  "symbol": "BTC",
  "product_id": 27,
  "entry_price": 107100,
  "size": 1,
  "side": "buy",
  "stop_loss_price": 106300,
  "take_profit_price": 107800,
  "client_order_id": "string",
  "wait_time_seconds": 60
}
```

**Response:**
```json
{
  "success": true,
  "order_id": 1019878258,
  "message": "Stop-limit order with bracket SL/TP placed successfully",
  "order_data": { ... },
  "error": null
}
```

## Features

- ✅ Stop-limit orders that wait for price to reach entry level
- ✅ Automatic bracket order placement (stop loss and take profit)
- ✅ Client authentication via CSV file
- ✅ Per-user logging system
- ✅ Configurable log retention and cleanup
- ✅ Multi-user support with optimized backend
- ✅ Separate backend and frontend packages for clean architecture

## Development

### Backend Development

The backend is organized into clean modules:
- `api/`: FastAPI routes
- `services/`: Business logic
- `models/`: Pydantic models for validation
- `auth/`: Client authentication
- `config/`: Configuration management
- `utils/`: Utility functions (logging, cleanup)
- `delta_rest_client/`: Delta Exchange API client

### Frontend Development

The frontend uses Next.js 14 with:
- TypeScript for type safety
- Tailwind CSS for styling
- App Router for routing
- React Server Components

## Security

- Client credentials are stored in `privatedata/` (not committed to git)
- API keys and secrets are never logged
- Sensitive data is sanitized in logs
- CORS is configured for API access

## License

MIT
