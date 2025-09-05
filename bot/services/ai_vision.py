"""
OpenAI Vision API integration for product analysis
"""
import json
import logging
import time
from typing import Dict, Any, Optional

from openai import AsyncOpenAI

from bot.config import Config

logger = logging.getLogger(__name__)

class AIVisionAnalyzer:
    """OpenAI Vision API integration for product image analysis"""
    
    def __init__(self):
        if Config.OPENAI_API_KEY:
            try:
                self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            self.client = None
        self.model = Config.OPENAI_MODEL
        self.product_types = Config.PRODUCT_TYPES
        self.colors = Config.COLORS
        
    async def analyze_product_image(self, image_url: str, user_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze product image using OpenAI Vision API
        
        Args:
            image_url: Public URL of the image to analyze
            user_context: Optional context provided by user
            
        Returns:
            Dictionary containing structured product analysis
        """
        start_time = time.time()
        
        if not self.client:
            return self._get_fallback_analysis(image_url, "OpenAI API key not configured")
        
        try:
            # Construct detailed prompt with controlled vocabulary
            prompt = self._build_analysis_prompt(user_context)
            
            # Make API call to OpenAI Vision
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url", 
                                "image_url": {
                                    "url": image_url,
                                    "detail": "high"  # High detail for better analysis
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent results
            )
            
            # Parse and validate response
            raw_content = response.choices[0].message.content
            analysis = self._parse_ai_response(raw_content)
            
            # Add metadata
            analysis.update({
                "processing_time": round(time.time() - start_time, 2),
                "model_used": self.model,
                "image_url": image_url,
                "api_usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                }
            })
            
            logger.info(f"AI analysis completed in {analysis['processing_time']}s")
            return analysis
            
        except Exception as e:
            logger.error(f"AI Vision analysis failed: {e}")
            return self._get_fallback_analysis(image_url, str(e))
    
    def _build_analysis_prompt(self, user_context: Optional[str] = None) -> str:
        """Build the analysis prompt with controlled vocabulary"""
        
        context_text = f"\n\nAdditional context: {user_context}" if user_context else ""
        
        return f"""You are an expert product cataloger. Analyze this product image and provide detailed information in JSON format.

**STRICT VOCABULARY REQUIREMENTS:**
- Type: MUST be exactly one of: {', '.join(self.product_types)}
- Color: MUST be exactly one of: {', '.join(self.colors)}

**Required JSON Response:**
{{
    "title": "Concise product title (max 60 characters)",
    "description": "Detailed product description focusing on visible features (max 250 characters)",
    "type": "Product type from vocabulary list above",
    "color": "Primary/dominant color from vocabulary list above", 
    "secondary_colors": ["array", "of", "additional", "colors", "if", "any"],
    "brand": "Brand name if clearly visible, otherwise 'unknown'",
    "material": "Visible material type (cotton, leather, denim, etc.) or 'unknown'",
    "style_features": ["key", "style", "elements", "visible"],
    "condition": "new/used/vintage assessment",
    "confidence_score": 85,
    "brand_confidence": 45,
    "analysis_notes": "Any important details or uncertainties"
}}

**Analysis Guidelines:**
- Focus on clearly visible features only
- Use conservative confidence scoring
- If brand is unclear or confidence < 70, use 'unknown'
- Be specific about style features (collar type, fit, etc.)
- Note any damage, wear, or quality indicators{context_text}

Provide ONLY the JSON response, no additional text."""

    def _parse_ai_response(self, raw_content: str) -> Dict[str, Any]:
        """Parse and validate AI response"""
        try:
            # Extract JSON from response (handle cases where AI adds extra text)
            content = raw_content.strip()
            
            # Find JSON boundaries
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = content[json_start:json_end]
            analysis = json.loads(json_str)
            
            # Validate and clean the response
            analysis = self._validate_analysis(analysis)
            
            return analysis
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse AI response: {e}\nRaw content: {raw_content}")
            raise ValueError(f"Invalid AI response format: {e}")
    
    def _validate_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize analysis results"""
        
        # Required fields with defaults
        required_fields = {
            "title": "Product",
            "description": "Product analysis available",
            "type": "other",
            "color": "multicolor", 
            "brand": "unknown",
            "confidence_score": 0,
            "brand_confidence": 0
        }
        
        # Ensure all required fields exist
        for field, default in required_fields.items():
            if field not in analysis:
                analysis[field] = default
        
        # Validate vocabulary compliance
        if analysis["type"] not in self.product_types:
            logger.warning(f"Invalid product type '{analysis['type']}', using 'other'")
            analysis["type"] = "other"
        
        if analysis["color"] not in self.colors:
            logger.warning(f"Invalid color '{analysis['color']}', using 'multicolor'")
            analysis["color"] = "multicolor"
        
        # Validate confidence scores
        for score_field in ["confidence_score", "brand_confidence"]:
            try:
                score = int(analysis.get(score_field, 0))
                analysis[score_field] = max(0, min(100, score))  # Clamp to 0-100
            except (ValueError, TypeError):
                analysis[score_field] = 0
        
        # Clean text fields
        analysis["title"] = str(analysis["title"])[:60]  # Max 60 chars
        analysis["description"] = str(analysis["description"])[:250]  # Max 250 chars
        analysis["brand"] = str(analysis["brand"]).strip()
        
        # Ensure optional fields exist
        optional_fields = {
            "secondary_colors": [],
            "material": "unknown",
            "style_features": [],
            "condition": "unknown",
            "analysis_notes": ""
        }
        
        for field, default in optional_fields.items():
            if field not in analysis:
                analysis[field] = default
        
        return analysis
    
    def _get_fallback_analysis(self, image_url: str, error_msg: str) -> Dict[str, Any]:
        """Return fallback analysis when AI processing fails"""
        return {
            "title": "Product (Analysis Failed)",
            "description": "AI analysis unavailable - manual review required",
            "type": "other",
            "color": "multicolor",
            "secondary_colors": [],
            "brand": "unknown",
            "material": "unknown",
            "style_features": [],
            "condition": "unknown",
            "confidence_score": 0,
            "brand_confidence": 0,
            "analysis_notes": f"AI processing failed: {error_msg}",
            "processing_time": 0,
            "model_used": self.model,
            "image_url": image_url,
            "error": True,
            "api_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
    
    async def reanalyze_with_context(self, image_url: str, user_feedback: str) -> Dict[str, Any]:
        """
        Re-analyze image with additional user context/feedback
        
        Args:
            image_url: Public URL of the image
            user_feedback: User's feedback or additional context
            
        Returns:
            Updated analysis results
        """
        logger.info(f"Re-analyzing with user feedback: {user_feedback}")
        return await self.analyze_product_image(image_url, user_feedback)
    
    def get_supported_types(self) -> list:
        """Get list of supported product types"""
        return self.product_types.copy()
    
    def get_supported_colors(self) -> list:
        """Get list of supported colors"""
        return self.colors.copy()