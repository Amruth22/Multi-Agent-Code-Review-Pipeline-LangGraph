#!/usr/bin/env python3
"""
Parallel State Management for Multi-Agent Code Review
Handles concurrent state updates from multiple agents using LangGraph annotations
"""

from typing import TypedDict, List, Dict, Any, Annotated
import operator
from datetime import datetime
import uuid

# Define custom reducer for adding to lists
def add_to_list(existing: List, new: List) -> List:
    """Reducer function to safely add items to a list"""
    if existing is None:
        existing = []
    if new is None:
        new = []
    return existing + new

class ParallelReviewState(TypedDict):
    """State schema for parallel multi-agent code review"""
    
    # Basic review information
    review_id: str
    repo_owner: str
    repo_name: str
    pr_number: int
    timestamp: str
    stage: str
    
    # PR and file data
    pr_details: Dict[str, Any]
    files_data: List[Dict[str, Any]]
    
    # Agent completion tracking - allows multiple concurrent updates
    agents_completed: Annotated[List[str], add_to_list]
    
    # Agent results - each agent updates its own key
    security_results: List[Dict[str, Any]]
    pylint_results: List[Dict[str, Any]]
    coverage_results: List[Dict[str, Any]]
    ai_reviews: List[Dict[str, Any]]
    documentation_results: List[Dict[str, Any]]
    missing_tests: List[Dict[str, Any]]
    
    # Coordination and decision
    pr_summary: Dict[str, Any]
    has_critical_issues: bool
    critical_reason: str
    
    # Email tracking - allows multiple concurrent updates
    emails_sent: Annotated[List[Dict[str, Any]], add_to_list]
    
    # Workflow control
    next: str
    error: str
    workflow_complete: bool
    updated_at: str

def create_parallel_review_state(repo_owner: str, repo_name: str, pr_number: int) -> ParallelReviewState:
    """Create initial state for parallel multi-agent review"""
    review_id = f"REV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    return ParallelReviewState(
        review_id=review_id,
        repo_owner=repo_owner,
        repo_name=repo_name,
        pr_number=pr_number,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        stage="started",
        
        pr_details={},
        files_data=[],
        
        agents_completed=[],
        
        security_results=[],
        pylint_results=[],
        coverage_results=[],
        ai_reviews=[],
        documentation_results=[],
        missing_tests=[],
        
        pr_summary={},
        has_critical_issues=False,
        critical_reason="",
        
        emails_sent=[],
        
        next="",
        error="",
        workflow_complete=False,
        updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

def update_parallel_stage(state: ParallelReviewState, new_stage: str) -> ParallelReviewState:
    """Update review stage with timestamp"""
    state["stage"] = new_stage
    state["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return state

def add_agent_completed(state: ParallelReviewState, agent_name: str) -> ParallelReviewState:
    """Add agent to completed list - this will be merged automatically"""
    # The Annotated[List[str], add] will handle merging multiple agent completions
    state["agents_completed"] = [agent_name]
    return state

def add_parallel_email_sent(state: ParallelReviewState, email_type: str) -> ParallelReviewState:
    """Track emails sent - allows concurrent updates"""
    email_entry = {
        "type": email_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # The Annotated[List[Dict], add] will handle merging multiple email entries
    state["emails_sent"] = [email_entry]
    return state

def check_all_agents_completed(state: ParallelReviewState) -> bool:
    """Check if all expected agents have completed"""
    expected_agents = {"security", "quality", "coverage", "ai_review", "documentation"}
    completed_agents = set(state.get("agents_completed", []))
    return expected_agents.issubset(completed_agents)

def get_parallel_review_summary(state: ParallelReviewState) -> str:
    """Get brief review summary for parallel execution"""
    completed_count = len(state.get("agents_completed", []))
    return f"Review {state['review_id']}: PR #{state['pr_number']} - {state['stage']} ({completed_count} agents completed)"