from google.genai import types


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


async def process_agent_response(event):
    """Process and display agent response events."""
    # Debug: Print all parts to understand what's happening
    if event.content and event.content.parts:
        for i, part in enumerate(event.content.parts):
            part_type = type(part).__name__
            print(f"  Debug: Part {i}: {part_type}")

            if hasattr(part, "function_call") and part.function_call:
                print(f"    Function call: {part.function_call.name}")
                has_specific_part = True
            elif hasattr(part, "executable_code") and part.executable_code:
                print(f"    Executable code: {part.executable_code.code}")
                has_specific_part = True
            elif hasattr(part, "code_execution_result") and part.code_execution_result:
                print(f"    Code execution result: {part.code_execution_result.outcome}")
                has_specific_part = True
            elif hasattr(part, "tool_response") and part.tool_response:
                print(f"    Tool response: {part.tool_response.output}")
                has_specific_part = True
            elif hasattr(part, "text") and part.text:
                print(f"    Text: {part.text[:100]}...")
            else:
                print(
                    f"    Unknown part type with attributes: {[attr for attr in dir(part) if not attr.startswith('_')]}")

    # Check for specific parts first
    has_specific_part = False
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "executable_code") and part.executable_code:
                # Access the actual code string via .code
                print(
                    f"  Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```"
                )
                has_specific_part = True
            elif hasattr(part, "code_execution_result") and part.code_execution_result:
                # Access outcome and output correctly
                print(
                    f"  Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}"
                )
                has_specific_part = True
            elif hasattr(part, "tool_response") and part.tool_response:
                # Print tool response information (optional debug info)
                print(f"  Tool Response: {part.tool_response.output}")
                has_specific_part = True

    # Check for final response after specific parts
    final_response = None
    if event.is_final_response():
        if (
                event.content
                and event.content.parts
                and hasattr(event.content.parts[0], "text")
                and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Use colors and formatting to make the final response stand out
            print(
                f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╔══ AGENT RESPONSE ═════════════════════════════════════════{Colors.RESET}"
            )
            print(f"{Colors.CYAN}{Colors.BOLD}{final_response}{Colors.RESET}")
            print(
                f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╚═════════════════════════════════════════════════════════════{Colors.RESET}\n"
            )
        else:
            print(
                f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}==> Final Agent Response: [No text content in final event]{Colors.RESET}\n"
            )

    return final_response


async def call_agent_async(runner, user_id, session_id, query):
    """Call the agent asynchronously with the user's query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(
        f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}--- Running Query: {query} ---{Colors.RESET}"
    )
    final_response_text = None

    try:
        async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=content
        ):
            # Process each event and get the final response if available
            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"Error during agent call: {e}")

    return final_response_text