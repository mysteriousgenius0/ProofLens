import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import traceback

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import analysis modules
from services.image_analyzer import ImageAnalyzer
from services.evidence_gatherer import EvidenceGatherer
from services.credibility_scorer import CredibilityScorer
from utils.helpers import allowed_file, validate_image

# Initialize services
image_analyzer = ImageAnalyzer()
evidence_gatherer = EvidenceGatherer()
credibility_scorer = CredibilityScorer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ProofLens ML Service',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """
    Main analysis endpoint
    Accepts image upload and returns credibility assessment
    """
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: jpg, jpeg, png, gif'}), 400
        
        # Validate image
        is_valid, error_msg = validate_image(file)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        logger.info(f"Processing image: {file.filename}")
        
        # Step 1: Extract text and visual features
        logger.info("Step 1: Analyzing image content...")
        extracted_text = image_analyzer.extract_text(file)
        visual_features = image_analyzer.detect_visual_red_flags(file)
        
        # Step 2: Gather evidence
        logger.info("Step 2: Gathering evidence...")
        evidence = evidence_gatherer.gather_evidence(
            text=extracted_text,
            visual_features=visual_features
        )
        
        # Step 3: Calculate credibility score
        logger.info("Step 3: Calculating credibility score...")
        credibility_assessment = credibility_scorer.assess_credibility(
            extracted_text=extracted_text,
            visual_features=visual_features,
            evidence=evidence
        )
        
        # Compile final report
        report = {
            'analysis_id': generate_analysis_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'extracted_content': {
                'text': extracted_text,
                'visual_elements': visual_features
            },
            'evidence': evidence,
            'credibility_assessment': credibility_assessment,
            'recommendation': get_recommendation(credibility_assessment)
        }
        
        logger.info(f"Analysis complete. Assessment: {credibility_assessment['assessment']}")
        return jsonify(report), 200
    
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error during analysis'}), 500

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """
    Text-only analysis endpoint
    For analyzing claims without images
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        if len(text) < 10:
            return jsonify({'error': 'Text too short for analysis'}), 400
        
        logger.info("Analyzing text claim...")
        
        # Gather evidence
        evidence = evidence_gatherer.gather_evidence(text=text)
        
        # Calculate credibility
        credibility_assessment = credibility_scorer.assess_credibility(
            extracted_text=text,
            evidence=evidence
        )
        
        report = {
            'analysis_id': generate_analysis_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'input_text': text,
            'evidence': evidence,
            'credibility_assessment': credibility_assessment,
            'recommendation': get_recommendation(credibility_assessment)
        }
        
        return jsonify(report), 200
    
    except Exception as e:
        logger.error(f"Error during text analysis: {str(e)}")
        return jsonify({'error': 'Internal server error during text analysis'}), 500

@app.route('/api/models/status', methods=['GET'])
def model_status():
    """Check status of loaded ML models"""
    return jsonify({
        'image_analyzer': 'loaded',
        'evidence_gatherer': 'loaded',
        'credibility_scorer': 'loaded',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

def generate_analysis_id():
    """Generate unique analysis ID"""
    import uuid
    return str(uuid.uuid4())

def get_recommendation(assessment):
    """Get user-friendly recommendation based on assessment"""
    score = assessment.get('confidence_score', 0)
    
    if score >= 0.75:
        return {
            'status': 'CAN_BE_VERIFIED',
            'message': '✅ Strong evidence supports this claim',
            'action': 'This claim appears trustworthy based on available evidence'
        }
    elif score >= 0.45:
        return {
            'status': 'NEEDS_MORE_EVIDENCE',
            'message': '⚠️ Insufficient evidence to make a determination',
            'action': 'More information needed. Seek additional sources and verification'
        }
    else:
        return {
            'status': 'LOOKS_SUSPICIOUS',
            'message': '🚨 Multiple red flags detected',
            'action': 'Exercise caution. This claim shows signs of being potentially fraudulent'
        }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
