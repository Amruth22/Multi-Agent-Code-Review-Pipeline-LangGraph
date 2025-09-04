#!/usr/bin/env python3
"""
Parallel Multi-Agent Code Review Workflow
LangGraph orchestration with specialized agents working in parallel
"""

from langgraph.graph import StateGraph, END
from multi_agent_nodes import (
    pr_detector_agent, security_analysis_agent, quality_analysis_agent,
    coverage_analysis_agent, ai_review_agent, documentation_agent,
    agent_coordinator
)
from workflow_nodes import decision_maker_node, report_generator_node, error_handler_node
from parallel_state import ParallelReviewState, create_parallel_review_state, check_all_agents_completed
from github_service import parse_repo_url

def create_review_workflow():
    """Create the parallel multi-agent code review workflow"""
    
    print("🏗️ Building Parallel Multi-Agent Workflow...")
    
    # Create workflow graph with proper state schema
    workflow = StateGraph(ParallelReviewState)
    
    # Add specialized agent nodes
    workflow.add_node("pr_detector", pr_detector_agent)
    workflow.add_node("security_agent", security_analysis_agent)
    workflow.add_node("quality_agent", quality_analysis_agent)
    workflow.add_node("coverage_agent", coverage_analysis_agent)
    workflow.add_node("ai_review_agent", ai_review_agent)
    workflow.add_node("documentation_agent", documentation_agent)
    workflow.add_node("agent_coordinator", agent_coordinator)
    workflow.add_node("decision_maker", decision_maker_node)
    workflow.add_node("report_generator", report_generator_node)
    workflow.add_node("error_handler", error_handler_node)
    
    # Set entry point
    workflow.set_entry_point("pr_detector")
    
    # Define parallel agent routing logic
    def route_to_parallel_agents(state):
        """Route to parallel agents after PR detection"""
        next_step = state.get("next", "end")
        
        if next_step == "parallel_agents":
            # Launch all agents in parallel
            return ["security_agent", "quality_agent", "coverage_agent", "ai_review_agent", "documentation_agent"]
        elif next_step == "error_handler":
            return "error_handler"
        else:
            return END
    
    def route_after_coordination(state):
        """Route after coordination is complete"""
        # Check if all agents have completed before proceeding
        expected_agents = ["security", "quality", "coverage", "ai_review", "documentation"]
        completed_agents = state.get("agents_completed", [])
        
        if not all(agent in completed_agents for agent in expected_agents):
            missing_agents = [agent for agent in expected_agents if agent not in completed_agents]
            print(f"⏳ Coordinator waiting for agents: {missing_agents}")
            return END  # Wait for more agents
        
        # All agents completed, proceed based on next step
        next_step = state.get("next", "end")
        
        if next_step == "decision_maker":
            return "decision_maker"
        elif next_step == "error_handler":
            return "error_handler"
        else:
            return END
    
    def route_after_decision(state):
        """Route after decision making"""
        next_step = state.get("next", "end")
        
        if next_step == "report_generator":
            return "report_generator"
        elif next_step == "error_handler":
            return "error_handler"
        else:
            return END
    
    def route_final(state):
        """Final routing logic"""
        next_step = state.get("next", "end")
        
        if next_step == "end":
            return END
        elif next_step == "error_handler":
            return "error_handler"
        else:
            return END
    
    # Add conditional edges for parallel execution
    workflow.add_conditional_edges("pr_detector", route_to_parallel_agents)
    
    # All parallel agents always route to coordinator
    # Coordinator will handle checking if all agents are complete
    workflow.add_edge("security_agent", "agent_coordinator")
    workflow.add_edge("quality_agent", "agent_coordinator")
    workflow.add_edge("coverage_agent", "agent_coordinator")
    workflow.add_edge("ai_review_agent", "agent_coordinator")
    workflow.add_edge("documentation_agent", "agent_coordinator")
    
    # Coordinator routes to decision maker only when all agents complete
    workflow.add_conditional_edges("agent_coordinator", route_after_coordination)
    
    # Decision maker routes to report generator
    workflow.add_conditional_edges("decision_maker", route_after_decision)
    
    # Report generator ends workflow
    workflow.add_conditional_edges("report_generator", route_final)
    
    # Error handler always ends
    workflow.add_edge("error_handler", END)
    
    print("✅ Parallel Multi-Agent Workflow Created")
    print("🎯 Agents: PR Detector → [Security, Quality, Coverage, AI Review, Documentation] → Coordinator → Decision → Report")
    
    return workflow.compile()

