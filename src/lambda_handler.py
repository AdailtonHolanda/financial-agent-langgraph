import json
import os
import asyncio
from src.agent import FinancialAgent
from langfuse.callback import CallbackHandler

agent = None

def get_agent():
    global agent
    if agent is None:
        langfuse_handler = CallbackHandler(
            secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
            public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
            host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        agent = FinancialAgent(langfuse_handler=langfuse_handler)
        agent.setup_rag()
    return agent

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        
        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Query parameter is required'})
            }
        
        agent_instance = get_agent()
        
        result = agent_instance.invoke(query)
        
        messages = result.get('messages', [])
        final_response = ""
        
        for msg in messages:
            if hasattr(msg, 'content') and isinstance(msg.content, str) and msg.content:
                if not hasattr(msg, 'tool_calls') or not msg.tool_calls:
                    final_response = msg.content
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': final_response,
                'message_count': len(messages)
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

async def stream_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        
        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Query parameter is required'})
            }
        
        agent_instance = get_agent()
        
        events = []
        async for event in agent_instance.astream(query):
            events.append({
                'message_count': len(event.get('messages', [])),
                'last_message_type': type(event.get('messages', [None])[-1]).__name__ if event.get('messages') else None
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'events': events,
                'total_events': len(events)
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
