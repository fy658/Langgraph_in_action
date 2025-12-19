"""
FastAPI backend for Customer Support Agent
Connects the Vue3 frontend to the LangGraph workflow
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import sys
import os

# Add parent directory to path to import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from customer_support_agent_langgraph import run_customer_support, app as langgraph_app

# Create FastAPI app
api = FastAPI(
    title="Customer Support Agent API",
    description="API for interacting with the LangGraph Customer Support Agent",
    version="1.0.0"
)

# Configure CORS for Vue frontend
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    """Request model for customer queries"""
    query: str

class QueryResponse(BaseModel):
    """Response model for processed queries"""
    query: str
    category: str
    sentiment: str
    response: str
    status: str = "success"

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str

@api.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(status="healthy", message="Customer Support Agent API is running")

@api.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", message="Service is operational")

@api.post("/api/chat", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a customer query through the LangGraph workflow.
    
    - Categorizes the query (Technical, Billing, General)
    - Analyzes sentiment (Positive, Neutral, Negative)
    - Routes to appropriate handler or escalates if negative
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Process through LangGraph
        result = run_customer_support(request.query)
        
        return QueryResponse(
            query=request.query,
            category=result["category"],
            sentiment=result["sentiment"],
            response=result["response"],
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/categories")
async def get_categories():
    """Get available query categories"""
    return {
        "categories": ["Technical", "Billing", "General"],
        "description": {
            "Technical": "Technical support issues like connectivity, software problems",
            "Billing": "Billing inquiries, payment issues, receipts",
            "General": "General questions about services, business hours, etc."
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000, reload=True)
