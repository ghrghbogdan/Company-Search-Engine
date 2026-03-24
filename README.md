# Hybrid Company Search Engine - Setup & Run Guide

This project uses a hybrid architecture (local LLM for JSON parsing + NLP model for semantic ranking) to query a company database. Processing is done 100% locally, without any external APIs.

## 1. Prerequisites
* Python 3.8+ installed on your system.
* Ollama installed to run the local language model.

## 2. Ollama Setup & Configuration
The system relies on the Llama model to translate natural language queries into database filters.

1. Install Ollama from ollama.com.
2. Open a terminal and download the required model:
   ```bash
   ollama pull llama3.2:3b
   ```
3. Ensure the Ollama server is running in the background. On a desktop, the application must be open. If using a headless environment, start the server manually:
   ```bash
   ollama serve
   ```

## 3. Python Environment Setup
Open a terminal in the project's root folder and install the dependencies:

```bash
pip install -r requirements.txt
```
*Note: On the first run, the sentence-transformers library will automatically download the embedding model (all-MiniLM-L6-v2, approx. 80MB).*

## 4. Running the Application
1. Make sure the database file (companies.jsonl) is located in the same folder as the main script.
2. Run the main script:

```bash
python solution.py
```

The system will process the queries, contact the local Ollama server to generate JSON filters, extract matching data from the .jsonl file, and return the top companies sorted by semantic relevance.