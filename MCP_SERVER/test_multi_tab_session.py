import asyncio
from core.browser_controller import MockBrowserController
from core.tab_manager import TabManager, TabInfo
from core.session_manager import SessionManager, SessionInfo


async def test_multi_tab_management():
    """
    Tests the multi-tab management functionality.
    """
    print("Testing Multi-Tab Management")
    print("="*40)
    
    # Create a mock browser controller and tab manager
    browser_controller = MockBrowserController()
    tab_manager = TabManager(browser_controller)
    
    print("1. Creating initial tabs")
    
    # Create first tab
    tab1_id = await tab_manager.create_new_tab("https://example.com")
    print(f"   Created tab 1: {tab1_id}")
    
    # Create second tab
    tab2_id = await tab_manager.create_new_tab("https://httpbin.org")
    print(f"   Created tab 2: {tab2_id}")
    
    # Create third tab
    tab3_id = await tab_manager.create_new_tab("https://google.com")
    print(f"   Created tab 3: {tab3_id}")
    
    print("\n2. Checking tab information")
    
    # Check active tab
    active_tab = tab_manager.get_active_tab()
    print(f"   Active tab: {active_tab.tab_id if active_tab else None}")
    
    # Get all tabs
    all_tabs = tab_manager.get_all_tabs()
    print(f"   Total tabs: {len(all_tabs)}")
    for tab in all_tabs:
        print(f"     - {tab.tab_id}: {tab.url} (active: {tab.is_active})")
    
    print("\n3. Switching between tabs")
    
    # Switch to tab 1
    success = await tab_manager.switch_to_tab(tab1_id)
    print(f"   Switched to tab 1: {success}")
    
    # Check active tab again
    active_tab = tab_manager.get_active_tab()
    print(f"   Active tab now: {active_tab.tab_id if active_tab else None}")
    
    # Switch to tab 3
    success = await tab_manager.switch_to_tab(tab3_id)
    print(f"   Switched to tab 3: {success}")
    
    # Check active tab again
    active_tab = tab_manager.get_active_tab()
    print(f"   Active tab now: {active_tab.tab_id if active_tab else None}")
    
    print("\n4. Testing tab operations")
    
    # Navigate in a specific tab
    success = await tab_manager.navigate_in_tab(tab2_id, "https://httpbin.org/json")
    print(f"   Navigated in tab 2: {success}")
    
    # Get state of a specific tab
    tab_state = await tab_manager.get_tab_state(tab1_id)
    print(f"   Tab 1 state retrieved: {tab_state.url if tab_state else 'Failed'}")
    
    print("\n5. Closing tabs")
    
    # Close tab 2
    success = await tab_manager.close_tab(tab2_id)
    print(f"   Closed tab 2: {success}")
    
    # Check remaining tabs
    remaining_tabs = tab_manager.get_all_tabs()
    print(f"   Remaining tabs: {len(remaining_tabs)}")
    for tab in remaining_tabs:
        print(f"     - {tab.tab_id}: {tab.url} (active: {tab.is_active})")
    
    # Close remaining tabs
    await tab_manager.close_tab(tab1_id)
    await tab_manager.close_tab(tab3_id)
    print("   Closed remaining tabs")
    
    print("\nMulti-tab management test completed.")


async def test_multi_session_management():
    """
    Tests the multi-session management functionality.
    """
    print("\nTesting Multi-Session Management")
    print("="*40)
    
    session_manager = SessionManager()
    
    print("1. Creating sessions")
    
    # Create session for user 1
    session1_id = await session_manager.create_session("user_123", "chromium")
    print(f"   Created session 1: {session1_id}")
    
    # Create session for user 2
    session2_id = await session_manager.create_session("user_456", "chromium")
    print(f"   Created session 2: {session2_id}")
    
    # Create another session for user 1
    session3_id = await session_manager.create_session("user_123", "chromium")
    print(f"   Created session 3: {session3_id}")
    
    print("\n2. Checking session information")
    
    # Get all sessions
    all_sessions = session_manager.get_all_sessions()
    print(f"   Total sessions: {len(all_sessions)}")
    for session in all_sessions:
        print(f"     - {session.session_id}: User {session.user_id}, {session.browser_type}")
    
    # Get sessions for user 1
    user1_sessions = session_manager.get_user_sessions("user_123")
    print(f"   Sessions for user 123: {len(user1_sessions)}")
    for session in user1_sessions:
        print(f"     - {session.session_id}")
    
    print("\n3. Getting specific session info")
    
    # Get session info for session 1
    session_info = session_manager.get_session_info(session1_id)
    if session_info:
        print(f"   Session 1 info: {session_info.session_id} for user {session_info.user_id}")
    
    # Get session data
    session_data = session_manager.get_session(session1_id)
    if session_data:
        print(f"   Session 1 controller type: {type(session_data['controller'])}")
        print(f"   Session 1 tab manager tabs: {len(session_data['tab_manager'].tabs)}")
    
    print("\n4. Testing session management")
    
    # Try to get non-existent session
    nonexistent = session_manager.get_session_info("nonexistent")
    print(f"   Non-existent session: {nonexistent}")
    
    print("\n5. Closing sessions")
    
    # Close session 2
    success = await session_manager.delete_session(session2_id)
    print(f"   Closed session 2: {success}")
    
    # Check remaining sessions
    remaining_sessions = session_manager.get_all_sessions()
    print(f"   Remaining sessions: {len(remaining_sessions)}")
    
    # Close remaining sessions
    await session_manager.delete_session(session1_id)
    await session_manager.delete_session(session3_id)
    print("   Closed remaining sessions")
    
    print("\nMulti-session management test completed.")


async def test_combined_functionality():
    """
    Tests combined multi-tab and multi-session functionality.
    """
    print("\nTesting Combined Multi-Tab & Multi-Session Functionality")
    print("="*60)
    
    session_manager = SessionManager()
    
    # Create two sessions
    session1_id = await session_manager.create_session("user_A", "chromium")
    session2_id = await session_manager.create_session("user_B", "chromium")
    
    print(f"Created sessions: {session1_id}, {session2_id}")
    
    # Get tab managers for each session
    session1_data = session_manager.get_session(session1_id)
    session2_data = session_manager.get_session(session2_id)
    
    if session1_data and session2_data:
        tab_manager1 = session1_data['tab_manager']
        tab_manager2 = session2_data['tab_manager']
        
        # Create additional tabs in each session
        tab1_2 = await tab_manager1.create_new_tab("https://session1-tab2.com")
        tab1_3 = await tab_manager1.create_new_tab("https://session1-tab3.com")
        
        tab2_2 = await tab_manager2.create_new_tab("https://session2-tab2.com")
        
        print(f"Session 1 has {len(tab_manager1.tabs)} tabs")
        print(f"Session 2 has {len(tab_manager2.tabs)} tabs")
        
        # Verify that tabs in one session don't affect the other
        session1_tabs = tab_manager1.get_all_tabs()
        session2_tabs = tab_manager2.get_all_tabs()
        
        print(f"Session 1 tab count: {len(session1_tabs)}")
        print(f"Session 2 tab count: {len(session2_tabs)}")
    
    # Clean up
    await session_manager.delete_session(session1_id)
    await session_manager.delete_session(session2_id)
    
    print("Combined functionality test completed.")


async def main():
    await test_multi_tab_management()
    await test_multi_session_management()
    await test_combined_functionality()
    
    print("\n" + "="*60)
    print("All multi-tab and multi-session management tests completed!")


if __name__ == "__main__":
    asyncio.run(main())