from github_service import get_pr_details, get_pr_files, get_file_content
from pylint_service import analyze_multiple_files, format_pylint_summary
from coverage_service import analyze_test_coverage, analyze_missing_tests, format_coverage_summary
from gemini_service import review_multiple_files, generate_pr_summary, determine_critical_issues
from email_service import (
    send_review_started_email, send_analysis_complete_email, 
    send_ai_review_complete_email, send_final_report_email,
    format_ai_reviews_summary, format_final_report
)
from parallel_state import update_parallel_stage, add_parallel_email_sent

# Backward compatibility functions for legacy nodes
def update_stage(state, new_stage):
    """Backward compatibility wrapper for update_parallel_stage"""
    return update_parallel_stage(state, new_stage)

def add_email_sent(state, email_type):
    """Backward compatibility wrapper for add_parallel_email_sent"""
    return add_parallel_email_sent(state, email_type)

def pr_detector_node(state):
    """Node 1: Detect and fetch PR details"""
    print(f"🔍 PR DETECTOR: {state['review_id']}")
    
    try:
        # Get PR details
        pr_details = get_pr_details(state["repo_owner"], state["repo_name"], state["pr_number"])
        if not pr_details:
            state["error"] = "Failed to fetch PR details"
            state["next"] = "error"
            return state
        
        # Add PR number to details
        pr_details["pr_number"] = state["pr_number"]
        state["pr_details"] = pr_details
        
        # Get changed Python files
        files = get_pr_files(state["repo_owner"], state["repo_name"], state["pr_number"])
        if not files:
            state["error"] = "No Python files found in PR"
            state["next"] = "error"
            return state
        
        # Get file contents from the PR head branch (not main!)
        pr_head_branch = pr_details.get("head_branch", "main")
        print(f"📁 Fetching files from branch: {pr_head_branch}")
        
        files_with_content = []
        for file_info in files:
            if file_info["status"] != "deleted":  # Skip deleted files
                # CRITICAL FIX: Use PR head branch instead of main
                content = get_file_content(state["repo_owner"], state["repo_name"], file_info["filename"], ref=pr_head_branch)
                if content:
                    file_info["content"] = content
                    files_with_content.append(file_info)
                else:
                    print(f"⚠️ Could not fetch content for {file_info['filename']} from branch {pr_head_branch}")
        
        state["files_data"] = files_with_content
        
        # Send initial email
        send_review_started_email(pr_details, len(files_with_content))
        add_email_sent(state, "review_started")
        
        state = update_stage(state, "analyzing")
        state["next"] = "code_analyzer"
        
        print(f"✅ PR detected: {len(files_with_content)} Python files to review")
        return state
        
    except Exception as e:
        print(f"❌ PR detector error: {e}")
        state["error"] = str(e)
        state["next"] = "error"
        return state

def code_analyzer_node(state):
    """Node 2: Analyze code with PyLint"""
    print(f"🐍 CODE ANALYZER: {state['review_id']}")
    
    try:
        # Run PyLint analysis
        pylint_results = analyze_multiple_files(state["files_data"])
        state["pylint_results"] = pylint_results
        
        # Run coverage analysis
        coverage_results = analyze_test_coverage(state["files_data"])
        missing_tests = analyze_missing_tests(state["files_data"], coverage_results)
        state["coverage_results"] = coverage_results
        state["missing_tests"] = missing_tests
        
        # Format summaries
        pylint_summary = format_pylint_summary(pylint_results)
        coverage_summary = format_coverage_summary(coverage_results, missing_tests)
        
        # Send analysis email
        send_analysis_complete_email(state["pr_details"], pylint_summary, coverage_summary)
        # Use regular add_email_sent for sequential workflow compatibility
        if "agents_completed" in state:
            state = add_parallel_email_sent(state, "analysis_complete")
        else:
            add_email_sent(state, "analysis_complete")
        
        state = update_stage(state, "ai_reviewing")
        state["next"] = "ai_reviewer"
        
        print(f"✅ Code analysis complete")
        return state
        
    except Exception as e:
        print(f"❌ Code analyzer error: {e}")
        state["error"] = str(e)
        state["next"] = "error"
        return state

