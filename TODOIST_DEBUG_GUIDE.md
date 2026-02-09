# 🐛 Todoist Integration - Debugging Guide

## Issues Found and Fixed

### ✅ Issue 1: Import Statement Syntax Error
**Problem:** Line 11 had `from.services.todoist_service` (missing space)
**Fix:** Changed to `from .services.todoist_service`

### ✅ Issue 2: Improved Error Logging
**Added:** Detailed logging at every step to track where the process fails:
- API key validation on initialization
- Todoist service availability check
- Task detection verification
- API call attempt and response
- Error with full traceback

### ✅ Issue 3: Better Response Validation
**Enhanced:** TodoistService now:
- Validates API token is not empty
- Checks API client initialization
- Validates API response attributes
- Returns detailed error messages

---

## 🔍 How to Debug - Complete Checklist

### Step 1: Test Todoist API Directly
```bash
cd c:\Users\kirut\voice-agent
python test_todoist_debug.py YOUR_TODOIST_API_TOKEN
```

This will verify:
- ✅ todoist_api_python package is installed
- ✅ API token format is valid
- ✅ API connection works
- ✅ Task creation works
- ✅ Task retrieval works

### Step 2: Check API Key Format
Todoist API tokens should:
- Be 40+ characters long
- Start with specific patterns (usually alphanumeric)
- NOT be empty or contain only spaces

Look for in logs:
```
🔧 TodoistService initializing - Token provided: True (length: XX)
```

### Step 3: Monitor Logs During Voice Interaction

**When you speak to the bot, check for these log messages:**

1. **API Keys Received:**
   ```
   ✅ API Keys received - Murf: True, Assembly: True, Gemini: True, Todoist: True
   ```
   If `Todoist: False` - the token wasn't sent by frontend!

2. **User Text Received:**
   ```
   👤 User: create a task to buy groceries
   ```

3. **Task Detection:**
   ```
   ✅ Detected task creation request; preparing to create Todoist task.
   📝 Extracted task content: 'buy groceries'
   ```

4. **Task Creation Attempt:**
   ```
   📝 Attempting to create task in Todoist: 'buy groceries'
   ```

5. **Success or Failure:**
   - Success: `✅ Task successfully created in Todoist: 'buy groceries' (ID: 12345)`
   - Failure: `❌ Todoist API returned error: YOUR_ERROR_MESSAGE`

---

## 🚨 Common Issues & Solutions

### Issue: "Todoist: False" in API keys log

**Cause:** Frontend is not sending the Todoist API token

**Solution:**
1. Open the web interface
2. Make sure you're entering your Todoist API token in the form
3. Check browser developer console (F12) for JavaScript errors
4. Verify the key field name matches `x-todoist-key`

**Frontend should send:**
```json
{
  "type": "api_keys",
  "keys": {
    "x-todoist-key": "your_actual_token_here",
    ...other keys...
  }
}
```

---

### Issue: "API token not configured" error

**Causes:**
1. Token is being set to empty string `""`
2. Token contains only whitespace
3. TodoistService not initialized

**Solutions:**
- Verify token value in frontend
- Check for extra spaces or newlines
- Run the test script to verify token format

---

### Issue: "API client not initialized" error

**Cause:** TodoistAPI constructor failed with your token

**Solution:**
1. Run: `python test_todoist_debug.py YOUR_TOKEN`
2. If test fails, your token is invalid
3. Get a new token from: https://todoist.com/app/settings/integrations/developer

---

### Issue: Task keywords not detected

**Keywords that trigger task creation:**
- "create task"
- "add task"
- "todo"
- "reminder"
- "remember to"
- "add to my list"
- "make a note"

**Example phrases that WILL trigger:**
- "Create a task to buy milk"
- "Add task: call mom"
- "I need a reminder for tomorrow"
- "Make a note about the meeting"

**Example phrases that WON'T trigger:**
- "I have a task" (no keyword match)
- "What are my tasks" (no keyword match)

---

## 🔧 Manual Testing Steps

### Step 1: Start the server with verbose logging
```bash
cd c:\Users\kirut\voice-agent\backend
python main.py
```

Watch the console for startup logs.

### Step 2: Open web interface
Visit: `http://localhost:8000`

### Step 3: Enter API keys in the form
Make sure to enter:
- ✅ Todoist API token (required for tasks)
- ✅ All other required keys (Murf, Assembly, Gemini)

### Step 4: Test with voice command
Say: **"Create a task to test the integration"**

### Step 5: Check logs in console
Look for the sequence of log messages listed in Step 3 above.

---

## 📊 Expected Log Flow for Successful Task Creation

```
👤 User: create a task to buy groceries
✅ Detected task creation request; preparing to create Todoist task.
📝 Extracted task content: 'buy groceries'
📝 Attempting to create task in Todoist: 'buy groceries'
✅ Created Todoist task: 'buy groceries' (ID: 12345678)
✅ Task successfully created in Todoist: 'buy groceries' (ID: 12345678)
✅ Task creation result: {'success': True, 'task_id': 12345678, ...}
🤖 AI Chunk: Task created successfully!
```

---

## 💡 Tips for Diagnosing Issues

1. **Enable Debug Logging:**
   Add to `main.py` after logger setup:
   ```python
   logging.getLogger().setLevel(logging.DEBUG)
   ```

2. **Test Todoist Service in Isolation:**
   ```python
   from backend.services.todoist_service import TodoistService
   service = TodoistService("your_token_here")
   result = service.create_task("Test task")
   print(result)
   ```

3. **Check Network Tab in Browser:**
   - F12 → Network tab
   - Filter for WebSocket messages
   - Look for `api_keys` message being sent
   - Verify `x-todoist-key` is present and not empty

4. **Verify todoist-python-api Installation:**
   ```bash
   pip list | grep todoist
   ```
   Should show: `todoist-python-api`

5. **Get Your Real Todoist Token:**
   - Go to: https://todoist.com/app/settings/integrations/developer
   - Scroll down to "API token"
   - Copy the 40+ character token
   - **Never share this token!**

---

## 🎯 Next Steps

1. Run the debug script: `python test_todoist_debug.py YOUR_TOKEN`
2. Check which test fails
3. Follow the solution for that specific issue
4. Monitor logs when speaking to bot
5. Report any errors that appear in logs

Good luck! 🚀
