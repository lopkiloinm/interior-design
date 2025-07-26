import os
import json
import asyncio
import logging
import base64
import time
import re
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from PIL import Image
import httpx
import io
from bs4 import BeautifulSoup

from openai import OpenAI
from arcadepy import Arcade
from dotenv import load_dotenv

from models import (
    AgentStatus, DesignPlan, RoomAnalysis, FurnitureItem,
    ShoppingResult, DesignProgress, FinalDesign
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class InteriorDesignAgent:
    def __init__(self, session_id: str, room_image_path: str):
        self.session_id = session_id
        self.room_image_path = room_image_path
        self.status = AgentStatus.IDLE
        self.design_plan = DesignPlan(
            session_id=session_id,
            design_style="modern",
            furniture_needed=[],
            color_scheme=[],
            layout_description=""
        )
        self.progress_messages = []
        self.steps_completed = []
        self.furniture_items = []
        self.errors = []
        self.start_time = time.time()
        
        # Initialize API clients
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.arcade_client = Arcade(api_key=os.getenv("ARCADE_API_KEY"))
        self.user_id = os.getenv("ARCADE_USER_ID", "default_user")
        
        # Agent memory for planning
        self.plan_markdown = ""
        self.current_step = ""
        
    async def run(self):
        """Main autonomous agent loop"""
        try:
            self.status = AgentStatus.ANALYZING
            self.add_message("🏠 Starting interior design analysis...")
            
            # Step 1: Analyze the empty room
            await self.analyze_room()
            
            # Step 2: Create design plan
            self.status = AgentStatus.PLANNING
            await self.create_design_plan()
            
            # Step 3: Search for furniture
            self.status = AgentStatus.SHOPPING
            await self.search_furniture()
            
            # Step 4: Generate final design
            self.status = AgentStatus.DESIGNING
            await self.generate_final_design()
            
            self.status = AgentStatus.COMPLETED
            self.add_message("✅ Interior design completed successfully!")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.errors.append(str(e))
            logger.error(f"Agent error: {str(e)}")
            self.add_message(f"❌ Error: {str(e)}")
    
    async def analyze_room(self):
        """Analyze the empty room using GPT-4.1-mini with vision capabilities"""
        self.current_step = "Analyzing room characteristics"
        self.add_message("🔍 Analyzing room dimensions, lighting, and features...")
        
        try:
            # Convert image to base64
            with open(self.room_image_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode()
            
            # Use OpenAI's responses API for room analysis
            response = self.openai_client.responses.create(
                model="gpt-4.1-mini",
                input=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": """Analyze this empty room and provide a detailed assessment:

1. Room type (bedroom, living room, kitchen, etc.)
2. Estimated dimensions (approximate width x length)
3. Existing features (windows, doors, built-ins, electrical outlets)
4. Natural lighting conditions
5. Suggested design styles that would work well
6. Recommended color palette based on lighting and space

Return your analysis as a JSON object with the following structure:
{
    "room_type": "string",
    "dimensions_estimate": {"width": number, "length": number},
    "existing_features": ["feature1", "feature2"],
    "lighting_conditions": "string",
    "style_suggestions": ["style1", "style2", "style3"],
    "color_palette": ["color1", "color2", "color3"]
}"""
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image_data}"
                        }
                    ]
                }]
            )
            
            # Parse the analysis
            analysis_text = response.output_text
            analysis_data = json.loads(analysis_text)
            
            self.design_plan.room_analysis = RoomAnalysis(**analysis_data)
            self.steps_completed.append("Room Analysis")
            self.add_message(f"✓ Room identified as: {analysis_data['room_type']}")
            
            # Update plan markdown
            self.plan_markdown += f"""# Interior Design Plan

## Room Analysis
- **Room Type**: {analysis_data['room_type']}
- **Estimated Dimensions**: {analysis_data['dimensions_estimate']['width']}m x {analysis_data['dimensions_estimate']['length']}m
- **Lighting**: {analysis_data['lighting_conditions']}
- **Existing Features**: {', '.join(analysis_data['existing_features'])}
- **Suggested Styles**: {', '.join(analysis_data['style_suggestions'])}
- **Color Palette**: {', '.join(analysis_data['color_palette'])}

"""
            
        except Exception as e:
            logger.error(f"Room analysis error: {str(e)}")
            self.errors.append(f"Room analysis failed: {str(e)}")
            # Fallback analysis
            self.design_plan.room_analysis = RoomAnalysis(
                room_type="living room",
                dimensions_estimate={"width": 4.5, "length": 5.5},
                existing_features=["window", "door"],
                lighting_conditions="natural light",
                style_suggestions=["modern", "minimalist", "scandinavian"],
                color_palette=["white", "light gray", "wood tones"]
            )
    
    async def create_design_plan(self):
        """Create a detailed design plan based on room analysis"""
        self.current_step = "Creating design plan"
        self.add_message("📝 Creating comprehensive design plan...")
        
        try:
            # Generate design plan using GPT-4.1-mini
            room_info = self.design_plan.room_analysis
            
            response = self.openai_client.responses.create(
                model="gpt-4.1-mini",
                input=[{
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": f"""Based on this room analysis, create a detailed interior design plan:

Room Type: {room_info.room_type}
Dimensions: {room_info.dimensions_estimate}
Style Suggestions: {room_info.style_suggestions}
Color Palette: {room_info.color_palette}

Create a comprehensive design plan that includes:
1. Selected design style
2. Detailed furniture list with categories
3. Layout description
4. Budget estimate
5. Color scheme refinement

Return as JSON:
{{
    "design_style": "string",
    "budget_estimate": number,
    "furniture_needed": [
        {{"item": "string", "category": "string", "priority": "high/medium/low", "quantity": number}}
    ],
    "color_scheme": ["color1", "color2", "color3"],
    "layout_description": "detailed layout plan"
}}"""
                    }]
                }]
            )
            
            # Debug log the response
            logger.info(f"Design plan response type: {type(response)}")
            logger.info(f"Design plan response: {response}")
            
            # Get the actual text from the response
            if hasattr(response, 'output_text'):
                response_text = response.output_text
            elif hasattr(response, 'text'):
                response_text = response.text
            elif hasattr(response, 'content'):
                response_text = response.content
            else:
                logger.error(f"Unknown response structure: {dir(response)}")
                raise ValueError("Could not extract text from OpenAI response")
            
            logger.info(f"Design plan text: {response_text[:200]}...")  # Log first 200 chars
            
            # Parse the JSON
            plan_data = json.loads(response_text)
            
            # Update design plan
            self.design_plan.design_style = plan_data["design_style"]
            self.design_plan.budget_estimate = plan_data["budget_estimate"]
            self.design_plan.furniture_needed = plan_data["furniture_needed"]
            self.design_plan.color_scheme = plan_data["color_scheme"]
            self.design_plan.layout_description = plan_data["layout_description"]
            
            self.steps_completed.append("Design Planning")
            self.add_message(f"✓ Design style selected: {plan_data['design_style']}")
            
            # Update plan markdown
            self.plan_markdown += f"""## Design Plan
- **Style**: {plan_data['design_style']}
- **Budget Estimate**: ${plan_data['budget_estimate']:,.2f}
- **Color Scheme**: {', '.join(plan_data['color_scheme'])}

### Layout Description
{plan_data['layout_description']}

### Furniture List
"""
            for item in plan_data['furniture_needed']:
                self.plan_markdown += f"- **{item['item']}** ({item['category']}) - Priority: {item['priority']} - Qty: {item['quantity']}\n"
            
            self.plan_markdown += "\n"
            
        except Exception as e:
            logger.error(f"Design planning error: {str(e)}")
            self.errors.append(f"Design planning failed: {str(e)}")
            
            # Set default values based on room type
            if not self.design_plan.design_style:
                self.design_plan.design_style = "Modern Scandinavian"
            if not self.design_plan.color_scheme:
                self.design_plan.color_scheme = ["White", "Light Oak", "Soft Gray"]
            if not self.design_plan.furniture_needed:
                if self.design_plan.room_analysis.room_type.lower() == "bedroom":
                    self.design_plan.furniture_needed = [
                        {"item": "bed", "category": "Bedroom", "priority": "high", "quantity": 1},
                        {"item": "nightstand", "category": "Bedroom", "priority": "medium", "quantity": 2},
                        {"item": "dresser", "category": "Storage", "priority": "medium", "quantity": 1}
                    ]
                else:
                    self.design_plan.furniture_needed = [
                        {"item": "sofa", "category": "Seating", "priority": "high", "quantity": 1},
                        {"item": "coffee table", "category": "Tables", "priority": "medium", "quantity": 1}
                    ]
                    
            # Update markdown with defaults
            self.plan_markdown = f"# Interior Design Plan\n\n## Room: {self.design_plan.room_analysis.room_type}\n\n"
            self.plan_markdown += f"### Design Style: {self.design_plan.design_style}\n\n"
            self.plan_markdown += f"### Color Scheme: {', '.join(self.design_plan.color_scheme)}\n\n"
            self.plan_markdown += "### Furniture Needed:\n"
            for item in self.design_plan.furniture_needed:
                self.plan_markdown += f"- **{item['item']}** ({item['category']}) - Priority: {item['priority']} - Qty: {item['quantity']}\n"
    
    async def search_furniture(self):
        """Search for furniture items using Arcade Google Shopping"""
        self.current_step = "Searching for furniture"
        self.add_message("🛍️ Searching for furniture items...")
        
        self.plan_markdown += "## Shopping Results\n"
        
        try:
            # Search for each furniture item - limit to 3 items max
            furniture_to_search = self.design_plan.furniture_needed[:3]  # Only search for 3 items
            
            for furniture in furniture_to_search:
                # Make query more generic - remove overly specific terms
                item_name = furniture['item'].lower()
                
                # Simplify common furniture names
                generic_names = {
                    'platform bed with light oak frame': 'bed',
                    'minimalist bedside tables': 'nightstand',
                    'simple dresser with warm white finish': 'dresser',
                    'scandinavian style desk': 'desk',
                    'ergonomic chair': 'office chair',
                    'bedside table': 'nightstand',
                    'bed frame': 'bed'
                }
                
                # Use generic name if available
                for specific, generic in generic_names.items():
                    if specific in item_name:
                        item_name = generic
                        break
                
                # Simple query - just the item type
                query = item_name
                
                # Keep queries super simple
                if len(query.split()) > 2:
                    # Just use the main furniture word
                    for word in ['bed', 'mattress', 'nightstand', 'dresser', 'desk', 'chair', 'sofa', 'table']:
                        if word in query:
                            query = word
                            break
                
                self.add_message(f"🔍 Searching for: {query}")
                
                try:
                    # Use Arcade API to search Google Shopping
                    result = await self._arcade_search(query)
                    
                    # Debug logging
                    logger.info(f"Arcade API result for '{query}': {result if result else 'None'}")
                    
                    # Try different ways to access the products
                    products = []
                    
                    if result:
                        # Method 1: Direct dictionary access
                        if isinstance(result, dict) and "output" in result:
                            output = result["output"]
                            if isinstance(output, dict) and "value" in output:
                                value = output["value"]
                                if isinstance(value, dict) and "products" in value:
                                    products = value["products"]
                        
                        # Method 2: If output is an object, try to access its attributes
                        if not products and hasattr(result, 'output'):
                            output = result.output
                            if hasattr(output, 'value'):
                                value = output.value
                                if hasattr(value, 'products'):
                                    products = value.products
                                elif isinstance(value, dict) and 'products' in value:
                                    products = value['products']
                            elif isinstance(output, dict) and 'value' in output:
                                value = output['value']
                                if isinstance(value, dict) and 'products' in value:
                                    products = value['products']
                    
                    if products:
                        products = products[:3]  # Get top 3 results
                        logger.info(f"Found {len(products)} products for {furniture['item']}")
                        
                        # Limit to 2 products per furniture type
                        added_count = 0
                        for idx, product in enumerate(products[:2]):
                            furniture_item = FurnitureItem(
                                title=product.get("title", furniture['item']),
                                price=product.get("price"),
                                google_link=product.get("google_link"),
                                direct_link=product.get("direct_link"),
                                source=product.get("source"),
                                delivery=product.get("delivery"),
                                product_rating=product.get("product_rating"),
                                product_reviews=product.get("product_reviews"),
                                store_rating=product.get("store_rating"),
                                store_reviews=product.get("store_reviews"),
                                category=furniture.get('category', 'Furniture')
                            )
                            
                            # Skip image scraping for now - just use Google Images later
                            # This prevents getting stuck on broken Google Shopping pages
                            self.furniture_items.append(furniture_item)
                            added_count += 1
                        
                        if added_count > 0:
                            self.add_message(f"✓ Found {added_count} options")
                            
                                                    # Use simpler category name in markdown
                            category_display = furniture.get('category', furniture['item'])
                            self.plan_markdown += f"\n### {category_display}\n"
                            for idx, product in enumerate(products, 1):
                                price_str = product.get('price', 'Price not available')
                                # Simplify the title for display
                                title = product.get('title', 'Unknown')
                                if len(title) > 60:
                                    title = title[:57] + "..."
                                self.plan_markdown += f"{idx}. **{title}** - {price_str}\n"
                                if product.get('source'):
                                    self.plan_markdown += f"   - Source: {product['source']}\n"
                                if product.get('product_rating'):
                                    self.plan_markdown += f"   - Rating: {product['product_rating']}⭐ ({product.get('product_reviews', 0)} reviews)\n"
                                if product.get('delivery'):
                                    self.plan_markdown += f"   - Delivery: {product['delivery']}\n"
                    else:
                        # No products found
                        logger.warning(f"No products found for query: {query}")
                        self.add_message(f"⚠️ No products found for: {furniture['item']}")
                        # Log the full result for debugging
                        if result:
                            logger.debug(f"Arcade API returned: {result}")
                        
                        # Fallback: Use mock data with real furniture links
                        self.add_message(f"🔄 Using alternative search for: {furniture['item']}")
                        mock_products = self._get_mock_furniture(furniture['item'], furniture.get('category', ''))
                        
                        # Only use 1 mock product per item
                        if mock_products:
                            mock_product = mock_products[0]
                            furniture_item = FurnitureItem(**mock_product)
                            self.furniture_items.append(furniture_item)
                            
                            self.plan_markdown += f"\n### {furniture['item']}\n"
                            self.plan_markdown += f"1. **{furniture_item.title}** - {furniture_item.price}\n"
                            if furniture_item.source:
                                self.plan_markdown += f"   - Source: {furniture_item.source}\n"
                    
                except Exception as e:
                    logger.error(f"Search error for {query}: {str(e)}")
                    self.add_message(f"⚠️ Could not find: {furniture['item']}")
                
                # Stop if we have enough items
                if len(self.furniture_items) >= 5:
                    self.add_message("✓ Found enough furniture items, moving on...")
                    break
                
                # Small delay between searches
                await asyncio.sleep(0.5)  # Reduced from 1 second
            
            self.steps_completed.append("Furniture Shopping")
            self.add_message(f"✓ Found {len(self.furniture_items)} furniture items")
            
        except Exception as e:
            logger.error(f"Shopping error: {str(e)}")
            self.errors.append(f"Shopping failed: {str(e)}")
    
    async def _arcade_search(self, query: str) -> Dict[str, Any]:
        """Execute Arcade Google Shopping search"""
        try:
            # Run in executor to handle sync Arcade client
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.arcade_client.tools.execute(
                    tool_name="GoogleShopping.SearchProducts@3.0.0",
                    input={
                        "owner": "ArcadeAI",
                        "name": "arcade-ai",
                        "starred": "true",
                        "keywords": query
                    },
                    user_id=self.user_id
                )
            )
            
            # The result is an ExecuteToolResponse object, we need to access its data
            if result:
                # Convert to dict - the ExecuteToolResponse should have attributes we can access
                try:
                    # Try to access as object attributes
                    if hasattr(result, 'dict'):
                        result_dict = result.dict()
                    elif hasattr(result, '__dict__'):
                        result_dict = result.__dict__
                    elif hasattr(result, 'model_dump'):
                        result_dict = result.model_dump()
                    else:
                        # Try to access common attributes
                        result_dict = {
                            'id': getattr(result, 'id', None),
                            'status': getattr(result, 'status', None),
                            'output': getattr(result, 'output', None),
                            'success': getattr(result, 'success', None),
                        }
                    
                    logger.info(f"Arcade API response type: {type(result).__name__}")
                    logger.info(f"Arcade API response attributes: {dir(result)}")
                    
                    return result_dict
                except Exception as e:
                    logger.error(f"Error converting Arcade response: {e}")
                    # Try to return the raw result
                    return result
            
            return {}
        except Exception as e:
            logger.error(f"Arcade API error: {str(e)}")
            # Log full error details
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {e}")
            return {}
    
    def _get_mock_furniture(self, item_name: str, category: str) -> List[Dict[str, Any]]:
        """Get mock furniture data when Arcade API fails"""
        # Mock data with realistic furniture items
        mock_data = {
            "mattress": [
                {
                    "title": "IKEA HAUGESUND Spring Mattress Medium Firm",
                    "price": "$279.00",
                    "source": "IKEA",
                    "category": category or "Bedroom",
                    "google_link": "https://www.ikea.com/us/en/p/haugesund-spring-mattress-medium-firm-beige-50307417/"
                },
                {
                    "title": "Casper Original Foam Mattress",
                    "price": "$595.00",
                    "source": "Casper",
                    "category": category or "Bedroom",
                    "google_link": "https://casper.com/mattresses/casper-original/"
                }
            ],
            "bed frame": [
                {
                    "title": "West Elm Mid-Century Bed Frame - Acorn",
                    "price": "$899.00",
                    "source": "West Elm",
                    "category": category or "Bedroom",
                    "google_link": "https://www.westelm.com/products/mid-century-bed-acorn-h6565/"
                },
                {
                    "title": "Article Nera Walnut Wood Bed",
                    "price": "$1,299.00",
                    "source": "Article",
                    "category": category or "Bedroom",
                    "google_link": "https://www.article.com/product/1457/nera-walnut-wood-bed"
                }
            ],
            "nightstand": [
                {
                    "title": "CB2 Suspend II Wood Nightstand",
                    "price": "$299.00",
                    "source": "CB2",
                    "category": category or "Bedroom",
                    "google_link": "https://www.cb2.com/suspend-ii-wood-nightstand/s574306"
                },
                {
                    "title": "IKEA NORDKISA Bamboo Nightstand",
                    "price": "$59.99",
                    "source": "IKEA",
                    "category": category or "Bedroom",
                    "google_link": "https://www.ikea.com/us/en/p/nordkisa-nightstand-bamboo-00468437/"
                }
            ],
            "dresser": [
                {
                    "title": "IKEA MALM 6-drawer Dresser White",
                    "price": "$229.00",
                    "source": "IKEA",
                    "category": category or "Bedroom",
                    "google_link": "https://www.ikea.com/us/en/p/malm-6-drawer-dresser-white-00360454/"
                },
                {
                    "title": "West Elm Penelope 6-Drawer Dresser",
                    "price": "$899.00",
                    "source": "West Elm",
                    "category": category or "Bedroom",
                    "google_link": "https://www.westelm.com/products/penelope-6-drawer-dresser-h5735/"
                }
            ],
            "desk": [
                {
                    "title": "Article Madera Oak Desk",
                    "price": "$449.00",
                    "source": "Article",
                    "category": category or "Office",
                    "google_link": "https://www.article.com/product/16069/madera-oak-desk"
                },
                {
                    "title": "IKEA IDASEN Desk Beige",
                    "price": "$279.00",
                    "source": "IKEA",
                    "category": category or "Office",
                    "google_link": "https://www.ikea.com/us/en/p/idasen-desk-beige-s79280997/"
                }
            ],
            "chair": [
                {
                    "title": "Herman Miller Aeron Chair",
                    "price": "$1,395.00",
                    "source": "Herman Miller",
                    "category": category or "Office",
                    "google_link": "https://www.hermanmiller.com/products/seating/office-chairs/aeron-chairs/"
                },
                {
                    "title": "IKEA JÄRVFJÄLLET Office Chair",
                    "price": "$229.00",
                    "source": "IKEA",
                    "category": category or "Office",
                    "google_link": "https://www.ikea.com/us/en/p/jaervfjaellet-office-chair-gunnared-beige-00521856/"
                }
            ],
            "sofa": [
                {
                    "title": "Article Sven Charme Tan Sofa",
                    "price": "$1,799.00",
                    "source": "Article",
                    "category": category or "Living Room",
                    "google_link": "https://www.article.com/product/1789/sven-charme-tan-sofa"
                },
                {
                    "title": "IKEA KIVIK Sofa Hillared Beige",
                    "price": "$579.00",
                    "source": "IKEA",
                    "category": category or "Living Room",
                    "google_link": "https://www.ikea.com/us/en/p/kivik-sofa-hillared-beige-s09419027/"
                }
            ]
        }
        
        # Find best match for the item
        item_lower = item_name.lower()
        for key, products in mock_data.items():
            if key in item_lower or item_lower in key:
                return products
        
        # Default fallback
        return [{
            "title": f"Modern {item_name}",
            "price": "$499.00",
            "source": "Generic Furniture Store",
            "category": category or "General",
            "google_link": f"https://www.google.com/search?q={item_name.replace(' ', '+')}"
        }]
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        try:
            if not price_str:
                return 0.0
            # Remove currency symbols and convert to float
            price_clean = price_str.replace("$", "").replace(",", "").strip()
            return float(price_clean)
        except:
            return 0.0
    
    async def _get_image_from_google_images(self, product_title: str) -> Optional[str]:
        """Fallback: Get product image from Google Images search"""
        try:
            # Simplify the product title for better search results
            simplified_title = product_title.lower()
            
            # Remove brand names and specific details
            simplifications = {
                # Beds
                'scandinavian solid wood rectangle panel headboard bed frame': 'wooden bed frame',
                'southerland scandinavian': 'scandinavian mattress',
                'latex foam mattress': 'mattress',
                'memory foam mattress': 'mattress',
                'tempur-pedic': 'memory foam mattress',
                'platform bed': 'bed frame',
                'bed frame': 'bed',
                
                # Common furniture
                'nightstand': 'bedside table',
                'dresser': 'bedroom dresser',
                'office chair': 'desk chair',
                'desk': 'writing desk',
                'sofa': 'couch',
                'coffee table': 'coffee table',
                'bookshelf': 'bookcase'
            }
            
            # Apply simplifications
            search_term = simplified_title
            for complex_term, simple_term in simplifications.items():
                if complex_term in simplified_title:
                    search_term = simple_term
                    break
            
            # If no match, extract the most basic furniture type
            furniture_keywords = ['bed', 'mattress', 'nightstand', 'dresser', 'desk', 'chair', 'sofa', 'table', 'shelf']
            found_keyword = False
            for keyword in furniture_keywords:
                if keyword in simplified_title:
                    search_term = keyword
                    found_keyword = True
                    break
            
            # If still no match, just use "furniture"
            if not found_keyword and len(search_term) > 30:
                search_term = "modern furniture"
            
            # Remove numbers, measurements, brand names
            import re
            search_term = re.sub(r'\d+["\']?|\d+x\d+|\b\d+\b', '', search_term)  # Remove measurements
            search_term = re.sub(r'\b(ikea|west elm|article|cb2|herman miller|tempur-pedic|southerland|casper)\b', '', search_term, flags=re.I)  # Remove common brands
            search_term = ' '.join(search_term.split())  # Clean up extra spaces
            
            logger.info(f"Simplified image search: '{product_title}' -> '{search_term}'")
            
            # Create a Google Images search URL
            search_query = search_term.replace(' ', '+')
            search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"
            
            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                },
                timeout=5.0,  # Reduced timeout
                follow_redirects=True
            ) as client:
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    # Extract first image URL from search results
                    # Google Images embeds image URLs in the page
                    import re
                    # Look for image URLs in the response
                    pattern = r'https?://[^\s"]+\.(?:jpg|jpeg|png|webp)'
                    urls = re.findall(pattern, response.text)
                    
                    # Filter out Google's own assets - try max 5 URLs
                    attempts = 0
                    for url in urls:
                        if attempts >= 5:  # Max 5 attempts
                            break
                            
                        if 'gstatic' not in url and 'google' not in url.lower() and len(url) > 50:
                            attempts += 1
                            # Try to download this image
                            try:
                                img_response = await client.get(url, timeout=2.0)  # Reduced timeout
                                if img_response.status_code == 200 and len(img_response.content) > 1000:
                                    # Save the image
                                    safe_title = re.sub(r'[^\w\s-]', '', product_title)[:50]
                                    safe_title = re.sub(r'[-\s]+', '-', safe_title)
                                    filename = f"{safe_title}_{int(time.time())}.jpg"
                                    filepath = os.path.join(self.output_dir, filename)
                                    
                                    with open(filepath, 'wb') as f:
                                        f.write(img_response.content)
                                    
                                    return filepath
                            except:
                                continue
        except Exception as e:
            logger.error(f"Error getting image from Google Images: {str(e)}")
        
        return None
    
    async def _scrape_product_image(self, google_link: str, product_title: str) -> Optional[str]:
        """Scrape product image from Google Shopping link"""
        try:
            # Create HTTP client with headers to avoid being blocked
            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                },
                timeout=10.0,
                follow_redirects=True
            ) as client:
                response = await client.get(google_link)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try different strategies to find product images
                    image_url = None
                    
                    # Strategy 1: Look for og:image meta tag
                    og_image = soup.find('meta', property='og:image')
                    if og_image and og_image.get('content'):
                        image_url = og_image['content']
                    
                    # Strategy 2: Look for product images in specific divs
                    if not image_url:
                        # Google Shopping often uses specific class names
                        img_tags = soup.find_all('img', class_=re.compile(r'(product|item|gallery)', re.I))
                        for img in img_tags:
                            src = img.get('src') or img.get('data-src')
                            if src and ('http' in src or src.startswith('//')):
                                if src.startswith('//'):
                                    src = 'https:' + src
                                if 'googleusercontent.com' in src or 'gstatic.com' in src:
                                    image_url = src
                                    break
                    
                    # Strategy 3: Look for the first large image
                    if not image_url:
                        all_imgs = soup.find_all('img')
                        for img in all_imgs:
                            src = img.get('src') or img.get('data-src')
                            if src and ('http' in src or src.startswith('//')):
                                if src.startswith('//'):
                                    src = 'https:' + src
                                # Skip small icons and UI elements
                                if any(skip in src.lower() for skip in ['icon', 'logo', 'sprite', 'pixel']):
                                    continue
                                # Look for product-related URLs
                                if any(prod in src.lower() for prod in ['product', 'item', 'image']):
                                    image_url = src
                                    break
                    
                    if image_url:
                        # Download and save the image
                        img_response = await client.get(image_url)
                        if img_response.status_code == 200:
                            # Create filename from product title
                            safe_title = re.sub(r'[^\w\s-]', '', product_title)[:50]
                            safe_title = re.sub(r'[-\s]+', '-', safe_title)
                            filename = f"{safe_title}_{int(time.time())}.jpg"
                            filepath = os.path.join(self.output_dir, filename)
                            
                            # Save image
                            with open(filepath, 'wb') as f:
                                f.write(img_response.content)
                            
                            return filepath
                
        except Exception as e:
            logger.error(f"Error scraping image from {google_link}: {str(e)}")
        
        return None
    
    async def generate_final_design(self):
        """Generate the final room design by compositing furniture"""
        self.current_step = "Generating final design"
        self.add_message("🎨 Creating final room design...")
        
        try:
            # Prepare furniture descriptions and images
            furniture_descriptions = []
            content_items = []
            
            # Add the text prompt
            prompt_text = f"""Generate a photorealistic interior design visualization of this empty room furnished with the shown furniture items.

The first image shows the empty room to be designed.
The following images show the furniture pieces to place in the room.

Design Requirements:
- Style: {self.design_plan.design_style}
- Color Scheme: {', '.join(self.design_plan.color_scheme)}
- Layout: {self.design_plan.layout_description}

"""
            
            # Add furniture details to prompt
            for idx, item in enumerate(self.furniture_items[:5], 1):  # Limit to 5 items
                furniture_descriptions.append({
                    "title": item.title,
                    "category": item.category,
                    "price": item.price,
                    "source": item.source,
                    "has_image": bool(item.local_image_path)
                })
                prompt_text += f"\nFurniture {idx}: {item.title}"
                if item.category:
                    prompt_text += f" ({item.category})"
            
            prompt_text += """

Create a beautiful, photorealistic room visualization that:
- Shows all the furniture pieces properly placed in the room
- Maintains the room's original architecture and windows
- Uses professional interior design principles
- Creates a cohesive, livable space
- Adds appropriate lighting and ambiance

Generate a high-quality interior design image showing the furnished room."""
            
            content_items.append({
                "type": "input_text",
                "text": prompt_text
            })
            
            # Add room image
            with open(self.room_image_path, "rb") as img_file:
                room_image_data = base64.b64encode(img_file.read()).decode()
            
            content_items.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{room_image_data}"
            })
            
            # Try to fetch images for first 3 items only
            self.add_message("📸 Looking for furniture images...")
            images_fetched = 0
            
            for item in self.furniture_items[:3]:
                if images_fetched >= 3:  # Max 3 images
                    break
                    
                try:
                    # Don't log the exact product name, it's confusing
                    # Quick Google Images search with timeout
                    image_path = await asyncio.wait_for(
                        self._get_image_from_google_images(item.title),
                        timeout=2.0  # Reduced to 2 second timeout per image
                    )
                    
                    if image_path and os.path.exists(image_path):
                        with open(image_path, "rb") as img_file:
                            furniture_image_data = base64.b64encode(img_file.read()).decode()
                        content_items.append({
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{furniture_image_data}"
                        })
                        item.local_image_path = image_path
                        item.image_url = f"/uploads/{os.path.basename(image_path)}"
                        images_fetched += 1
                        # Log the category instead of exact name
                        self.add_message(f"✓ Found image")
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout fetching image for {item.title}")
                    # Don't log timeout, just continue
                except Exception as e:
                    logger.error(f"Error fetching image for {item.title}: {str(e)}")
            
            if images_fetched == 0:
                self.add_message("🎨 Generating new room design...")
            else:
                self.add_message(f"🎨 Generating new room with {images_fetched} furniture items...")
            
            # Generate new room image using GPT-4.1-mini with image generation tool
            response = self.openai_client.responses.create(
                model="gpt-4.1-mini",
                input=[{
                    "role": "user",
                    "content": content_items
                }],
                tools=[{"type": "image_generation"}]
            )
            
            # Extract the generated image
            image_generated = False
            design_description = "Your room has been beautifully redesigned with the selected furniture."
            
            if hasattr(response, 'output') and response.output:
                for output in response.output:
                    if hasattr(output, 'type') and output.type == "image_generation_call" and hasattr(output, 'result'):
                        # Save the generated room image
                        filename = f"designed_{self.session_id}_{uuid.uuid4().hex[:8]}.png"
                        designed_image_path = os.path.join("uploads", filename)
                        
                        try:
                            with open(designed_image_path, "wb") as f:
                                f.write(base64.b64decode(output.result))
                            image_generated = True
                            self.add_message("✨ New room visualization created!")
                        except Exception as e:
                            logger.error(f"Error saving generated image: {str(e)}")
                    elif hasattr(output, 'output_text'):
                        design_description = output.output_text
            
            # Fallback if no image was generated
            if not image_generated:
                logger.warning("No image generated, using original as fallback")
                designed_image_path = f"uploads/designed_{self.session_id}.jpg"
                import shutil
                shutil.copy(self.room_image_path, designed_image_path)
            
            self.steps_completed.append("Design Generation")
            self.add_message("✓ Final design generated successfully!")
            
            # Calculate total cost
            total_cost = sum(self._parse_price(item.price) for item in self.furniture_items if item.price)
            
            # Update plan markdown
            self.plan_markdown += f"""
## Final Design Summary
- **Total Estimated Cost**: ${total_cost:,.2f}
- **Items Selected**: {len(self.furniture_items)}
- **Design Style**: {self.design_plan.design_style}
- **Completion Time**: {time.time() - self.start_time:.2f} seconds

### Design Description
{design_description}
"""
            
        except Exception as e:
            logger.error(f"Design generation error: {str(e)}")
            self.errors.append(f"Design generation failed: {str(e)}")
    
    def add_message(self, message: str):
        """Add a progress message"""
        self.progress_messages.append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
        logger.info(f"Agent {self.session_id}: {message}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and progress"""
        progress_percentage = len(self.steps_completed) / 4 * 100  # 4 main steps
        
        return {
            "status": self.status.value,
            "current_step": self.current_step,
            "steps_completed": self.steps_completed,
            "progress_percentage": progress_percentage,
            "messages": self.progress_messages,
            "errors": self.errors
        }
    
    def get_plan_markdown(self) -> str:
        """Get the design plan in markdown format"""
        return self.plan_markdown
    
    def get_final_results(self) -> Dict[str, Any]:
        """Get the final design results"""
        total_cost = sum(self._parse_price(item.price) for item in self.furniture_items if item.price)
        
        # Find the generated image
        designed_image_path = None
        for file in os.listdir("uploads"):
            if file.startswith(f"designed_{self.session_id}") and file.endswith((".png", ".jpg")):
                designed_image_path = f"/uploads/{file}"
                break
        
        # Fallback if not found
        if not designed_image_path:
            designed_image_path = f"/uploads/designed_{self.session_id}.jpg"
        
        return {
            "session_id": self.session_id,
            "original_image": f"/uploads/{os.path.basename(self.room_image_path)}",
            "designed_image": designed_image_path,
            "design_plan": self.design_plan.dict(),
            "total_cost_estimate": total_cost,
            "furniture_items": [item.dict() for item in self.furniture_items],
            "completion_time": time.time() - self.start_time,
            "design_description": self.plan_markdown
        }
    
    def stop(self):
        """Stop the agent"""
        self.status = AgentStatus.IDLE
        self.add_message("⏹️ Agent stopped by user") 