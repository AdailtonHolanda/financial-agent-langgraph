# Financial Agent - Amazon Stock Analysis with LangGraph

A production-ready financial analysis agent built with LangGraph, featuring RAG over Amazon earnings reports, real-time stock data, AWS deployment with Terraform, and Cognito authentication.

## Features

- **LangGraph Agent**: Intelligent agent with tool calling and reasoning
- **Stock Analysis Tools**: Real-time and historical stock prices via yfinance
- **RAG System**: Semantic search over Amazon Q2 and Q3 2025 earnings reports
- **Event Streaming**: Responses streamed via `.astream()`
- **AWS Cognito**: Secure user authentication
- **Langfuse Tracing**: Complete observability of agent interactions
- **Terraform Infrastructure**: Automated AWS deployment

## Architecture

```
User Request
    ↓
AWS Cognito Authentication
    ↓
API Gateway (with Cognito Authorizer)
    ↓
AWS Lambda (Financial Agent)
    ↓
LangGraph Agent
    ├── retrieve_realtime_stock_price (yfinance)
    ├── retrieve_historical_stock_price (yfinance)
    └── search_amazon_reports (RAG/FAISS)
    ↓
Langfuse Tracing
    ↓
Response
```

## Prerequisites

- Python 3.11+
- AWS Account with CLI configured
- Terraform >= 1.0
- OpenAI API Key
- Langfuse Account (free at https://cloud.langfuse.com)

## Quick Start

### 1. Clone and Setup

```bash
cd teste
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
AWS_REGION=us-east-1
```

### 3. Test Locally (Optional)

```bash
python local_test.py
```

This will:
- Download Amazon earnings PDFs
- Create FAISS vector store
- Run test queries locally

### 4. Deploy to AWS

#### Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:
```hcl
aws_region          = "us-east-1"
project_name        = "financial-agent"
environment         = "prod"
openai_api_key      = "sk-..."
langfuse_secret_key = "sk-lf-..."
langfuse_public_key = "pk-lf-..."
```

#### Build and Deploy

**On Linux/Mac:**
```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
```

**On Windows:**
```powershell
.\scripts\deploy.ps1
```

This will:
1. Build Lambda deployment package
2. Initialize Terraform
3. Create AWS resources:
   - Lambda function
   - API Gateway with Cognito authorizer
   - Cognito User Pool
   - S3 bucket for deployment
4. Output deployment details

### 5. Create Cognito User

After deployment, create a test user:

```bash
# Get outputs from Terraform
cd terraform
terraform output

# Create user
aws cognito-idp admin-create-user \
  --user-pool-id <COGNITO_USER_POOL_ID> \
  --username your-email@example.com \
  --user-attributes Name=email,Value=your-email@example.com \
  --message-action SUPPRESS

# Set permanent password
aws cognito-idp admin-set-user-password \
  --user-pool-id <COGNITO_USER_POOL_ID> \
  --username your-email@example.com \
  --password YourSecurePassword123! \
  --permanent
```

### 6. Update .env with Deployment Info

Add the deployment outputs to your `.env`:

```env
API_ENDPOINT=https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/query
COGNITO_USER_POOL_ID=us-east-1_xxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxx
```

### 7. Run Demo Notebook

```bash
jupyter notebook demo_notebook.ipynb
```

The notebook will:
- Authenticate with Cognito
- Execute all test queries
- Display responses
- Show Langfuse traces

## Test Queries

The system handles these queries (as per requirements):

1. **Real-time Price**: "What is the stock price for Amazon right now?"
2. **Historical Data**: "What were the stock prices for Amazon in Q4 last year?"
3. **Performance Analysis**: "Compare Amazon's recent stock performance to what analysts predicted in their reports"
4. **AI Business Research**: "I'm researching AMZN give me the current price and any relevant information about their AI business"
5. **Office Space**: "What is the total amount of office space Amazon owned in North America in 2024?"

## Project Structure

```
teste/
├── src/
│   ├── __init__.py
│   ├── agent.py              # LangGraph agent implementation
│   ├── tools.py              # Stock price tools (yfinance)
│   ├── rag.py                # RAG system for Amazon reports
│   └── lambda_handler.py     # AWS Lambda handler
├── terraform/
│   ├── main.tf               # Main infrastructure
│   ├── variables.tf          # Input variables
│   ├── outputs.tf            # Output values
│   └── terraform.tfvars      # Your configuration
├── scripts/
│   ├── build_lambda.sh       # Build Lambda package (Linux/Mac)
│   ├── build_lambda.ps1      # Build Lambda package (Windows)
│   ├── deploy.sh             # Full deployment (Linux/Mac)
│   └── deploy.ps1            # Full deployment (Windows)
├── demo_notebook.ipynb       # Demo with all test queries
├── local_test.py             # Local testing script
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## Tools Implemented

### 1. retrieve_realtime_stock_price
- Uses yfinance API
- Returns current price, market cap, day range, volume
- Example: `retrieve_realtime_stock_price("AMZN")`

### 2. retrieve_historical_stock_price
- Uses yfinance API
- Supports date ranges or periods (1mo, 3mo, 1y, ytd)
- Returns price statistics and changes
- Example: `retrieve_historical_stock_price("AMZN", period="3mo")`

### 3. search_amazon_reports (RAG)
- Searches Amazon Q2 and Q3 2025 earnings reports
- Uses FAISS vector store with OpenAI embeddings
- Returns relevant document chunks with sources

## Langfuse Tracing

All agent interactions are traced in Langfuse:

1. Go to https://cloud.langfuse.com
2. View your project
3. See traces for:
   - LLM calls
   - Tool invocations
   - Token usage
   - Latency metrics
   - Full conversation flow

## Infrastructure Details

### AWS Resources Created

- **Lambda Function**: Runs the financial agent (Python 3.11, 1GB RAM, 5min timeout)
- **API Gateway**: REST API with Cognito authorization
- **Cognito User Pool**: User authentication and management
- **S3 Bucket**: Stores Lambda deployment package
- **IAM Roles**: Lambda execution role with necessary permissions

### Cost Estimate

- Lambda: ~$0.20 per 1M requests + compute time
- API Gateway: ~$3.50 per 1M requests
- Cognito: Free tier covers 50,000 MAUs
- S3: Minimal storage costs

## Streaming Implementation

The agent uses LangGraph's `.astream()` for event streaming:

```python
async for event in agent.astream(query):
    # Process streaming events
    messages = event.get('messages', [])
    # Handle each event
```

Events are filtered by LLM invocation as per LangGraph documentation.

## Troubleshooting

### Lambda Package Too Large

If the Lambda package exceeds 50MB:
1. Use Lambda Layers for heavy dependencies
2. Or deploy via S3 (already configured in Terraform)

### RAG Setup Issues

If PDF download fails:
1. Check internet connection
2. Manually download PDFs to `pdfs/` directory
3. Run `local_test.py` to create vector store

### Cognito Authentication Errors

- Ensure user is confirmed
- Check password meets requirements (8+ chars, uppercase, lowercase, number, symbol)
- Verify client ID and user pool ID are correct

### Langfuse Not Showing Traces

- Verify API keys in `.env`
- Check Langfuse project is active
- Ensure callbacks are passed to LLM initialization

## Development

### Adding New Tools

1. Define tool in `src/tools.py`:
```python
@tool
def my_new_tool(param: str) -> str:
    """Tool description"""
    # Implementation
    return result
```

2. Add to agent in `src/agent.py`:
```python
self.tools = [
    retrieve_realtime_stock_price,
    retrieve_historical_stock_price,
    self.rag_tool,
    my_new_tool  # Add here
]
```

### Updating RAG Documents

1. Add PDFs to `pdfs/` directory
2. Update `src/rag.py` to include new sources
3. Rebuild vector store

## Cleanup

To destroy all AWS resources:

```bash
cd terraform
terraform destroy
```

## License

MIT

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Langfuse traces for debugging
3. Check CloudWatch logs for Lambda errors

## Acknowledgments

- LangChain/LangGraph for agent framework
- OpenAI for LLM capabilities
- Langfuse for observability
- yfinance for stock data
- AWS for infrastructure
