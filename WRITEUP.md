## Hybrid Company Search Engine

## 3.1 Approach

My solution implements a Hybrid Retriever-Ranker architecture that bridges the gap between deterministic database filtering and semantic natural language understanding. 

**Components:**
1. **Query Parser (Retriever - Hard Filter):** A local LLM (Llama 3B) instructed via a strict system prompt to translate natural language queries into a JSON filter. It handles exact constraints (e.g., employee count boundaries, dynamic mapping of geographical regions to ISO-2 codes).
2. **Data Engine (Processor & Matcher):** A custom Python engine that reads a `.jsonl` file line-by-line. It cleans stringified nested objects (like `address`), intelligently merges duplicate entries (filling `None` values and combining arrays using `operational_name` or `website` as keys), and applies the LLM's JSON filter recursively.
3. **Semantic Ranker (Soft Filter):** A local HuggingFace embedding model (`all-MiniLM-L6-v2`) that calculates Cosine Similarity between the user's query and a concatenated "story" string of the filtered companies (name + description + target markets + offerings).

**Interaction:**
The user inputs a query -> Llama 3B generates a structured JSON filter -> The Python Engine scans the `.jsonl` dataset, merges duplicates, and returns a subset of companies that strictly match the hard rules -> The NLP Ranker scores this subset semantically and returns only the results above a 25% relevance threshold.

**Design Choice Rationale:**
I chose this design because pure vector searches fail at hard constraints (e.g., "revenue over 1M" or "strictly in Norway"), while pure SQL/NoSQL fails at nuance (e.g., understanding that "sustainable" relates to "renewable energy"). By using a small LLM solely as a logic translator and delegating the semantic matching to a specialized embedding model, the system achieves high accuracy with minimal compute overhead.

## 3.2 Tradeoffs

**Optimized for:**
* **Accuracy & Precision:** Ensuring numerical limits and geographic boundaries are strictly respected before any semantic guessing occurs.
* **Robustness to Messy Data:** The deduplication logic ensures that fragmented records (e.g., one with revenue, another with employee count) are combined to prevent false negatives.
* **Privacy & Cost:** The entire stack runs locally on a low-medium-end GPU with standard RAM and CPU, without reliance on paid APIs.

**Intentional Tradeoffs:**
* **Latency vs. Simplicity:** Parsing the dataset line-by-line in Python is O(N). I traded query speed (which would be faster with a pre-indexed database) for architectural simplicity and memory efficiency, avoiding the need to spin up and maintain a dedicated database instance for the initial iteration.
* **LLM Categorization vs. NLP Ranking:** I intentionally removed specific array fields (`business_model`, `target_markets`) from the LLM's prompt. Small models hallucinate categories (e.g., inventing "Battery Manufacturing"). I traded the LLM's ability to filter by strict categories for broader keyword searches (`$contains` in `description`), relying entirely on the NLP ranker to sort out the actual niche relevance.

## 3.3 Error Analysis

**Where the system struggles:**
1. **Negation handling:** If a user searches for "Companies doing packaging for cosmetics", and a company description states "We provide packaging for food, but NOT cosmetics", the LLM's `$contains` filter will find both words and pass it to the NLP ranker. Semantic models often struggle with negation, so this company might still receive a high relevance score.
2. **Complex nested logic interpretation:** For highly convoluted queries (e.g., "Startups in UK over 500 employees OR in France under 100 employees"), Llama 3B occasionally struggles to map the correct `$or` nesting, leading to overly restrictive filters.

## 3.4 Scaling

If the system needed to handle 100,000 or millions of companies per query, the current O(N) line-by-line Python evaluation would become a severe bottleneck. 

**Changes required:**
1. **Data Layer:** I would replace the Python dictionary-matching script with an actual document database (like MongoDB). The data cleaning and deduplication would be moved to an asynchronous ingestion pipeline (ETL) rather than happening on-the-fly at query time.
2. **Indexing:** The LLM would query the database using standard indexes for numbers and geographical codes, returning the subset in milliseconds.
3. **NLP Component:** The Ranker architecture would remain the same. Because the database handles the heavy lifting of hard filtering, the NLP model still only needs to evaluate a small subset of results (e.g., the top 500 matches), allowing the semantic search to remain fast and computationally cheap.


## 3.5 Failure Modes

**Confident but incorrect results:**
* **Keyword Bias in Data:** If a company heavily stuffs its description with buzzwords ("AI", "SaaS", "Green Energy") but actually operates in a different primary sector, the Ranker will confidently assign a high score based on keyword proximity.
* **Prompt Drift / Format Failure:** If the LLM generates a slightly malformed JSON (e.g., missing a bracket or using an unsupported operator), the Python engine will fail to parse it, returning 0 results while the system appears to have functioned normally.

**Production Monitoring:**
To detect these failures, I would monitor:
1. **Filter Match Rates:** If queries consistently return 0 companies before the NLP stage, the LLM is likely generating overly restrictive or hallucinated filters.
2. **JSON Parse Error Rates:** Tracking how often the `ast.literal_eval` or `json.loads` fails on the LLM output.
3. **Average Relevance Scores:** If the top results consistently score near the 25% minimum threshold, it indicates the hard filter is passing irrelevant data, or the embedding model lacks the domain vocabulary to properly score the industry.

## Critical Thinking & Reflection

The system works exceptionally well at isolating structured data points embedded in unstructured prompts. Its greatest strength lies in its hybrid nature: it does not force an LLM to read thousands of company descriptions, nor does it force a vector database to understand math.

A primary assumption I made is that the `description` field contains enough vocabulary to trigger the `$contains` keyword searches. If a company has a sparse description but rich `core_offerings`, the LLM might miss it because I restricted its access to those arrays to prevent hallucinations.

The system relies heavily on the LLM strictly following the JSON schema. This signal can be misleading if the model's underlying logic flips a `>=` to a `<=`. Therefore, the next priority for improvement would be implementing a self-correction loop: if the LLM output causes a JSON decode error or returns 0 results, the system should automatically inject the error back into the LLM and ask for a revised filter. Understanding that the LLM is the single point of failure for the entire retrieval pipeline dictates that future work must focus on bounding its output even more rigidly.


Also, for a more precise response properly fine-tuning and distilation is needed. Actually, this is why I sticked to this approach, because I believe that it can be very cost-effective and accurate.