import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class CredibilityScorer:
    """Calculates credibility scores based on gathered evidence"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Weight configuration for different evidence types
        self.weights = {
            'red_flags': -0.3,  # Negative impact
            'supporting_evidence': 0.4,  # Positive impact
            'conflicting_evidence': -0.2,  # Negative impact
            'image_quality': 0.1,  # Slight positive impact
            'source_reliability': 0.2  # Positive impact
        }
    
    def assess_credibility(self, extracted_text: str = "", visual_features: Dict = None, 
                          evidence: Dict = None) -> Dict:
        """
        Assess overall credibility of a claim
        
        Args:
            extracted_text: Text extracted from image
            visual_features: Visual analysis results
            evidence: Gathered evidence
            
        Returns:
            Credibility assessment with score and reasoning
        """
        assessment = {
            'confidence_score': 0.5,  # Start with neutral score
            'assessment': 'NEEDS_MORE_EVIDENCE',
            'reasoning': [],
            'contributing_factors': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Calculate components
        text_score = self._analyze_text_credibility(extracted_text) if extracted_text else 0.5
        visual_score = self._analyze_visual_credibility(visual_features) if visual_features else 0.5
        evidence_score = self._analyze_evidence_credibility(evidence) if evidence else 0.5
        
        # Weighted average
        assessment['confidence_score'] = (
            text_score * 0.3 +
            visual_score * 0.25 +
            evidence_score * 0.45
        )
        
        # Store contributing factors
        assessment['contributing_factors'] = {
            'text_credibility_score': round(text_score, 2),
            'visual_credibility_score': round(visual_score, 2),
            'evidence_credibility_score': round(evidence_score, 2)
        }
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            assessment['confidence_score'],
            text_score,
            visual_score,
            evidence_score,
            evidence
        )
        assessment['reasoning'] = reasoning
        
        # Determine assessment category
        confidence = assessment['confidence_score']
        if confidence >= 0.75:
            assessment['assessment'] = 'CAN_BE_VERIFIED'
            assessment['recommendation'] = 'This claim appears trustworthy'
        elif confidence >= 0.45:
            assessment['assessment'] = 'NEEDS_MORE_EVIDENCE'
            assessment['recommendation'] = 'More information needed for verification'
        else:
            assessment['assessment'] = 'LOOKS_SUSPICIOUS'
            assessment['recommendation'] = 'This claim shows signs of being potentially fraudulent'
        
        self.logger.info(f"Credibility assessment complete - Score: {assessment['confidence_score']}, Assessment: {assessment['assessment']}")
        return assessment
    
    def _analyze_text_credibility(self, text: str) -> float:
        """Analyze text for credibility signals"""
        score = 0.5  # Start neutral
        
        if not text or len(text) < 10:
            return 0.3  # Very short text is suspicious
        
        # Check for professional language
        professional_words = ['hereby', 'confirm', 'verify', 'official', 'authentic', 'legitimate']
        text_lower = text.lower()
        professional_count = sum(1 for word in professional_words if word in text_lower)
        
        if professional_count > 0:
            score += 0.1
        
        # Check for excessive capitalization (COMMON IN SCAMS)
        if len(text) > 20:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.3:
                score -= 0.15  # Reduce score for excessive caps
        
        # Check text length (reasonable length is good)
        if 50 < len(text) < 500:
            score += 0.05
        elif len(text) > 500:
            score += 0.1  # Detailed explanations are more credible
        
        # Check for proper punctuation
        proper_punct = text.count('.') + text.count('!') + text.count('?')
        if proper_punct > len(text) / 100:  # Reasonable punctuation ratio
            score += 0.05
        
        return min(1.0, max(0.0, score))  # Clamp between 0 and 1
    
    def _analyze_visual_credibility(self, visual_features: Dict) -> float:
        """Analyze visual features for credibility"""
        score = 0.5  # Start neutral
        
        if not visual_features:
            return score
        
        # High quality images are more credible
        quality_score = visual_features.get('quality_score', 50) / 100
        score += quality_score * 0.2
        
        # Clear, sharp images are better
        if not visual_features.get('blurry', False):
            score += 0.1
        else:
            score -= 0.15
        
        # Good resolution is positive
        if not visual_features.get('low_resolution', False):
            score += 0.1
        else:
            score -= 0.1
        
        # Presence of watermark/branding is positive
        if visual_features.get('watermark_absence', False):
            score -= 0.05  # Absence is slightly negative
        
        # Pixelation is a red flag
        if visual_features.get('pixelation_detected', False):
            score -= 0.15
        
        return min(1.0, max(0.0, score))  # Clamp between 0 and 1
    
    def _analyze_evidence_credibility(self, evidence: Dict) -> float:
        """Analyze evidence for credibility assessment"""
        score = 0.5  # Start neutral
        
        if not evidence:
            return score
        
        summary = evidence.get('evidence_summary', {})
        
        # Count evidence items
        red_flags_count = summary.get('total_red_flags', 0)
        supporting_count = summary.get('supporting_evidence_count', 0)
        conflicting_count = summary.get('conflicting_evidence_count', 0)
        
        # Impact of red flags (each flag reduces score)
        if red_flags_count > 0:
            score -= min(0.3, red_flags_count * 0.05)  # Each flag: -0.05 (max -0.3)
        
        # Impact of supporting evidence (each piece increases score)
        if supporting_count > 0:
            score += min(0.2, supporting_count * 0.05)  # Each piece: +0.05 (max +0.2)
        
        # Impact of conflicting evidence (each piece reduces score)
        if conflicting_count > 0:
            score -= min(0.15, conflicting_count * 0.05)
        
        # Check severity of red flags
        red_flags = evidence.get('red_flags', [])
        high_severity_count = sum(1 for flag in red_flags if flag.get('severity') == 'high')
        
        if high_severity_count > 0:
            score -= min(0.2, high_severity_count * 0.1)  # Each high-severity: -0.1
        
        return min(1.0, max(0.0, score))  # Clamp between 0 and 1
    
    def _generate_reasoning(self, overall_score: float, text_score: float, 
                           visual_score: float, evidence_score: float, 
                           evidence: Dict = None) -> list:
        """Generate human-readable reasoning for the assessment"""
        reasoning = []
        
        # Text analysis reasoning
        if text_score > 0.6:
            reasoning.append("✓ Text appears professionally written")
        elif text_score < 0.4:
            reasoning.append("⚠ Text shows signs of poor quality or suspicious language")
        
        # Visual analysis reasoning
        if visual_score > 0.6:
            reasoning.append("✓ Image quality is good and consistent")
        elif visual_score < 0.4:
            reasoning.append("⚠ Image quality issues detected (blurry, low resolution, pixelation)")
        
        # Evidence analysis reasoning
        if evidence and evidence.get('evidence_summary'):
            summary = evidence['evidence_summary']
            red_flags = summary.get('total_red_flags', 0)
            
            if red_flags == 0:
                reasoning.append("✓ No major red flags detected")
            elif red_flags == 1:
                reasoning.append("⚠ One red flag detected")
            elif red_flags > 1:
                reasoning.append(f"🚨 Multiple red flags detected ({red_flags})")
            
            # Supporting evidence
            supporting = summary.get('supporting_evidence_count', 0)
            if supporting > 0:
                reasoning.append(f"✓ Found {supporting} supporting evidence(s)")
        
        # Overall assessment reasoning
        if overall_score >= 0.75:
            reasoning.append("✓ Overall assessment: High credibility")
        elif overall_score >= 0.45:
            reasoning.append("⚠ Overall assessment: Insufficient information for definitive conclusion")
        else:
            reasoning.append("🚨 Overall assessment: Multiple indicators suggest caution")
        
        return reasoning