def ai_reviewer_node(state):
    """Node 3: AI code review with Gemini"""
    print(f"🤖 AI REVIEWER: {state['review_id']}")
    
    try:
        # Run AI reviews
        ai_reviews = review_multiple_files(
            state["files_data"], 
            state["pylint_results"], 
            state["coverage_results"]
        )
        state["ai_reviews"] = ai_reviews
        
        # Generate PR summary
        pr_summary = generate_pr_summary(
            state["pr_details"],
            state["pylint_results"],
            state["coverage_results"],
            ai_reviews
        )
        state["pr_summary"] = pr_summary
        
        # Send AI review email
        ai_summary = format_ai_reviews_summary(ai_reviews)
        send_ai_review_complete_email(state["pr_details"], ai_summary)
        # Use regular add_email_sent for sequential workflow compatibility
        if "agents_completed" in state:
            state = add_parallel_email_sent(state, "ai_review_complete")
        else:
            add_email_sent(state, "ai_review_complete")
        
        state = update_stage(state, "evaluating")
        state["next"] = "decision_maker"
        
        print(f"✅ AI review complete")
        return state
        
    except Exception as e:
        print(f"❌ AI reviewer error: {e}")
        state["error"] = str(e)
        state["next"] = "error"
        return state

def decision_maker_node(state):
    """Node 4: Make final decision"""
    print(f"⚖️ DECISION MAKER: {state['review_id']}")
    
    try:
        # Check for critical issues
        has_critical, critical_reason = determine_critical_issues(
            state["pylint_results"],
            state["coverage_results"], 
            state["ai_reviews"]
        )
        
        state["has_critical_issues"] = has_critical
        state["critical_reason"] = critical_reason
        
        if has_critical:
            # Use appropriate update function based on state type
            if "agents_completed" in state:
                state = update_parallel_stage(state, "needs_human_review")
            else:
                state = update_stage(state, "needs_human_review")
            state["next"] = "report_generator"
            print(f"🔴 Critical issues found: {critical_reason}")
        else:
            # Use appropriate update function based on state type
            if "agents_completed" in state:
                state = update_parallel_stage(state, "approved")
            else:
                state = update_stage(state, "approved")
            state["next"] = "report_generator"
            print(f"✅ No critical issues, auto-approved")
        
        return state
        
    except Exception as e:
        print(f"❌ Decision maker error: {e}")
        state["error"] = str(e)
        state["next"] = "error"
        return state

def report_generator_node(state):
    """Node 5: Generate final report"""
    print(f"📧 REPORT GENERATOR: {state['review_id']}")
    
    try:
        # Generate final report with all multi-agent results
        final_report = format_final_report(
            state["pr_summary"],
            state["pylint_results"],
            state["coverage_results"],
            state["ai_reviews"],
            state.get("security_results", []),
            state.get("documentation_results", [])
        )
        
        # Send final email
        send_final_report_email(
            state["pr_details"], 
            final_report, 
            state["has_critical_issues"]
        )
        # Use appropriate email function based on state type
        if "agents_completed" in state:
            state = add_parallel_email_sent(state, "final_report")
        else:
            add_email_sent(state, "final_report")
        
        # Final status
        if state["has_critical_issues"]:
            # Use appropriate update function based on state type
            if "agents_completed" in state:
                state = update_parallel_stage(state, "escalated")
            else:
                state = update_stage(state, "escalated")
            print(f"🔴 REVIEW ESCALATED: {state['review_id']}")
            print(f"   Reason: {state['critical_reason']}")
        else:
            # Use appropriate update function based on state type
            if "agents_completed" in state:
                state = update_parallel_stage(state, "completed")
            else:
                state = update_stage(state, "completed")
            print(f"✅ REVIEW COMPLETED: {state['review_id']}")
            print(f"   Status: Auto-approved")
        
        state["workflow_complete"] = True
        state["next"] = "end"
        
        return state
        
    except Exception as e:
        print(f"❌ Report generator error: {e}")
        state["error"] = str(e)
        state["next"] = "error"
        return state

def error_handler_node(state):
    """Handle workflow errors"""
    print(f"❌ ERROR HANDLER: {state['review_id']}")
    
    error_msg = state.get("error", "Unknown error occurred")
    print(f"   Error: {error_msg}")
    
    # Try to send error notification
    try:
        from email_service import send_email
        subject = f"❌ Code Review Error: PR #{state.get('pr_number', 'N/A')}"
        body = f"""
CODE REVIEW ERROR
================
Review ID: {state['review_id']}
PR Number: {state.get('pr_number', 'N/A')}
Stage: {state.get('stage', 'Unknown')}

ERROR: {error_msg}

Manual review required.
        """
        send_email(subject, body)
        from parallel_state import add_parallel_email_sent
        state = add_parallel_email_sent(state, "error_notification")
    except:
        print("⚠️ Failed to send error notification email")
    
    # Use appropriate update function based on state type
    if "agents_completed" in state:
        state = update_parallel_stage(state, "error")
    else:
        state = update_stage(state, "error")
    state["workflow_complete"] = True
    
    return state