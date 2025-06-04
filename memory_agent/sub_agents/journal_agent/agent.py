from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
import datetime
from typing import Optional


def add_entry(entry: str, tool_context: ToolContext, mood: Optional[str], tags: Optional[str]) -> dict:
    """Add a new entry to the user's journal list with metadata.

    Args:
        entry: The entry text to add
        tool_context: Context for accessing and updating session state
        mood: Optional mood indicator (happy, sad, excited, stressed, neutral, etc.)
        tags: Optional comma-separated tags for categorization

    Returns:
        A confirmation message
    """
    print(f"--- Tool: add_entry called for '{entry}' ---")

    # Get current entries from state
    entries = tool_context.state.get("entries", [])

    # Create entry with metadata
    entry_data = {
        "id": len(entries) + 1,  # Simple incrementing ID
        "text": entry,
        "timestamp": datetime.datetime.now().isoformat(),
        "mood": mood.lower() if mood else None,
        "tags": [tag.strip().lower() for tag in tags.split(",")] if tags else []
    }

    # Add the new entry
    entries.append(entry_data)

    # Update state with the new list of entries
    tool_context.state["entries"] = entries

    # Format response message
    metadata_parts = []
    if mood:
        metadata_parts.append(f"mood: {mood}")
    if tags:
        metadata_parts.append(f"tags: {tags}")

    metadata_str = f" ({', '.join(metadata_parts)})" if metadata_parts else ""

    return {
        "action": "add_entry",
        "entry": entry_data,
        "message": f"Added entry: {entry}{metadata_str}",
    }


def view_entries(tool_context: ToolContext, filter_mood: Optional[str],
                 filter_tags: Optional[str], recent_days: Optional[int]) -> dict:
    """View entries with optional filtering.

    Args:
        tool_context: Context for accessing session state
        filter_mood: Optional mood to filter by
        filter_tags: Optional comma-separated tags to filter by
        recent_days: Optional number of recent days to show

    Returns:
        The filtered list of entries
    """
    # Handle None values inside the function
    if recent_days is None:
        recent_days = 30
    if filter_tags is None:
        filter_tags = ""
    if filter_mood is None:
        filter_mood = ""

    print("--- Tool: view_entries called ---")

    # Get entries from state
    all_entries = tool_context.state.get("entries", [])

    # Handle legacy entries (convert strings to objects if needed)
    normalized_entries = []
    for i, entry in enumerate(all_entries):
        if isinstance(entry, str):
            # Convert legacy string entries to new format
            normalized_entries.append({
                "id": i + 1,
                "text": entry,
                "timestamp": datetime.datetime.now().isoformat(),  # Use current time as fallback
                "mood": None,
                "tags": []
            })
        else:
            normalized_entries.append(entry)

    # Update state with normalized entries if we had to convert any
    if len(normalized_entries) != len([e for e in all_entries if isinstance(e, dict)]):
        tool_context.state["entries"] = normalized_entries

    filtered_entries = normalized_entries.copy()

    # Apply filters
    if filter_mood:
        filtered_entries = [e for e in filtered_entries if e.get("mood") == filter_mood.lower()]

    if filter_tags:
        filter_tag_list = [tag.strip().lower() for tag in filter_tags.split(",")]
        filtered_entries = [e for e in filtered_entries
                            if any(tag in e.get("tags", []) for tag in filter_tag_list)]

    if recent_days:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=recent_days)
        filtered_entries = [e for e in filtered_entries
                            if datetime.datetime.fromisoformat(e["timestamp"]) >= cutoff_date]

    return {
        "action": "view_entries",
        "entries": filtered_entries,
        "count": len(filtered_entries),
        "total_count": len(normalized_entries),
        "filters_applied": {
            "mood": filter_mood,
            "tags": filter_tags,
            "recent_days": recent_days
        }
    }


