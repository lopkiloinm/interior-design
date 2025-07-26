"""
Minimal LlamaIndex integration for interior design knowledge
"""
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.llms.openai import OpenAI
from typing import Dict, List
import os

# Design principles knowledge base
DESIGN_KNOWLEDGE = {
    "bedroom": [
        "Bedrooms should prioritize comfort and tranquility. Use soft, calming colors like blues, grays, or warm neutrals.",
        "Place the bed as the focal point, ideally against the longest wall and away from the door.",
        "Include bedside tables on both sides for balance and functionality.",
        "Layer lighting: overhead for general use, bedside lamps for reading, and accent lighting for ambiance.",
        "Add soft textiles like rugs, curtains, and throw pillows to absorb sound and create warmth."
    ],
    "living_room": [
        "Living rooms should balance comfort with style. Create conversation areas with seating facing each other.",
        "Use the 60-30-10 color rule: 60% dominant color, 30% secondary, 10% accent.",
        "Place the largest piece of furniture (usually sofa) first, then build around it.",
        "Create a focal point: fireplace, TV, art piece, or statement furniture.",
        "Mix textures and materials to add visual interest: wood, metal, fabric, glass."
    ],
    "kitchen": [
        "Follow the kitchen work triangle principle: sink, stove, and refrigerator should form an efficient triangle.",
        "Maximize counter space and ensure adequate task lighting over work areas.",
        "Use durable, easy-to-clean materials for high-traffic areas.",
        "Include both closed storage and open shelving for balance.",
        "Consider an island or peninsula for additional prep space and casual dining."
    ],
    "office": [
        "Position desk near natural light source but avoid glare on computer screens.",
        "Invest in ergonomic furniture: adjustable chair, proper desk height.",
        "Include both task lighting and ambient lighting to reduce eye strain.",
        "Add plants to improve air quality and create a calming environment.",
        "Use vertical storage solutions to maximize floor space."
    ]
}

class DesignKnowledgeBase:
    """Simple LlamaIndex-based knowledge retrieval for design tips"""
    
    def __init__(self):
        self.indices = {}
        self._initialize_indices()
    
    def _initialize_indices(self):
        """Create vector indices for each room type"""
        # Configure LlamaIndex to use OpenAI
        Settings.llm = OpenAI(model="gpt-4-turbo-preview", api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create indices for each room type
        for room_type, principles in DESIGN_KNOWLEDGE.items():
            documents = [Document(text=principle) for principle in principles]
            self.indices[room_type] = VectorStoreIndex.from_documents(documents)
    
    def get_design_tips(self, room_type: str, query: str = None) -> List[str]:
        """Get relevant design tips for a room type"""
        room_type = room_type.lower().replace(" ", "_")
        
        if room_type not in self.indices:
            # Return general tips if room type not found
            return [
                "Focus on creating a balanced and functional space.",
                "Use appropriate lighting for the room's purpose.",
                "Choose a cohesive color scheme.",
                "Consider traffic flow and furniture placement."
            ]
        
        if query:
            # Use query engine for specific questions
            query_engine = self.indices[room_type].as_query_engine()
            response = query_engine.query(query)
            return [str(response)]
        else:
            # Return all tips for the room type
            return DESIGN_KNOWLEDGE.get(room_type, [])
    
    def get_style_recommendations(self, style: str) -> Dict[str, List[str]]:
        """Get recommendations for specific design styles"""
        style_guides = {
            "modern": [
                "Use clean lines and minimal ornamentation",
                "Stick to neutral colors with bold accent pieces",
                "Choose furniture with geometric shapes",
                "Incorporate materials like glass, steel, and concrete"
            ],
            "scandinavian": [
                "Embrace minimalism with functional furniture",
                "Use light woods like pine, ash, or birch",
                "Keep color palette light and neutral",
                "Add cozy textiles for 'hygge' feeling"
            ],
            "traditional": [
                "Use rich, warm colors and classic patterns",
                "Choose furniture with curved lines and ornate details",
                "Layer different textures and fabrics",
                "Include antiques or vintage pieces"
            ],
            "industrial": [
                "Expose raw materials like brick, concrete, and metal",
                "Use a neutral color palette with darker tones",
                "Choose furniture with metal frames and reclaimed wood",
                "Add Edison bulb lighting for ambiance"
            ]
        }
        
        return style_guides.get(style.lower(), 
            ["Focus on creating a cohesive look that reflects your personal style"])

# Singleton instance
design_kb = DesignKnowledgeBase() 