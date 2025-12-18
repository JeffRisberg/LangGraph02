"""
This is the main entry point for the agent.
It defines the workflow graph, state, tools, nodes and edges.
"""

from langchain.tools import tool
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from typing_extensions import Literal, TypedDict, Annotated


model = ChatOpenAI(model="gpt-4o")

@tool
def get_weather(location: str):
    """
    Get the weather for a given location.
    """
    if location.lower() == "new york":
        return "The weather for New York is 75 degrees."
    elif location.lower() == "los angeles":
        return "The weather for Los Angeles is 80 degrees."

    return f"The weather for {location} is 70 degrees."

@tool
def get_jobs(skill: str):
    """
    Get the job for a given skill.
    """
    if "math" in skill:
        return "The best job for you is financial analyst."
    elif "computer" in skill:
        return "The best job for you is software developer."
    elif "communication" in skill:
        return "The best job for you is teacher."

    return f"The best job for you is bricklayer or burgerflipper."


tools = [
    get_weather,
    get_jobs
]


# Bind the tools to the model
model_with_tools = model.bind_tools(tools,
                                    parallel_tool_calls=False,
                                    )


class AgentState(TypedDict):
    """
    Here we define the state of the agent
    """
    skills: str
    messages: Annotated[list[HumanMessage | AIMessage], add_messages]


def add_message(state: AgentState, message: str, is_human: bool = True) -> AgentState:
    new_message = HumanMessage(content=message) if is_human else AIMessage(content=message)
    return AgentState(
        skills=state["skills"],
        messages=state["messages"] + [new_message]
    )


async def chat_node(state: AgentState, config: RunnableConfig) -> Command[Literal["tool_node", "__end__"]]:
    """
    Standard chat node based on the ReAct design pattern. It handles:
    - The system prompt
    - Getting a response from the model
    - Handling tool calls

    For more about the ReAct design pattern, see:
    https://www.perplexity.ai/search/react-agents-NcXLQhreS0WDzpVaS4m9Cg
    """

    # 1. Define the system message by which the chat model will be run
    system_message = SystemMessage(
        content=f"You are a helpful assistant. Talk in {state.get('language', 'english')}."
    )

    # 2. Run the model to generate a response
    response = await model_with_tools.ainvoke([
        system_message,
        *state["messages"],
    ], config)

    print(response)

    # 3. Check for tool calls in the response and handle them.
    if isinstance(response, AIMessage) and response.tool_calls:
        return Command(goto="tool_node", update={"messages": response})

    # 5. We've handled all tool calls, so we can end the graph.
    return Command(
        goto=END,
        update={
            "messages": response
        }
    )


# Define the workflow graph
workflow = StateGraph(AgentState)
workflow.add_node("chat_node", chat_node)
workflow.add_node("tool_node", ToolNode(tools=tools))

workflow.add_edge("tool_node", "chat_node")

workflow.set_entry_point("chat_node")

# Compile the workflow graph
graph = workflow.compile()
