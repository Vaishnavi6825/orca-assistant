#!/usr/bin/env python3
"""
Debug script to test Todoist API connectivity and task creation.
Run this script with your Todoist API token to diagnose issues.
"""

import logging
import sys
from todoist_api_python.api import TodoistAPI

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


def test_todoist_connection(api_token: str):
    """Test basic Todoist API connection and task creation."""
    
    print("\n" + "="*60)
    print("🧪 TODOIST API DEBUG TEST")
    print("="*60)
    
    # Validate token format
    if not api_token:
        print("❌ ERROR: No API token provided!")
        return False
    
    if len(api_token.strip()) < 20:
        print(f"⚠️  WARNING: Token seems too short (length: {len(api_token.strip())})")
        print("   Todoist tokens are typically 40+ characters")
    
    print(f"\n📋 Token Details:")
    print(f"   - Token length: {len(api_token)}")
    print(f"   - Token starts with: {api_token[:10]}...")
    print(f"   - Token is stripped: {api_token == api_token.strip()}")
    
    # Test 1: Initialize API client
    print(f"\n[TEST 1] Initializing TodoistAPI client...")
    try:
        api = TodoistAPI(api_token)
        print("✅ TodoistAPI client initialized successfully")
    except Exception as e:
        print(f"❌ FAILED to initialize: {type(e).__name__}: {e}")
        return False
    
    # Test 2: Fetch existing tasks
    print(f"\n[TEST 2] Fetching existing tasks...")
    try:
        tasks = api.get_tasks()
        # `get_tasks()` may return a ResultsPaginator or iterable — convert to list for safe len()/indexing
        try:
            tasks_list = list(tasks)
        except TypeError:
            tasks_list = tasks
        if hasattr(tasks_list, '__len__'):
            count = len(tasks_list)
        else:
            count = sum(1 for _ in tasks_list)
        print(f"✅ Successfully retrieved {count} tasks")
        if count:
            try:
                print(f"   Sample task: {tasks_list[0].content}")
            except Exception:
                print("   Sample task unavailable")
    except Exception as e:
        print(f"❌ FAILED to fetch tasks: {type(e).__name__}: {e}")
        return False
    
    # Test 3: Create a test task
    print(f"\n[TEST 3] Creating a test task...")
    test_content = "🧪 Debug Test Task - " + str(__import__('time').time())
    try:
        task = api.add_task(content=test_content)
        print(f"✅ Task created successfully!")
        print(f"   - Task ID: {task.id}")
        print(f"   - Task Content: {task.content}")
        print(f"   - Task URL: {task.url if hasattr(task, 'url') else 'N/A'}")
        print(f"   - Task Complete: {task.is_completed}")
        
        # Try to retrieve the newly created task
        print(f"\n[TEST 4] Verifying task creation (retrieving all tasks again)...")
        tasks_after = api.get_tasks()
        try:
            tasks_after_list = list(tasks_after)
        except TypeError:
            tasks_after_list = tasks_after
        if hasattr(tasks_after_list, '__len__'):
            total_after = len(tasks_after_list)
        else:
            total_after = sum(1 for _ in tasks_after_list)
        print(f"✅ Total tasks now: {total_after}")
        
        # Cleanup: delete the test task
        print(f"\n[TEST 5] Cleaning up (deleting test task)...")
        try:
            api.delete_task(task.id)
            print(f"✅ Test task deleted successfully")
        except Exception as e:
            print(f"⚠️ Could not delete test task: {e}")
            print(f"   (You may need to manually delete: {test_content})")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED to create task: {type(e).__name__}: {e}")
        print(f"\nDetailed error information:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_todoist_service():
    """Check if todoist_api_python package is installed."""
    print("\n" + "="*60)
    print("📦 DEPENDENCY CHECK")
    print("="*60)
    
    try:
        import todoist_api_python
        print(f"✅ todoist_api_python is installed")
        print(f"   Version: {todoist_api_python.__version__ if hasattr(todoist_api_python, '__version__') else 'Unknown'}")
        return True
    except ImportError:
        print(f"❌ todoist_api_python is NOT installed!")
        print(f"   Install with: pip install todoist-python-api")
        return False


if __name__ == "__main__":
    # Check dependencies
    if not check_todoist_service():
        sys.exit(1)
    
    # Get API token from command line or environment
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        import os
        token = os.getenv("TODOIST_API_TOKEN", "").strip()
    
    if not token:
        print("\n" + "="*60)
        print("❌ NO API TOKEN PROVIDED")
        print("="*60)
        print("\nUsage:")
        print("  python test_todoist_debug.py <YOUR_TODOIST_API_TOKEN>")
        print("\nOr set environment variable:")
        print("  set TODOIST_API_TOKEN=<YOUR_TOKEN>")
        print("  python test_todoist_debug.py")
        sys.exit(1)
    
    # Run tests
    success = test_todoist_connection(token)
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED - Todoist API is working!")
    else:
        print("❌ TESTS FAILED - Check error messages above")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)
