import os
import asyncio
from dotenv import load_dotenv
from src.agent import FinancialAgent
from langfuse.callback import CallbackHandler

load_dotenv()

async def test_agent():
    """Test the financial agent locally"""
    
    langfuse_handler = CallbackHandler(
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    
    print("Initializing agent...")
    agent = FinancialAgent(langfuse_handler=langfuse_handler)
    
    print("Setting up RAG system...")
    agent.setup_rag()
    
    queries = [
        "What is the stock price for Amazon right now?",
        "What were the stock prices for Amazon in Q4 last year?",
        "Compare Amazon's recent stock performance to what analysts predicted in their reports",
        "I'm researching AMZN give me the current price and any relevant information about their AI business",
        "What is the total amount of office space Amazon owned in North America in 2024?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}: {query}")
        print('='*80)
        
        print("\nStreaming response:")
        async for event in agent.astream(query):
            messages = event.get('messages', [])
            if messages:
                last_msg = messages[-1]
                if hasattr(last_msg, 'content') and last_msg.content:
                    if not hasattr(last_msg, 'tool_calls') or not last_msg.tool_calls:
                        print(f"\nFinal Answer: {last_msg.content}")
        
        print("\n" + "-"*80)

if __name__ == "__main__":
    asyncio.run(test_agent())
