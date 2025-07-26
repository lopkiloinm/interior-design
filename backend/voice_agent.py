"""
Voice agent for text-to-speech using Inworld AI
"""
import requests
import base64
import os
import logging
from typing import Optional, Tuple
import uuid

logger = logging.getLogger(__name__)

class VoiceAgent:
    """Handle text-to-speech for interior design results"""
    
    def __init__(self):
        self.api_key = os.getenv('INWORLD_API_KEY')
        self.url = "https://api.inworld.ai/tts/v1/voice"
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("Inworld API key not found - voice agent disabled")
    
    def generate_design_summary(self, room_type: str, design_style: str, 
                               furniture_count: int, color_scheme: list) -> str:
        """Generate a spoken summary of the design"""
        colors = " and ".join(color_scheme[:2]) if len(color_scheme) > 1 else color_scheme[0]
        
        summary = f"""Welcome to your newly designed {room_type}! 
        
I've created a beautiful {design_style} interior that perfectly transforms your space. 
The design features a sophisticated {colors} color palette that brings warmth and elegance to the room.

I've carefully selected {furniture_count} furniture pieces that complement each other beautifully, 
creating a cohesive and inviting atmosphere.

Your new {room_type} balances both style and functionality, making it the perfect space 
for relaxation and daily living. I hope you love your transformed space!"""
        
        return summary
    
    async def generate_voice(self, text: str, voice_id: str = "Ashley") -> Optional[Tuple[bytes, str]]:
        """Generate voice audio from text"""
        if not self.enabled:
            return None
        
        try:
            headers = {
                "Authorization": f"Basic {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "voiceId": voice_id,
                "modelId": "inworld-tts-1"
            }
            
            response = requests.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            audio_content = base64.b64decode(result['audioContent'])
            
            # Save audio file
            filename = f"voice_{uuid.uuid4().hex[:8]}.mp3"
            filepath = os.path.join("uploads", filename)
            
            with open(filepath, "wb") as f:
                f.write(audio_content)
            
            logger.info(f"Generated voice audio: {filename}")
            return audio_content, f"/uploads/{filename}"
            
        except Exception as e:
            logger.error(f"Failed to generate voice: {e}")
            return None
    
    async def speak_design_results(self, design_plan, shopping_results) -> Optional[str]:
        """Generate and save voice narration for the design results"""
        if not self.enabled:
            return None
        
        try:
            # Extract design details
            room_type = design_plan.room_analysis.room_type
            design_style = design_plan.design_style
            color_scheme = design_plan.color_scheme
            furniture_count = len(shopping_results.items) if shopping_results else 0
            
            # Generate summary text
            summary = self.generate_design_summary(
                room_type, design_style, furniture_count, color_scheme
            )
            
            # Generate voice
            result = await self.generate_voice(summary)
            if result:
                _, audio_path = result
                return audio_path
            
        except Exception as e:
            logger.error(f"Failed to speak design results: {e}")
        
        return None

# Singleton instance
voice_agent = VoiceAgent() 