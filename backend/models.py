from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class AgentStatus(str, Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    SHOPPING = "shopping"
    DESIGNING = "designing"
    COMPLETED = "completed"
    ERROR = "error"

class FurnitureItem(BaseModel):
    title: str
    price: Optional[str] = None
    google_link: Optional[str] = None
    direct_link: Optional[str] = None
    source: Optional[str] = None
    delivery: Optional[str] = None
    product_rating: Optional[float] = None
    product_reviews: Optional[int] = None
    store_rating: Optional[float] = None
    store_reviews: Optional[int] = None
    # Additional fields we'll add during processing
    category: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    image_url: Optional[str] = None
    local_image_path: Optional[str] = None

class RoomAnalysis(BaseModel):
    room_type: str
    dimensions_estimate: Optional[Dict[str, float]] = None
    existing_features: List[str]
    lighting_conditions: str
    style_suggestions: List[str]
    color_palette: List[str]

class DesignPlan(BaseModel):
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    room_analysis: Optional[RoomAnalysis] = None
    design_style: str
    budget_estimate: Optional[float] = None
    furniture_needed: List[Dict[str, Any]]
    color_scheme: List[str]
    layout_description: str
    shopping_list: List[FurnitureItem] = []
    
class ShoppingQuery(BaseModel):
    query: str
    category: str
    max_price: Optional[float] = None
    style: Optional[str] = None

class ShoppingResult(BaseModel):
    query: str
    items: List[FurnitureItem]
    total_items: int
    search_time: float

class DesignProgress(BaseModel):
    status: AgentStatus
    current_step: str
    steps_completed: List[str]
    progress_percentage: float
    messages: List[Dict[str, Any]]
    errors: List[str] = []

class FinalDesign(BaseModel):
    session_id: str
    original_image: str
    designed_image: str
    design_plan: DesignPlan
    total_cost_estimate: float
    furniture_items: List[FurnitureItem]
    completion_time: float
    design_description: str 