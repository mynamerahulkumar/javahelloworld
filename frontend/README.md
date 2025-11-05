# Trading Frontend

Professional trading interface built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- ✅ Modern UI with shadcn/ui components
- ✅ Authentication system with Zustand
- ✅ React Query for server state management
- ✅ Trading dashboard with order placement forms
- ✅ Real-time price charts with Recharts
- ✅ Error boundaries and error handling
- ✅ Responsive design

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```bash
cp .env.example .env.local
```

3. Configure environment variables:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8501/api/v1
NEXT_PUBLIC_DEFAULT_DELTA_BASE_URL=https://api.india.delta.exchange
NEXT_PUBLIC_ENVIRONMENT=development
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

Build for production:

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Authentication routes
│   ├── (dashboard)/        # Protected dashboard routes
│   └── layout.tsx          # Root layout
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── trading/           # Trading-specific components
│   └── charts/            # Chart components
├── lib/
│   ├── api/               # API client
│   ├── hooks/             # React hooks
│   ├── types/             # TypeScript types
│   └── utils/             # Utility functions
├── store/                 # Zustand stores
└── public/                # Static assets
```

## Technologies

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - Component library
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Axios** - HTTP client
- **Recharts** - Charting library
- **React Hook Form** - Form handling
- **Zod** - Schema validation

## License

MIT
