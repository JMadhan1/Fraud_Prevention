import re
import json
from datetime import datetime
from textblob import TextBlob
import math

class FraudDetector:
    def __init__(self):
        # Enhanced fraud indicators with multi-language support
        self.fraud_keywords = {
            'english': [
                # Investment scams
                'guaranteed returns', 'risk-free investment', 'double your money',
                'limited time offer', 'exclusive opportunity', 'secret strategy',
                'insider information', 'pre-ipo', 'binary options', 'forex trading',

                # Ponzi scheme indicators
                'high returns', 'no risk', 'referral bonus', 'pyramid',
                'multi-level marketing', 'downline', 'matrix',

                # Urgency tactics
                'act now', 'limited spots', 'deadline', 'hurry', 'expires soon',
                'one-time offer', 'closing today', 'final warning',

                # Contact pressure
                'whatsapp only', 'telegram group', 'private group',
                'delete after reading', 'confidential', 'dont share',

                # Indian specific
                'sebi approved', 'rbi certified', 'government backed',
                'tax free returns', 'black money', 'demonetization profit',

                # Advanced patterns
                'deepfake', 'ai generated', 'pump and dump', 'wash trading',
                'market manipulation', 'coordinated buying', 'insider trading'
            ],
            'hindi': [
                'गारंटीशुदा रिटर्न', 'जोखिम मुक्त निवेश', 'पैसा दोगुना',
                'सीमित समय', 'विशेष अवसर', 'गुप्त रणनीति',
                'अंदरूनी जानकारी', 'तुरंत कार्य करें', 'व्हाट्सएप ग्रुप',
                'सेबी अप्रूवड', 'आरबीआई सर्टिफाइड', 'सरकारी समर्थन'
            ],
            'tamil': [
                'உத்தரவாதமான வருமானம்', 'ஆபத்து இல்லாத முதலீடு', 'பணம் இரட்டிப்பாக்கம்',
                'வரையறுக்கப்பட்ட நேரம்', 'சிறப்பு வாய்ப்பு', 'இரகசிய உத்தி',
                'உள்ளக தகவல்', 'உடனே செயல்படுங்கள்', 'வாட்ஸ்அப் குழு'
            ]
        }

        # Suspicious patterns
        self.suspicious_patterns = [
            r'\b\d{10}\b',  # Phone numbers
            r'₹\s*\d+\s*lakh',  # Large amounts in lakhs
            r'₹\s*\d+\s*crore',  # Large amounts in crores
            r'\b\d+%\s*return',  # Percentage returns
            r'whatsapp.*\+\d+',  # WhatsApp numbers
            r'telegram.*@\w+',  # Telegram handles
            r'(?i)ai-generated', # AI generated content
            r'(?i)deepfake', # Deepfake content
            r'(?i)pump and dump', # Pump and dump schemes
            r'(?i)wash trading', # Wash trading
            r'(?i)market manipulation', # Market manipulation
            r'(?i)coordinated buying', # Coordinated buying
            r'(?i)insider trading' # Insider trading
        ]

    def analyze_content(self, content, content_type='text', language='english'):
        """
        Analyze content for fraud indicators and return risk score
        """
        analysis_result = {
            'risk_score': 0.0,
            'indicators': [],
            'sentiment': 'neutral',
            'urgency_level': 'low',
            'contact_pressure': False,
            'suspicious_patterns': [],
            'recommendation': 'safe'
        }

        if content_type == 'text':
            return self._analyze_text(content, analysis_result, language)
        elif content_type == 'url':
            return self._analyze_url(content, analysis_result)
        else:
            # For image/video, return basic analysis
            analysis_result['risk_score'] = 3.0
            analysis_result['indicators'].append('Media content requires manual review')
            return analysis_result

    def _analyze_text(self, text, result, language):
        """Analyze text content for fraud indicators"""
        text_lower = text.lower()
        risk_score = 0.0

        # Get keywords for the specified language, default to English if not found
        keywords_to_check = self.fraud_keywords.get(language, self.fraud_keywords['english'])

        # Check for all fraud keywords with proper scoring
        high_risk_keywords = [
            'guaranteed returns', 'risk-free investment', 'double your money',
            'money-back guarantee', '100% guaranteed', '99.9% success rate',
            'celebrity endorsed', 'bollywood stars', 'risk-free trading'
        ]
        
        medium_risk_keywords = [
            'limited time offer', 'exclusive opportunity', 'secret strategy',
            'insider information', 'pre-ipo', 'binary options', 'forex trading',
            'high returns', 'no risk', 'referral bonus', 'pyramid',
            'multi-level marketing', 'downline', 'matrix'
        ]
        
        # Check for high-risk fraud keywords
        for keyword in high_risk_keywords:
            if keyword in text_lower:
                risk_score += 3.0
                result['indicators'].append(f"High-risk keyword: '{keyword}'")

        # Check for medium-risk keywords  
        for keyword in medium_risk_keywords:
            if keyword in text_lower:
                risk_score += 2.0
                result['indicators'].append(f"Medium-risk keyword: '{keyword}'")

        # Check for urgency indicators
        urgency_indicators = [
            'act now', 'limited spots', 'deadline', 'hurry', 'expires soon',
            'one-time offer', 'closing today', 'final warning', 'limited time',
            'only 48 hours', 'only 24 hours', 'expires today'
        ]
        
        urgency_count = 0
        for indicator in urgency_indicators:
            if indicator in text_lower:
                urgency_count += 1
                risk_score += 2.0
                result['indicators'].append(f"Urgency indicator: '{indicator}'")

        if urgency_count > 0:
            result['urgency_level'] = 'high' if urgency_count >= 2 else 'medium'

        # Check for contact pressure
        contact_pressure_indicators = [
            'whatsapp only', 'telegram group', 'private group',
            'delete after reading', 'confidential', 'dont share',
            'download our app', 'call immediately', 'contact now'
        ]
        
        for pressure in contact_pressure_indicators:
            if pressure in text_lower:
                risk_score += 2.0
                result['contact_pressure'] = True
                result['indicators'].append(f"Contact pressure: '{pressure}'")

        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                risk_score += len(matches) * 1.0
                result['suspicious_patterns'].extend(matches)
                result['indicators'].append(f"Suspicious pattern found: {matches}")
        
        # Check for unrealistic success rates
        success_rate_pattern = r'(\d+(?:\.\d+)?)\s*%\s*success'
        success_matches = re.findall(success_rate_pattern, text_lower)
        for match in success_matches:
            rate = float(match)
            if rate >= 90.0:
                risk_score += 3.0
                result['indicators'].append(f"Unrealistic success rate: {rate}%")
        
        # Check for large money amounts
        money_patterns = [
            r'₹\s*(\d+(?:,\d+)*)\s*lakh',
            r'₹\s*(\d+(?:,\d+)*)\s*crore',
            r'₹\s*(\d+(?:,\d+)*(?:,\d+)*)'
        ]
        
        for pattern in money_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                amount_str = match.replace(',', '')
                if amount_str.isdigit():
                    amount = int(amount_str)
                    if amount >= 50000:  # Large amounts
                        risk_score += 2.0
                        result['indicators'].append(f"Large money amount mentioned: ₹{match}")

        # Analyze sentiment (basic implementation)
        positive_words = ['amazing', 'fantastic', 'incredible', 'unbelievable', 'extraordinary', 'profit', 'growth', 'opportunity']
        negative_words = ['loss', 'risk', 'danger', 'careful', 'warning', 'scam', 'fraud']

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count + 2:
            result['sentiment'] = 'overly_positive'
            risk_score += 1.0
            result['indicators'].append("Overly positive sentiment detected")
        elif negative_count > 0:
            result['sentiment'] = 'cautious'
            risk_score -= 0.5  # Slightly reduce risk for cautious language

        # Check for excessive use of emojis or special characters
        emoji_pattern = r'[😀-🙏🌀-🗿🚀-🛿⚀-⚿]'
        emoji_count = len(re.findall(emoji_pattern, text))
        if emoji_count > 5:
            risk_score += 0.5
            result['indicators'].append(f"Excessive emoji usage: {emoji_count} emojis")

        # Check for all caps (shouting)
        # Avoid checking if text is too short or contains only numbers/symbols
        if len(text) > 10 and not text.isnumeric() and not all(c in ' .,!?' for c in text):
            caps_count = sum(1 for c in text if c.isupper())
            total_letters = sum(1 for c in text if c.isalpha())
            if total_letters > 0 and (caps_count / total_letters) > 0.5:
                risk_score += 1.0
                result['indicators'].append("Excessive use of capital letters")

        # Check for AI-generated or deepfake indicators
        ai_indicators = ['deepfake', 'ai generated', 'synthetic media', 'generated by ai']
        for ai_indicator in ai_indicators:
            if ai_indicator in text_lower:
                risk_score += 2.0
                result['indicators'].append(f"AI-generated content detected: '{ai_indicator}'")

        # Cap the risk score at 10
        result['risk_score'] = min(risk_score, 10.0)

        # Set recommendation based on risk score
        if result['risk_score'] >= 8.0:
            result['recommendation'] = 'block_immediately'
        elif result['risk_score'] >= 6.0:
            result['recommendation'] = 'high_caution'
        elif result['risk_score'] >= 4.0:
            result['recommendation'] = 'moderate_caution'
        else:
            result['recommendation'] = 'safe'

        return result

    def _analyze_url(self, url, result):
        """Analyze URL for suspicious characteristics"""
        url_lower = url.lower()
        risk_score = 0.0

        # Check for suspicious domains
        suspicious_domains = [
            'bit.ly', 'tinyurl.com', 'short.link', 't.co',
            'invest-now', 'quick-money', 'easy-profit', 'get-rich-quick',
            'secure-login', 'verify-account', 'update-details'
        ]

        for domain in suspicious_domains:
            if domain in url_lower:
                risk_score += 2.0
                result['indicators'].append(f"Suspicious domain: {domain}")

        # Check for suspicious URL patterns
        if re.search(r'\d{8,}', url):  # Long numbers in URL
            risk_score += 1.0
            result['indicators'].append("Suspicious number pattern in URL")

        if url_lower.count('-') > 3:  # Too many hyphens
            risk_score += 0.5
            result['indicators'].append("Excessive hyphens in URL")

        if not url.startswith(('http://', 'https://')):
            risk_score += 1.5
            result['indicators'].append("Non-standard URL format")

        # Check for suspicious parameters
        suspicious_params = ['user_id', 'account_no', 'password', 'pin', 'otp']
        for param in suspicious_params:
            if f"{param}=" in url_lower:
                risk_score += 1.0
                result['indicators'].append(f"Suspicious URL parameter: '{param}'")

        # Check for shortened URLs that are not common or known
        shortening_services = ['bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 'is.gd']
        if any(service in url_lower for service in shortening_services):
            risk_score += 1.0
            result['indicators'].append("Use of URL shortener detected")


        result['risk_score'] = min(risk_score, 10.0)

        if result['risk_score'] >= 6.0:
            result['recommendation'] = 'block_url'
        elif result['risk_score'] >= 3.0:
            result['recommendation'] = 'caution_advised'
        else:
            result['recommendation'] = 'safe'

        # Set recommendation based on risk score
        if result['risk_score'] >= 8.0:
            result['recommendation'] = 'block_immediately'
        elif result['risk_score'] >= 6.0:
            result['recommendation'] = 'high_caution'
        elif result['risk_score'] >= 4.0:
            result['recommendation'] = 'moderate_caution'
        else:
            result['recommendation'] = 'safe'

        return result

    def _determine_fraud_type(self, indicators):
        """Determine the type of fraud based on indicators."""
        if any('keyword' in i and ('return' in i or 'guaranteed' in i or 'risk-free' in i) for i in indicators):
            return 'Investment Scam'
        elif any('pyramid' in i or 'multi-level' in i or 'downline' in i for i in indicators):
            return 'Ponzi Scheme'
        elif any('act now' in i or 'limited spots' in i or 'deadline' in i or 'hurry' in i for i in indicators):
            return 'Urgency Tactic'
        elif any('whatsapp' in i or 'telegram' in i for i in indicators):
            return 'Contact Pressure'
        elif any('deepfake' in i or 'ai generated' in i for i in indicators):
            return 'AI/Deepfake Scam'
        elif any('pump and dump' in i or 'wash trading' in i or 'market manipulation' in i for i in indicators):
            return 'Market Manipulation'
        else:
            return 'Unknown'

    def _assess_platform_risk(self, content_type):
        """Assess risk based on the content type/platform."""
        if content_type == 'url':
            return 'high'
        elif content_type == 'text':
            return 'medium'
        else: # image, video, etc.
            return 'low'