def search_entries(query: str, tool_context: ToolContext) -> dict:
    """Search entries by text content.

    Args:
        query: Search query to match against entry text
        tool_context: Context for accessing session state

    Returns:
        Entries matching the search query
    """
    print(f"--- Tool: search_entries called for '{query}' ---")

    # Get entries from state
    all_entries = tool_context.state.get("entries", [])

    # Normalize entries (handle legacy format)
    normalized_entries = []
    for i, entry in enumerate(all_entries):
        if isinstance(entry, str):
            normalized_entries.append({
                "id": i + 1,
                "text": entry,
                "timestamp": datetime.datetime.now().isoformat(),
                "mood": None,
                "tags": []
            })
        else:
            normalized_entries.append(entry)

    # Search in entry text (case-insensitive)
    matching_entries = [
        entry for entry in normalized_entries
        if query.lower() in entry["text"].lower()
    ]

    return {
        "action": "search_entries",
        "query": query,
        "entries": matching_entries,
        "count": len(matching_entries)
    }


# Create the journal management sub-agent
journal_agent = Agent(
    name="journal_agent",
    model="gemini-2.0-flash",
    description="A specialized agent for managing journal entries with rich metadata support",
    instruction="""
    You are the Journal Agent, responsible for all entry management tasks in the digital journal system.
    You handle adding, viewing, searching, and organizing journal entries.

    The user's information is stored in state:
    - User's name: {user_name}
    - Entries: {entries} (with metadata: timestamp, mood, tags)

    AVAILABLE TOOLS:
    1. add_entry(entry, mood, tags) - Store new journal entries with optional metadata
    2. view_entries(filter_mood, filter_tags, recent_days) - View/filter entries
    3. search_entries(query) - Search entries by text content

    CORE RESPONSIBILITIES:

    **Adding Entries with Smart Metadata Detection:**
    - Extract mood indicators from natural language: "I'm feeling great today" → mood="happy"
    - Detect topic tags from content: "work meeting went well" → tags="work"
    - Common moods: happy, sad, excited, stressed, anxious, grateful, frustrated, peaceful, energetic, tired
    - Auto-suggest tags based on content: work, family, health, travel, food, friends, goals, etc.
    - Only remove explicit meta-commentary like "I want to add an entry about" or "Please record that"
    - Preserve all actual content and emotional expressions exactly as written
    - DO NOT add context or combine with previous entries

    **Examples:**
    - "I'm so excited about my promotion!" → add_entry("Got a promotion!", "excited", "work,career")
    - "Had a stressful day dealing with the kids" → add_entry("Stressful day with the kids", "stressed", "family,parenting")
    - "Grateful for my morning coffee ritual" → add_entry("Morning coffee ritual", "grateful", "routine,self-care")

    **Viewing and Filtering:**
    - "Show me happy entries" → view_entries(None, "happy", None, None)
    - "What did I write about work?" → view_entries(None, None, "work", None)
    - "Show me this week's entries" → view_entries(None, None, None, 7)
    - "Recent stressed entries" → view_entries(None, "stressed", None, 30)

    **Searching:**
    - "Find entries about coffee" → search_entries("coffee")
    - Use search for specific keywords when filters aren't enough

    **Entry Display Format:**
    When showing entries, format like:
    📅 [Date] 😊 [Mood] 🏷️ [tags]
    [Entry text]

    **Smart Content Processing:**
    - Always look for emotional indicators in the text to suggest mood
    - Identify key topics/themes for tagging
    - Preserve authentic voice while removing meta-commentary
    - Handle temporal references appropriately
    
    **Delegation**
    - For summaries, analysis, or insights: "That's a job for the Summarizer Agent. Let me connect you..."
    - For entry management only: proceed with your tools
    - Stay in your lane - you're the entry manager, not the analyst
    
    **ENTRY DETECTION:**
    - ANY user input describing an event, activity, or thought is a journal entry
    - Examples that should trigger add_entry():
      * "finished the Classification by KNN course"
      * "had coffee this morning"
      * "feeling stressed about work"
      * "great day at the beach"
    - Only use analysis tools if explicitly asked: "analyze my entries" or "summarize my day"
    - Default action for descriptive statements: add_entry()
    
    **NEVER analyze unless explicitly requested with words like:**
    - "analyze", "summarize", "review", "what patterns", "insights"

    You are focused solely on entry management. For analysis, summaries, or insights,
    that would be handled by the Summarizer Agent. Stay focused on your core mission:
    making journal entry management intuitive and powerful.
    """,
    tools=[
        add_entry,
        view_entries,
        search_entries,
    ],
)