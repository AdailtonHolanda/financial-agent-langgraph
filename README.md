# Financial Analysis Agent with LangGraph

An end-to-end AI agent for financial research built with LangGraph, OpenAI, RAG, external market-data tools, observability, authentication, and infrastructure as code.

The project combines live market data with retrieval over Amazon earnings reports so the agent can answer questions that require both current information and grounded company context.

## What this project demonstrates

- **Agent orchestration with LangGraph** using tool calling and conditional routing
- **RAG over financial reports** with OpenAI embeddings and FAISS
- **External tools** for real-time and historical stock data via `yfinance`
- **Observability** with Langfuse tracing
- **AWS deployment architecture** using Lambda, API Gateway, Cognito, S3, and IAM
- **Infrastructure as code** with Terraform
- **Local and deployed execution paths**
- **Automated tests** for core tool and retrieval behavior

## Architecture

```text
User Request
    |
    v
AWS Cognito Authentication
    |
    v
API Gateway
    |
    v
AWS Lambda
    |
    v
LangGraph Agent
    |-- retrieve_realtime_stock_price
    |-- retrieve_historical_stock_price
    `-- search_amazon_reports
            |
            v
        RAG / FAISS
            |
            v
   Amazon Earnings Reports

Agent execution -> Langfuse tracing
```

## Agent flow

The LangGraph workflow alternates between the LLM and tool execution until no further tool calls are requested:

```text
START -> agent -> tools -> agent -> ... -> END
```

The current implementation uses `gpt-4o-mini` with deterministic temperature settings and binds three tools to the model: two market-data tools and one retrieval tool.

## RAG pipeline

```text
Amazon earnings PDFs
        |
        v
PDF extraction
        |
        v
Recursive text splitting
        |
        v
OpenAI embeddings
        |
        v
FAISS vector index
        |
        v
Similarity search
        |
        v
Grounded context returned to the agent
```

The index is persisted locally so it can be reused between runs. For a production deployment, a pre-built index or managed vector store would be preferable to rebuilding retrieval assets during application startup.

## Project structure

```text
.
├── src/
│   ├── agent.py              # LangGraph orchestration
│   ├── tools.py              # Market-data tools
│   ├── rag.py                # Retrieval pipeline
│   └── lambda_handler.py     # AWS Lambda entry point
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── scripts/
│   ├── build_lambda.sh
│   ├── build_lambda.ps1
│   ├── deploy.sh
│   └── deploy.ps1
├── tests/                    # Unit tests for core behavior
├── demo_notebook.ipynb       # End-to-end demo
├── local_test.py             # Local smoke test
├── requirements.txt
└── .env.example
```

## Local setup

### 1. Clone and create an environment

```bash
git clone https://github.com/AdailtonHolanda/tech_challenge.git
cd tech_challenge
python -m venv .venv
```

Activate the environment:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Required values include:

```env
OPENAI_API_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_HOST=https://cloud.langfuse.com
AWS_REGION=us-east-1
```

### 4. Run locally

```bash
python local_test.py
```

On the first run, the retrieval component downloads the configured Amazon earnings reports and creates the local FAISS index.

## Example questions

The agent can handle questions such as:

- What is Amazon's current stock price?
- How has AMZN performed over the last three months?
- What do recent earnings reports say about Amazon's AI business?
- Combine the current stock price with relevant information from recent reports.
- What financial or operating information is reported in the indexed documents?

## Tests

Run the unit tests with:

```bash
pytest -q
```

The tests mock external APIs so core behavior can be validated without calling Yahoo Finance or OpenAI.

## AWS deployment

The Terraform configuration provisions the main infrastructure required to expose the agent behind an authenticated API:

- AWS Lambda
- API Gateway
- Cognito User Pool and authorizer
- S3 deployment bucket
- IAM roles and policies

Build and deploy with the scripts under `scripts/`, or run Terraform directly.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

After deployment, use the Terraform outputs to configure the demo notebook with the API endpoint and Cognito identifiers.

## Observability

Langfuse is integrated into the LLM execution path to capture traces for model calls, tool invocations, latency, token usage, and conversation flow. This makes it easier to debug agent behavior and inspect how requests are resolved.

## Streaming note

The LangGraph layer supports asynchronous event iteration with `.astream()`. The current REST/Lambda response path returns a completed response to the client rather than maintaining a true streaming HTTP connection. A production streaming API could use an appropriate streaming transport such as WebSockets, Server-Sent Events, or a platform-specific streaming response mechanism.

## Production considerations

This repository demonstrates a complete application path, but several improvements would be appropriate for a higher-scale production system:

- build and version the vector index outside Lambda cold starts;
- store retrieval assets in durable/shared infrastructure;
- add retries, timeouts, and circuit-breaking around external services;
- introduce structured evaluation for retrieval quality and answer faithfulness;
- add rate limiting and request-level telemetry;
- use secret-management infrastructure instead of deployment variables for sensitive values;
- add CI/CD and integration tests for the deployed API;
- use a true streaming transport when token/event streaming is required by the client.

## Design decisions

**Why LangGraph?** It makes the agent state and tool-routing loop explicit rather than hiding orchestration inside a single opaque call.

**Why FAISS?** It provides a lightweight vector-search implementation that is easy to run locally and sufficient for demonstrating the retrieval architecture.

**Why separate tools from retrieval?** Market prices and historical time series are dynamic data sources, while earnings reports are document-based knowledge. Treating them as separate tools allows the agent to choose the appropriate source for each question.

**Why Terraform?** Infrastructure as code makes the deployment architecture reproducible and reviewable alongside the application code.

## Tech stack

Python · LangGraph · LangChain · OpenAI · FAISS · yfinance · Langfuse · AWS Lambda · API Gateway · Cognito · S3 · Terraform · Pytest

## License

MIT
