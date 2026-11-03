# Self Learning Research Agent

A Python multi-agent research system built with LangChain and LangGraph. It plans a topic, searches the web, extracts and evaluates sources, synthesizes findings, and creates a structured report with citations.

The web interface is built with Gradio. The separate command-line workflow is still available through main.py.

## Features

- Multi-agent research planning, web searching, synthesis, and report writing
- Source credibility scoring and citation-supported reports
- Google Gemini, OpenAI-compatible APIs, Ollama, and llama.cpp model support
- DuckDuckGo or Tavily web search
- Research caching and graph checkpointing
- Markdown, HTML, and plain text report downloads
- Gradio web interface and command-line entry point

## Requirements

- Python 3.11 or newer
- An API key for the selected cloud model, or a running local model server
- Internet access for web search and page extraction

## Installation

From the project directory, create and activate a virtual environment:

    python -m venv .venv
    .venv\Scripts\activate

Install the dependencies:

    pip install -r requirements.txt

Create the project .env file from the Ollama example:

    Copy-Item .env.example .env

The default is Ollama with qwen2.5:7b for both the main agents and the summarizer. If you change the model, update MODEL_NAME and SUMMARIZATION_MODEL together (or remove SUMMARIZATION_MODEL so it follows MODEL_NAME). Make sure Ollama is running and the selected model is installed.

Gemini example:

    MODEL_PROVIDER=gemini
    MODEL_NAME=gemini-2.5-flash
    GEMINI_API_KEY=your_api_key

OpenAI example:

    MODEL_PROVIDER=openai
    MODEL_NAME=gpt-4o-mini
    OPENAI_API_KEY=your_api_key

Ollama example:

    MODEL_PROVIDER=ollama
    MODEL_NAME=qwen2.5:7b
    OLLAMA_BASE_URL=http://localhost:11434

Tavily search is optional. Set SEARCH_PROVIDER=tavily and TAVILY_API_KEY to use it; DuckDuckGo is the default.

## Start the Gradio interface

Run this command from the project directory:

    python app.py

Then open http://127.0.0.1:7860 in your browser. Enter a research topic and select Start research. The generated report is shown in the page and saved under outputs in Markdown, HTML, and plain text formats.

The server binds to localhost by default. To make it available on a network, change server_name in app.py to 0.0.0.0 and configure access controls appropriate for your environment.

## Command-line usage

Interactive:

    python main.py

With a topic:

    python main.py "Impact of quantum computing on cryptography"

## Project layout

    app.py                  Gradio web interface
    main.py                 Command-line entry point
    src/agents.py           Planner, searcher, synthesizer, and writer agents
    src/graph.py            LangGraph workflow
    src/state.py            Workflow state and data models
    src/config.py           Model, search, and report configuration
    src/utils/tools.py      Web search, extraction, and research tools
    src/utils/              Caching, citations, credibility, exports, and history
    outputs/                Generated reports

## Research workflow

1. The planner creates objectives, search queries, and a report outline.
2. The searcher gathers information from web sources and extracts page content.
3. The synthesizer combines findings and identifies research gaps.
4. The report writer creates a structured report with citations and references.

Academic papers may be found through web search like other public sources. The project does not use a local paper database or paper-corpus question-answering mode.

## License

MIT. See LICENSE.
