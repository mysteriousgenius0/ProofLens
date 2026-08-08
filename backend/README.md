# ProofLens Backend API

Node.js/Express backend for ProofLens fraud detection platform.

## Features
- User authentication (JWT)
- Image analysis submission
- Report generation and retrieval
- Database integration (PostgreSQL)
- ML service integration
- RESTful API

## Installation

```bash
cd backend
npm install
cp .env.example .env
```

## Running

### Development
```bash
npm run dev
```

### Production
```bash
NODE_ENV=production npm start
```

### Docker
```bash
docker build -t prooflens-backend .
docker run -p 3000:3000 prooflens-backend
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Analysis
- `POST /api/analysis/submit` - Submit image for analysis
- `GET /api/analysis/:id` - Get analysis status

### Reports
- `GET /api/reports/:id` - Get analysis report
- `GET /api/reports` - List all reports

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile

## Environment Variables

See `.env.example` for all available variables.
