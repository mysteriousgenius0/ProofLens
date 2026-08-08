# ProofLens Frontend

React web application for ProofLens fraud detection platform.

## Features
- Image upload interface
- Real-time analysis
- Report visualization
- User authentication
- Responsive design

## Installation

```bash
cd frontend
npm install
```

## Running

### Development
```bash
npm start
```

### Build
```bash
npm run build
```

### Docker
```bash
docker build -t prooflens-frontend .
docker run -p 80:80 prooflens-frontend
```

## Environment

The app connects to the backend at `/api` (proxied through package.json).
