# Satellite Data Extraction Chatbot

An intelligent chatbot for extracting and analyzing satellite data using LangGraph.

## Features
- Satellite data extraction from trusted sources
- Interactive chat interface for general queries
- Structured data output for specific satellite details
- Caching system for previously queried satellites

## Project Structure
- `src/`: Source code
  - `agents/`: LangGraph agents for data collection and processing
  - `data/`: Data collection and processing modules
  - `utils/`: Utility functions
  - `app/`: Streamlit application
- `tests/`: Test files
- `data/`: Data storage

## Setup
1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run src/app/streamlit_app.py
   ```

## Development
- Use `src/agents/` for LangGraph agent implementations
- Add new data sources in `src/data/scrapers/`
- Modify the UI in `src/app/streamlit_app.py`