"""
Travel Planner API Adapter
Adapts the LangGraph travel planner for API usage
"""
from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="Qwen/Qwen3-8B", temperature=0.7)

class PlannerState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], "The messages in the conversation"]
    city: str
    interests: List[str]
    itinerary: str

itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful travel assistant. Create a day trip itinerary for {city} based on the user's interests: {interests}. Provide a detailed, bulleted itinerary with specific recommendations for places to visit, restaurants, and activities. Include approximate timing for each activity."),
    ("human", "Create an itinerary for my day trip."),
])

def process_inputs(state: PlannerState) -> PlannerState:
    """Process the city and interests from the initial state"""
    return state

def create_itinerary(state: PlannerState) -> PlannerState:
    """Generate travel itinerary based on city and interests"""
    response = llm.invoke(
        itinerary_prompt.format_messages(
            city=state['city'], 
            interests=", ".join(state['interests'])
        )
    )
    return {
        **state,
        "messages": state['messages'] + [AIMessage(content=response.content)],
        "itinerary": response.content,
    }

# Create workflow
workflow = StateGraph(PlannerState)
workflow.add_node("process_inputs", process_inputs)
workflow.add_node("create_itinerary", create_itinerary)
workflow.set_entry_point("process_inputs")
workflow.add_edge("process_inputs", "create_itinerary")
workflow.add_edge("create_itinerary", END)

app = workflow.compile()

def generate_travel_plan(city: str, interests: List[str]) -> Dict[str, str]:
    """
    Generate a travel itinerary for the given city and interests.
    
    Args:
        city: The destination city
        interests: List of user interests (e.g., ['food', 'history', 'art'])
        
    Returns:
        Dict containing the city, interests, and generated itinerary
    """
    state = {
        "messages": [HumanMessage(content=f"Plan a trip to {city}")],
        "city": city,
        "interests": interests,
        "itinerary": "",
    }
    
    result = app.invoke(state)
    
    return {
        "city": result["city"],
        "interests": result["interests"],
        "itinerary": result["itinerary"]
    }
