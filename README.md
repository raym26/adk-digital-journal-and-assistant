# Digital Journal & AI Assistant

A smart journaling system powered by AI agents that automatically extracts mood, tags, and provides intelligent entry management and analysis. As with some of projects, I really built this for me.  First and foremost, I used this project as a way to learn about ADK and multi-agents and secondly, to improve my workflows.  In this case, I wanted a tool to keep track of my activities and then be able
to go back to it days, weeks, months later.  THe pensieve in the Harry Potter books was the inspiration.  Future enhancements might include audio and video perhaps.

## Features

- **Smart Entry Processing**: Automatically detects mood and extracts relevant tags from natural language
- **AI-Powered Analysis**: Get insights, summaries, and patterns from your journal entries
- **Flexible Search & Filtering**: Find entries by mood, tags, date ranges, or text content
- **Multiple AI Agents**: Specialized agents for different tasks (entry management vs. analysis)
- **Persistent Storage**: SQLite database keeps your entries safe and private

## Quick Start

### Prerequisites

- Python 3.8+
- Google AI API key (Gemini)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/raym26/adk-digital-journal-and-assistant.git
   cd adk-digital-journal-and-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file in project root
   echo "GOOGLE_AI_API_KEY=your_api_key_here" > .env
   ```

5. **Run the journal**
   ```bash
   python main.py
   ```

## Usage Examples

### Adding Entries
The AI automatically detects mood and extracts tags:

```
You: Had a great day at work! Finally finished the big project.
→ Entry: "Finished the big project at work"
→ Mood: "happy" 
→ Tags: ["work", "achievement"]
```

```
You: Feeling stressed about the upcoming presentation tomorrow.
→ Entry: "Stressed about upcoming presentation"
→ Mood: "anxious"
→ Tags: ["work", "presentation"]
```

### Getting Summaries
```
You: Summarize my day
→ Connects you to Summarizer Agent for analysis
```

### Searching & Filtering
```
You: Show me all work-related entries from this week
You: Find entries where I felt happy
You: Search for entries about coffee
```

## AI Agents

### Journal Agent
- **Purpose**: Entry management and organization
- **Functions**: Add, view, search, and filter entries
- **Smart Features**: Mood detection, tag extraction, text cleanup

### Summarizer Agent  
- **Purpose**: Analysis and insights
- **Functions**: Daily summaries, pattern recognition, trend analysis
- **Output**: Concise, actionable insights

## Project Structure

```
adk-digital-journal-and-assistant/
├── main.py                 # Main application entry point
├── utils.py                # Response processing and utilities
├── memory_agent/           # AI agent configurations
│   └── agent.py            # Agent definitions and tools
│   └── sub_agents/         # Sub Agents folder, each will have .env and agent.py
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not tracked)
├── my_daily_journal.db    # SQLite database (not tracked)
└── README.md              # This file
```

## Configuration

### Environment Variables
Create a `.env` file with:
```env
GOOGLE_AI_API_KEY=your_gemini_api_key
USER_NAME=Your Name
```

### Customizing Agents
Edit `memory_agent/agent.py` to modify:
- Mood detection keywords
- Tag extraction logic  
- Response formatting
- Agent behavior and prompts

## Technical Details

- **AI Model**: Google Gemini 2.0 Flash
- **Database**: SQLite for local storage
- **Framework**: Python with async support
- **Entry Storage**: JSON metadata with timestamp, mood, and tags

## Privacy & Security

- All data stored locally in SQLite database
- No data sent to external services except AI API calls
- `.env` files and database excluded from git tracking
- API keys never committed to repository

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

**503 API Errors**: Google AI is temporarily overloaded
- Solution: Wait 5-10 minutes and try again

**Entry Concatenation**: Entries getting combined
- Solution: Check agent instructions for context bleeding

**Missing Dependencies**: Module not found errors
- Solution: Ensure virtual environment is activated and requirements installed

### Debug Mode
To enable detailed logging, add to your code:
```python
DEBUG = True  # Set to False for production
```

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with Google's Gemini AI
- Inspired by the need for intelligent journaling tools
- Thanks to the open-source community for various dependencies
