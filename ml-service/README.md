# ML Service - ProofLens
ML Service implementation for ProofLens fraud detection system.

## Features
- Image text extraction (OCR)
- Visual red flag detection
- Evidence gathering from multiple sources
- Credibility scoring based on multiple factors
- Text and image analysis

## Project Structure
```
ml-service/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── .env.example             # Environment variables
├── services/
│   ├── image_analyzer.py    # Image analysis & OCR
│   ├── evidence_gatherer.py # Evidence collection
│   └── credibility_scorer.py # Confidence scoring
└── utils/
    └── helpers.py           # Utility functions
```

## Installation

### Local Development
```bash
cd ml-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

### Docker
```bash
docker build -t prooflens-ml .
docker run -p 5000:5000 prooflens-ml
```

## API Endpoints

### Health Check
```
GET /health
```

### Analyze Image
```
POST /api/analyze
Content-Type: multipart/form-data

image: <image_file>
```

### Analyze Text
```
POST /api/analyze/text
Content-Type: application/json

{
  "text": "Your claim text here..."
}
```

### Model Status
```
GET /api/models/status
```

## How It Works

### 1. Image Analysis
- Extract text using Tesseract OCR
- Preprocess image for better accuracy
- Detect visual red flags

### 2. Evidence Gathering
- Detect scam keywords
- Analyze claim patterns
- Verify facts

### 3. Credibility Scoring
- Weight text quality (30%)
- Weight visual quality (25%)
- Weight gathered evidence (45%)
- Generate confidence score (0-1)