def review_pull_request(repo_url, pr_number):
    """Review a pull request using parallel multi-agent workflow"""
    
    print(f"🚀 STARTING PARALLEL MULTI-AGENT CODE REVIEW WORKFLOW")
    print(f"📥 Repository: {repo_url}")
    print(f"📥 PR Number: {pr_number}")
    print("=" * 70)
    
    try:
        # Parse repository URL
        repo_owner, repo_name = parse_repo_url(repo_url)
        if not repo_owner or not repo_name:
            print("❌ Invalid repository URL format")
            return None
        
        # Create initial state for parallel execution
        state = create_parallel_review_state(repo_owner, repo_name, pr_number)
        
        # Create and run parallel multi-agent workflow
        workflow = create_review_workflow()
        print("🎯 Using Parallel Multi-Agent Architecture")
        
        # Execute workflow
        print(f"⚡ Executing PARALLEL MULTI-AGENT workflow...")
        final_state = workflow.invoke(state)
        
        print("=" * 70)
        print("🏁 WORKFLOW COMPLETED")
        print(f"📋 Review: {final_state['review_id']}")
        print(f"📊 Status: {final_state['stage'].upper()}")
        print(f"🏗️ Architecture: PARALLEL MULTI-AGENT")
        
        # Display agent completion status
        if "agents_completed" in final_state:
            completed_agents = final_state["agents_completed"]
            print(f"🤖 Agents Completed: {', '.join(set(completed_agents))}")
        
        if final_state.get("has_critical_issues"):
            print(f"🔴 Critical Issues: {final_state.get('critical_reason', 'Unknown')}")
        else:
            print("✅ No critical issues found")
        
        print(f"📧 Emails Sent: {len(final_state.get('emails_sent', []))}")
        
        # Display enhanced results
        display_parallel_results(final_state)
        
        return final_state
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def display_parallel_results(final_state):
    """Display results from parallel agents"""
    print("\n" + "=" * 70)
    print("🎯 PARALLEL AGENT RESULTS SUMMARY")
    print("=" * 70)
    
    # Security Results
    security_results = final_state.get("security_results", [])
    if security_results:
        total_vulns = sum(len(result.get('vulnerabilities', [])) for result in security_results)
        print(f"🔒 Security Agent: {len(security_results)} files analyzed, {total_vulns} vulnerabilities found")
    
    # Quality Results
    pylint_results = final_state.get("pylint_results", [])
    if pylint_results:
        avg_score = sum(result.get('score', 0) for result in pylint_results) / len(pylint_results)
        print(f"📊 Quality Agent: {len(pylint_results)} files analyzed, avg score: {avg_score:.2f}/10.0")
    
    # Coverage Results
    coverage_results = final_state.get("coverage_results", [])
    if coverage_results:
        avg_coverage = sum(result.get('coverage_percent', 0) for result in coverage_results) / len(coverage_results)
        print(f"🧪 Coverage Agent: {len(coverage_results)} files analyzed, avg coverage: {avg_coverage:.1f}%")
    
    # AI Review Results
    ai_reviews = final_state.get("ai_reviews", [])
    if ai_reviews:
        avg_ai_score = sum(review.get('overall_score', 0) for review in ai_reviews) / len(ai_reviews)
        print(f"🤖 AI Review Agent: {len(ai_reviews)} files analyzed, avg score: {avg_ai_score:.2f}/1.0")
    
    # Documentation Results
    doc_results = final_state.get("documentation_results", [])
    if doc_results:
        avg_doc_coverage = sum(result.get('documentation_coverage', 0) for result in doc_results) / len(doc_results)
        print(f"📚 Documentation Agent: {len(doc_results)} files analyzed, avg coverage: {avg_doc_coverage:.1f}%")
    
    print("=" * 70)

if __name__ == "__main__":
    # Demo execution
    print("🎬 Parallel Multi-Agent Workflow Demo")
    
    # Example usage
    repo_url = "https://github.com/Amruth22/lung-disease-prediction-yolov10"
    pr_number = 1
    
    # Run parallel multi-agent workflow
    result = review_pull_request(repo_url, pr_number)