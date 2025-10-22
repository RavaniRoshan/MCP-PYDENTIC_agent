import asyncio
from ai_services.session_manager import SessionManager


async def test_session_manager():
    """
    Tests the secure browser session management system.

    This function initializes a SessionManager, creates several test sessions
    with different permissions and domains, and then tests session validation,
    domain access, and session cleanup.
    """
    print("Testing Session Management System")
    print("="*50)
    
    # Create the session manager
    session_manager = SessionManager()
    
    # Start the session manager
    await session_manager.start()
    
    print("Creating sessions...")
    
    # Create a few test sessions
    sessions_to_create = [
        ("user_1", "full", ["example.com", "google.com"]),
        ("user_2", "write", ["httpbin.org"]),
        ("user_3", "read", [])  # No domain restrictions
    ]
    
    session_ids = []
    for i, (user_id, permission_level, allowed_domains) in enumerate(sessions_to_create):
        print(f"\nCreating session for {user_id} with {permission_level} permissions and domains {allowed_domains}")
        
        session_info = await session_manager.create_session(user_id, permission_level, allowed_domains)
        
        if session_info:
            print(f"  Success: Session ID = {session_info.session_id}")
            print(f"  Created: {session_info.created_at}")
            print(f"  Browser Type: {session_info.browser_type}")
            print(f"  Permission Level: {session_info.permission_level}")
            print(f"  Allowed Domains: {session_info.allowed_domains}")
            
            session_ids.append(session_info.session_id)
        else:
            print("  Failed to create session")
    
    print(f"\nTotal sessions created: {len(session_ids)}")
    
    # Test session validation
    print(f"\nTesting session validation:")
    for i, session_id in enumerate(session_ids):
        session_info = await session_manager.get_session(session_id)
        if session_info:
            print(f"  Session {i+1}: {session_info.user_id} - Active: {session_info.is_active}")
        else:
            print(f"  Session {i+1}: Invalid or expired")
    
    # Test domain access validation
    print(f"\nTesting domain access validation:")
    test_urls = [
        ("https://example.com/page", 0),  # Should work for session 0
        ("https://google.com/search", 0),  # Should work for session 0
        ("https://httpbin.org/get", 1),    # Should work for session 1
        ("https://github.com", 0),         # Should fail for session 0 (not in allowed domains)
        ("https://github.com", 2),         # Should fail for session 2 (read-only)
    ]
    
    for url, session_idx in test_urls:
        if session_idx < len(session_ids):
            session_id = session_ids[session_idx]
            is_allowed = await session_manager.validate_session_access(session_id, url)
            print(f"  Access to {url} for session {session_idx}: {'ALLOWED' if is_allowed else 'DENIED'}")
    
    # Test getting all sessions for a user
    print(f"\nSessions for user_1:")
    user1_sessions = await session_manager.get_user_sessions("user_1")
    for session in user1_sessions:
        print(f"  {session.session_id} - Created: {session.created_at}")
    
    # Test active session count
    print(f"\nActive sessions count: {await session_manager.get_active_session_count()}")
    
    # Close some sessions
    print(f"\nClosing first session...")
    if session_ids:
        success = await session_manager.close_session(session_ids[0])
        print(f"  Close success: {success}")
        
        # Verify it's gone
        session_info = await session_manager.get_session(session_ids[0])
        print(f"  Session still exists: {session_info is not None}")
    
    # Stop the session manager
    await session_manager.stop()
    print("\nSession manager stopped")
    print("Session management system test completed!")


if __name__ == "__main__":
    asyncio.run(test_session_manager())