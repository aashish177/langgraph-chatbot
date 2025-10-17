from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# NEW IMPORT
from amazon_agent import get_amazon_tools

load_dotenv()

llm = init_chat_model(
    model="gpt-4o-mini",
    model_provider="openai"
)

# NEW: Get Amazon tools
print("Loading Amazon tools...")
amazon_tools = get_amazon_tools()
llm_with_amazon_tools = llm.bind_tools(amazon_tools)
print(f"✓ Loaded {len(amazon_tools)} Amazon tools")

class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical", "amazon_query"] = Field(
        ...,
        description="Classify if the message requires an emotional (therapist), logical, or Amazon seller data response."
    )

class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None

def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
            - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
            - 'logical': if it asks for facts, information, logical analysis, or practical solutions
            - 'amazon_query': if it asks about Amazon seller data (orders, inventory, listings, sales, etc.)
            """
        },
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}

def router(state: State):
    message_type = state.get("message_type", "logical")
    if message_type == "emotional":
        return {"next": "therapist"}
    elif message_type == "amazon_query":
        return {"next": "amazon_agent"}

    return {"next": "logical"}

def therapist_agent(state: State):
    last_message = state["messages"][-1]
    print("state: " + str(state))

    messages = [
        {"role": "system",
         "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate their feelings, and help them process their emotions.
                        Ask thoughtful questions to help them explore their feelings more deeply.
                        Avoid giving logical solutions unless explicitly asked."""
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]

    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

def logical_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """You are a purely logical assistant. Focus only on facts and information.
            Provide clear, concise answers based on logic and evidence.
            Do not address emotions or provide emotional support.
            Be direct and straightforward in your responses."""},
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

# NEW: Amazon Agent
def amazon_agent(state: State):
    """Agent with access to Amazon Seller tools"""
    last_message = state["messages"][-1]

    messages = [
        {
            "role": "system",
            "content": """You are an Amazon Seller assistant with access to real-time seller data.
            You can help with:
            - Checking orders and order details
            - Viewing inventory levels
            - Getting product listings
            - Analyzing sales metrics

            Use the available tools to answer questions about the Amazon seller account.
            Always provide specific data when available."""
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ]

    # LLM will automatically call tools if needed
    response = llm_with_amazon_tools.invoke(messages)

    # Check if response has tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        # Execute tool calls
        tool_messages = []
        for tool_call in response.tool_calls:
            # Find and execute the tool
            tool = next((t for t in amazon_tools if t.name == tool_call['name']), None)
            if tool:
                try:
                    tool_result = tool.invoke(tool_call.get('args', {}))
                    tool_messages.append({
                        "role": "tool",
                        "content": str(tool_result),
                        "tool_call_id": tool_call.get('id', '')
                    })
                except Exception as e:
                    tool_messages.append({
                        "role": "tool",
                        "content": f"Error calling tool: {str(e)}",
                        "tool_call_id": tool_call.get('id', '')
                    })

        # Get final response with tool results
        if tool_messages:
            final_messages = messages + [response] + tool_messages
            final_response = llm.invoke(final_messages)
            return {"messages": [{"role": "assistant", "content": final_response.content}]}

    # Return direct response if no tool calls
    content = response.content if hasattr(response, 'content') else str(response)
    return {"messages": [{"role": "assistant", "content": content}]}


graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_node("logical", logical_agent)
graph_builder.add_node("amazon_agent", amazon_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"therapist": "therapist", "logical": "logical", "amazon_agent": "amazon_agent"},
)

graph_builder.add_edge("therapist", END)
graph_builder.add_edge("logical", END)
graph_builder.add_edge("amazon_agent", END)

graph = graph_builder.compile()

def run_chatbot():
    state  = {
        "messages": [],
        "message_type": None
    }

    print("\nChatbot ready! (type 'quit' to exit)")
    print("Try: 'What's my current inventory?' or 'How many orders today?'\n")

    while True:
        user_input = input("You: ")
        if user_input == "quit":
            print("Goodbye!")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}\n")

if __name__ == "__main__":
    run_chatbot()