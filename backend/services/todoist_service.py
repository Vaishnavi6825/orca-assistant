import logging
import os
from todoist_api_python.api import TodoistAPI

# Setup logger to match main app
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TodoistService:
    """Handles task creation and management using Todoist API (official library)."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        logger.info(f"🔧 TodoistService initializing - Token provided: {bool(api_token)} (length: {len(api_token) if api_token else 0})")
        if api_token and api_token.strip():
            try:
                self.api = TodoistAPI(api_token)
                logger.info("✅ TodoistAPI client successfully initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize TodoistAPI client: {e}")
                self.api = None
        else:
            logger.warning("⚠️ No API token provided to TodoistService")
            self.api = None

    def create_task(self, content: str, description: str = "", due_string: str = None, project_id: str = None) -> dict:
        """
        Create a task in Todoist using the official API.

        Args:
            content: Task title/name
            description: Optional task description
            due_string: Optional due date (e.g., "today", "tomorrow", "next Monday")
            project_id: Optional project ID (defaults to Inbox if None)

        Returns:
            Dictionary with task info including task ID
        """
        if not self.api_token:
            logger.error("❌ Todoist API token is empty or None")
            return {"success": False, "error": "API token not configured"}
        
        if not self.api:
            logger.error("❌ Todoist API client is not initialized")
            return {"success": False, "error": "API client not initialized"}

        try:
            logger.info(f"📝 Creating task in Todoist: '{content}' (due: {due_string or 'none'})")
            
            # Create task with explicit project_id (defaults to inbox if not provided)
            # Use "Inbox" as fallback to ensure task goes to inbox
            kwargs = {"content": content}
            if due_string:
                kwargs["due_string"] = due_string
            if project_id:
                kwargs["project_id"] = project_id
            
            task = self.api.add_task(**kwargs)
            logger.info(f"✅ Created Todoist task: '{content}' (ID: {task.id})")
            logger.debug(f"📋 Task object details: {vars(task) if hasattr(task, '__dict__') else task}")
            
            # Safely extract URL
            task_url = task.url if hasattr(task, 'url') else f"https://app.todoist.com/app/inbox"
            
            result = {
                "success": True,
                "task_id": task.id,
                "content": content,
                "url": task_url
            }
            logger.debug(f"📋 Task creation result: {result}")
            return result
        except AttributeError as e:
            logger.error(f"❌ Todoist API returned invalid response (AttributeError): {e}")
            return {"success": False, "error": f"Invalid API response: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Todoist task creation failed: {type(e).__name__}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def create_multiple_tasks(self, tasks: list) -> dict:
        """
        Create multiple tasks in Todoist.

        Args:
            tasks: List of dicts with 'content' and optional 'due_string' keys

        Returns:
            Dictionary with list of created tasks and summary
        """
        if not self.api_token or not self.api:
            logger.error("Todoist API token is not configured.")
            return {"success": False, "error": "API token not configured"}

        created = []
        failed = []

        for task_data in tasks:
            try:
                result = self.create_task(
                    content=task_data.get("content", ""),
                    due_string=task_data.get("due_string")
                )
                if result.get("success"):
                    created.append(result)
                else:
                    failed.append({"content": task_data.get("content"), "error": result.get("error")})
            except Exception as e:
                logger.warning(f"Failed to create task '{task_data.get('content', 'Unknown')}': {e}")
                failed.append({"content": task_data.get("content"), "error": str(e)})

        return {
            "success": True,
            "created_count": len(created),
            "failed_count": len(failed),
            "created_tasks": created,
            "failed_tasks": failed if failed else None
        }

    def get_tasks(self) -> list:
        """
        Retrieve all tasks from Todoist.
        """
        if not self.api_token or not self.api:
            logger.error("Todoist API token is not configured.")
            return []

        try:
            tasks = self.api.get_tasks()
            logger.info(f"✅ Retrieved {len(tasks)} tasks from Todoist")
            return tasks
        except Exception as e:
            logger.error(f"❌ Failed to retrieve Todoist tasks: {e}")
            return []

    def format_task_summary(self, task_count: int = 5) -> str:
        """
        Get a formatted summary of recent tasks for the agent to reference.
        """
        try:
            tasks = self.get_tasks()
            if not tasks:
                return "No tasks found in Todoist."

            recent = tasks[:task_count]
            summary_lines = ["📝 Your recent tasks:"]
            for i, task in enumerate(recent, 1):
                status = "✓" if task.is_completed else "○"
                summary_lines.append(f"  {status} {task.content}")

            return "\n".join(summary_lines)
        except Exception as e:
            logger.error(f"Error formatting task summary: {e}")
            return "Could not retrieve task summary from Todoist."
