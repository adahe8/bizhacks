# backend/external_apis/mock_media.py
"""Mock media generation for testing"""
import random
from typing import Dict, Any

class MockMediaGenerator:
    """Generate mock media content for campaigns"""
    
    @staticmethod
    def generate_facebook_content(theme: str, product: str) -> Dict[str, Any]:
        """Generate mock Facebook post content"""
        templates = [
            f"🎉 Discover the amazing {product}! {theme} 🎉\n\nLimited time offer!",
            f"Transform your life with {product} ✨\n\n{theme}\n\nShop now →",
            f"Why everyone's talking about {product} 🔥\n\n{theme}\n\nLearn more!"
        ]
        
        return {
            "message": random.choice(templates),
            "link": f"https://example.com/{product.lower().replace(' ', '-')}",
            "call_to_action": {
                "type": random.choice(["SHOP_NOW", "LEARN_MORE", "SIGN_UP"]),
                "value": {"link": f"https://example.com/{product.lower().replace(' ', '-')}"}
            },
            "image_url": f"https://via.placeholder.com/1200x630?text={product.replace(' ', '+')}"
        }
    
    @staticmethod
    def generate_email_content(theme: str, product: str) -> Dict[str, Any]:
        """Generate mock email content"""
        subjects = [
            f"Don't miss out on {product}!",
            f"Your exclusive {product} offer inside",
            f"{product}: {theme}",
            f"Limited time: Save on {product}"
        ]
        
        return {
            "subject": random.choice(subjects),
            "preview_text": f"{theme} - Shop {product} today!",
            "html_content": f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h1>{product}</h1>
                    <h2>{theme}</h2>
                    <p>Experience the difference with our premium {product}.</p>
                    <a href="https://example.com" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Shop Now</a>
                </body>
            </html>
            """,
            "plain_content": f"{product}\n\n{theme}\n\nShop now at https://example.com"
        }
    
    @staticmethod
    def generate_google_ads_content(theme: str, product: str) -> Dict[str, Any]:
        """Generate mock Google Ads content"""
        headlines = [
            f"{product} - Official Site",
            f"Best {product} Deals",
            f"Save on {product} Today",
            f"{product} | {theme}"
        ]
        
        descriptions = [
            f"Discover our premium {product}. {theme}. Free shipping on orders over $50.",
            f"Shop {product} now. {theme}. Limited time offer!",
            f"Get the best {product} deals. {theme}. Order today!"
        ]
        
        return {
            "headline1": random.choice(headlines)[:30],  # Google Ads limit
            "headline2": f"{theme}"[:30],
            "headline3": "Free Shipping"[:30],
            "description1": random.choice(descriptions)[:90],
            "description2": "100% Satisfaction Guaranteed. Shop with confidence."[:90],
            "final_url": f"https://example.com/{product.lower().replace(' ', '-')}",
            "path1": product.lower().replace(' ', '-')[:15],
            "path2": "deals"[:15]
        }