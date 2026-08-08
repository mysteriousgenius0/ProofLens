import aiohttp
import asyncio
import logging
from typing import Dict, List
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class EvidenceGatherer:
    """Gathers evidence from multiple sources to verify claims"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.timeout = 10
    
    def gather_evidence(self, text: str = "", visual_features: Dict = None) -> Dict:
        """
        Gather evidence from multiple sources
        
        Args:
            text: Extracted text from image
            visual_features: Visual analysis results
            
        Returns:
            Dictionary of gathered evidence
        """
        evidence = {
            'sources_checked': [],
            'red_flags': [],
            'supporting_evidence': [],
            'conflicting_evidence': [],
            'evidence_summary': {}
        }
        
        if text:
            # Check for common scam keywords
            scam_keywords = self._detect_scam_keywords(text)
            if scam_keywords:
                evidence['red_flags'].extend(scam_keywords)
            
            # Check for suspicious claims
            suspicious_claims = self._analyze_claim_patterns(text)
            if suspicious_claims:
                evidence['red_flags'].extend(suspicious_claims)
            
            # Try to verify facts (simplified)
            verified_facts = self._verify_facts(text)
            evidence['supporting_evidence'].extend(verified_facts)
        
        if visual_features:
            # Add visual evidence
            visual_evidence = self._analyze_visual_evidence(visual_features)
            evidence['red_flags'].extend(visual_evidence['red_flags'])
            evidence['sources_checked'].append('visual_analysis')
        
        # Calculate evidence summary
        evidence['evidence_summary'] = {
            'total_red_flags': len(evidence['red_flags']),
            'supporting_evidence_count': len(evidence['supporting_evidence']),
            'conflicting_evidence_count': len(evidence['conflicting_evidence']),
            'sources_checked': evidence['sources_checked']
        }
        
        self.logger.info(f"Evidence gathering complete: {evidence['evidence_summary']}")
        return evidence
    
    def _detect_scam_keywords(self, text: str) -> List[Dict]:
        """Detect common scam keywords in text"""
        red_flags = []
        
        scam_keywords = {
            'urgent': {'severity': 'high', 'type': 'urgency_pressure'},
            'act now': {'severity': 'high', 'type': 'urgency_pressure'},
            'limited time': {'severity': 'high', 'type': 'urgency_pressure'},
            'claim reward': {'severity': 'high', 'type': 'false_reward'},
            'claim prize': {'severity': 'high', 'type': 'false_reward'},
            'you won': {'severity': 'high', 'type': 'false_reward'},
            'congratulations': {'severity': 'medium', 'type': 'false_reward'},
            'verify account': {'severity': 'high', 'type': 'credential_theft'},
            'confirm identity': {'severity': 'high', 'type': 'credential_theft'},
            'update payment': {'severity': 'high', 'type': 'payment_scam'},
            'click here': {'severity': 'medium', 'type': 'suspicious_link'},
            'click below': {'severity': 'medium', 'type': 'suspicious_link'},
            'free money': {'severity': 'high', 'type': 'false_reward'},
            'no catch': {'severity': 'high', 'type': 'false_reward'},
            'guaranteed': {'severity': 'medium', 'type': 'unrealistic_claim'}
        }
        
        text_lower = text.lower()
        
        for keyword, info in scam_keywords.items():
            if keyword in text_lower:
                red_flags.append({
                    'flag': f'Detected scam keyword: "{keyword}"',
                    'type': info['type'],
                    'severity': info['severity'],
                    'evidence': f'Text contains "{keyword}" which is commonly used in {info["type"]} scams'
                })
        
        self.logger.debug(f"Scam keywords detected: {len(red_flags)}")
        return red_flags
    
    def _analyze_claim_patterns(self, text: str) -> List[Dict]:
        """Analyze text for suspicious claim patterns"""
        red_flags = []
        
        patterns = {
            'unrealistic_earnings': {
                'keywords': ['$', 'earn', 'per day', 'per hour'],
                'type': 'unrealistic_claim'
            },
            'spelling_errors': {
                'keywords': ['recieve', 'occured', 'seperate'],
                'type': 'poor_quality'
            },
            'urgency': {
                'keywords': ['immediately', 'instantly', 'right now'],
                'type': 'urgency_pressure'
            }
        }
        
        text_lower = text.lower()
        
        # Check for spelling errors (simplified)
        common_misspellings = ['recieve', 'occured', 'seperate', 'benifits', 'suceed']
        for misspell in common_misspellings:
            if misspell in text_lower:
                red_flags.append({
                    'flag': 'Spelling errors detected',
                    'type': 'poor_quality',
                    'severity': 'low',
                    'evidence': f'Contains misspelling: "{misspell}" - commonly found in phishing/scam emails'
                })
        
        self.logger.debug(f"Claim patterns analyzed: {len(red_flags)} suspicious patterns found")
        return red_flags
    
    def _verify_facts(self, text: str) -> List[Dict]:
        """Attempt to verify facts in the text"""
        verified = []
        
        # This is a simplified version; in production, you'd integrate with fact-checking APIs
        # like ClaimBuster, Google Fact Check API, etc.
        
        # Example: Check if text mentions known companies
        known_companies = ['amazon', 'apple', 'microsoft', 'google', 'facebook', 'twitter']
        text_lower = text.lower()
        
        for company in known_companies:
            if company in text_lower:
                verified.append({
                    'fact': f'Mentions company: {company.capitalize()}',
                    'verification_status': 'company_verified',
                    'evidence': 'Company name is legitimate'
                })
        
        return verified
    
    def _analyze_visual_evidence(self, visual_features: Dict) -> Dict:
        """Analyze visual features for evidence"""
        visual_evidence = {'red_flags': []}
        
        if visual_features.get('blurry'):
            visual_evidence['red_flags'].append({
                'flag': 'Image is blurry',
                'type': 'image_quality',
                'severity': 'medium',
                'evidence': 'Blurry images are often used to hide manipulation or low quality'
            })
        
        if visual_features.get('low_resolution'):
            visual_evidence['red_flags'].append({
                'flag': 'Low resolution image',
                'type': 'image_quality',
                'severity': 'low',
                'evidence': 'Low quality images may indicate hastily created content'
            })
        
        if visual_features.get('watermark_absence'):
            visual_evidence['red_flags'].append({
                'flag': 'No watermark or branding',
                'type': 'legitimacy',
                'severity': 'low',
                'evidence': 'Official promotions usually have clear branding'
            })
        
        if visual_features.get('pixelation_detected'):
            visual_evidence['red_flags'].append({
                'flag': 'Pixelation detected',
                'type': 'image_manipulation',
                'severity': 'high',
                'evidence': 'May indicate image has been compressed or manipulated'
            })
        
        quality_score = visual_features.get('quality_score', 0)
        if quality_score < 40:
            visual_evidence['red_flags'].append({
                'flag': f'Low image quality (score: {quality_score}/100)',
                'type': 'image_quality',
                'severity': 'medium',
                'evidence': 'Poor quality images are common in fraudulent content'
            })
        
        return visual_evidence
