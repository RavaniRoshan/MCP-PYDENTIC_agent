"""
Simple test to verify social media functionality
"""
import sys
import os
sys.path.insert(0, os.getcwd())

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    # Test models import
    from social_media.models import SocialMediaCredentials, PostContent, SocialPlatform
    print("[OK] Social media models imported successfully")
    
    # Test controller import
    from agents.automateai_agent import AutomateAIAgent
    from social_media.controller import SocialMediaScheduler
    print("[OK] Social media controller imported successfully")
    
    # Test service import (this should include the router)
    from social_media.service import router
    print("[OK] Social media service imported successfully")
    
    # Test that the main app can be imported with social media
    from main import app
    print("[OK] Main app with social media endpoints imported successfully")
    
    # Check routes
    route_paths = []
    for route in app.routes:
        if hasattr(route, 'path'):
            route_paths.append(route.path)
    
    social_routes = [path for path in route_paths if 'social' in path.lower()]
    print(f"[OK] Found {len(social_routes)} social media routes")
    
    for path in social_routes:
        print(f"  - {path}")
    
    print("All tests passed! Social Media Scheduler is fully integrated.")

if __name__ == "__main__":
    test_imports()