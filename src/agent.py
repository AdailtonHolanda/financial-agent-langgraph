from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain.tools import tool
from src.tools import retrieve_realtime_stock_price, retrieve_historical_stock_price
from src.rag import AmazonReportRAG
from langfuse.callback import CallbackHandler

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

class FinancialAgent:
    def __init__(self, langfuse_handler=None):
        self.rag = AmazonReportRAG()
        self.langfuse_handler = langfuse_handler
        
        self.rag_tool = self._create_rag_tool()
        
        self.tools = [
            retrieve_realtime_stock_price,
            retrieve_historical_stock_price,
            self.rag_tool
        ]
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            streaming=True
        )
        
        if langfuse_handler:
            self.llm_with_tools = self.llm.bind_tools(self.tools, callbacks=[langfuse_handler])
        else:
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.graph = self._create_graph()
    
    def _create_rag_tool(self):
        @tool
        def search_amazon_reports(query: str) -> str:
            """Search Amazon earnings reports for company information, financials, AI business, and analyst predictions."""
            try:
                docs = self.rag.search(query, k=4)
                
                if not docs:
                    return "No relevant information found in Amazon reports."
                
                result = "Information from Amazon Reports:\n\n"
                for i, doc in enumerate(docs, 1):
                    result += f"[Source {i}: {doc.metadata.get('source', 'Unknown')}]\n"
                    result += f"{doc.page_content}\n\n"
                
                return result
            except Exception as e:
                return f"Error searching Amazon reports: {str(e)}"
        
        return search_amazon_reports
    
    def _should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return "end"
        return "continue"
    
    def _call_model(self, state: AgentState):
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def _create_graph(self):
        workflow = StateGraph(AgentState)
        
        tool_node = ToolNode(self.tools)
        
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", tool_node)
        
        workflow.set_entry_point("agent")
        
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def setup_rag(self):
        self.rag.setup()
    
    async def astream(self, query: str):
        inputs = {"messages": [HumanMessage(content=query)]}
        
        async for event in self.graph.astream(inputs, stream_mode="values"):
            if "messages" in event:
                last_message = event["messages"][-1]
                yield event
    
    def invoke(self, query: str):
        inputs = {"messages": [HumanMessage(content=query)]}
        result = self.graph.invoke(inputs)
        return result
