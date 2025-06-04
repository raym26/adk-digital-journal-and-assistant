import asyncio

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from memory_agent.agent import memory_agent  # Import the manager agent
from utils import call_agent_async
import os
load_dotenv()
# Debug: Print environment loading
print("=== ENVIRONMENT DEBUG ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

# Check if .env file exists
if os.path.exists('.env'):
    print("✅ .env file found")
    with open('.env', 'r') as f:
        content = f.read()
        print(f".env content preview: {content[:50]}...")
else:
    print("❌ .env file NOT found")

# Check if API key is loaded
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print(f"✅ API key loaded: {api_key[:10]}...{api_key[-4:]}")
else:
    print("❌ API key not found in environment")
    print("Available env vars:", [k for k in os.environ.keys() if 'GOOGLE' in k])

print("========================")



# ===== PART 1: Initialize Persistent Session Service =====
# Using SQLite database for persistent storage
db_url = "sqlite:///./my_daily_journal_data.db"
session_service = DatabaseSessionService(db_url=db_url)


# ===== PART 2: Define Initial State =====utils.py
# This will only be used when creating a new session
initial_state = {
    "user_name": "Raymond Zialcita",
    "entries": [],
}


async def main_async():
    # Setup constants
    APP_NAME = "Journal Manager System"
    USER_ID = "rz"

    # ===== PART 3: Session Management - Find or Create =====
    # Check for existing sessions for this user
    existing_sessions = session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    # If there's an existing session, use it, otherwise create a new one
    if existing_sessions and len(existing_sessions.sessions) > 0:
        # Use the most recent session
        SESSION_ID = existing_sessions.sessions[0].id
        print(f"Continuing existing session: {SESSION_ID}")
    else:
        # Create a new session with initial state
        new_session = session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        print(f"Created new session: {SESSION_ID}")

    # ===== PART 4: Manager Agent Runner Setup =====
    # Create a runner with the manager agent (which coordinates sub-agents)
    runner = Runner(
        agent=memory_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # ===== PART 5: Interactive Conversation Loop =====
    print("\nWelcome to the Advanced Journal Management System!")
    print("🤖 Manager Agent: I coordinate journal entry management and analysis")
    print("📝 Journal Agent: Handles adding, viewing, and searching entries")
    print("📊 Summarizer Agent: Creates insights, summaries, and reports")
    print("\nYour journal entries will be remembered across conversations.")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        # Get user input
        user_input = input("You: ")

        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Your data has been saved to the database.")
            break

        # Process the user query through the manager agent
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)


if __name__ == "__main__":
    asyncio.run(main_async())