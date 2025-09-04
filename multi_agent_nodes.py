#!/usr/bin/env python3
"""
Multi-Agent Nodes for Parallel Code Review System
Each agent specializes in a specific aspect of code review and runs in parallel
"""

from github_service import get_pr_details, get_pr_files, get_file_content
from pylint_service import analyze_multiple_files, format_pylint_summary
from coverage_service import analyze_test_coverage, analyze_missing_tests, format_coverage_summary
from gemini_service import review_multiple_files, generate_pr_summary, determine_critical_issues
from email_service import (
    send_review_started_email, send_analysis_complete_email, 
    send_ai_review_complete_email, send_final_report_email,
    format_ai_reviews_summary, format_final_report
)
from parallel_state import update_parallel_stage, add_agent_completed, add_parallel_email_sent
import re
import ast
import subprocess
import json

def pr_detector_agent(state):
    """Agent 1: PR Detection and File Extraction"""
    print(f"🔍 PR DETECTOR AGENT: {state['review_id']}")
    
    try:
        # Get PR details
        pr_details = get_pr_details(state["repo_owner"], state["repo_name"], state["pr_number"])
        if not pr_details:
            state["error"] = "Failed to fetch PR details"
            state["next"] = "error_handler"
            return state
        
        # Add PR number to details
        pr_details["pr_number"] = state["pr_number"]
        state["pr_details"] = pr_details
        
        # Get changed Python files
        files = get_pr_files(state["repo_owner"], state["repo_name"], state["pr_number"])
        if not files:
            state["error"] = "No Python files found in PR"
            state["next"] = "error_handler"
            return state
        
        # Get file contents from the PR head branch
        pr_head_branch = pr_details.get("head_branch", "main")
        print(f"📁 Fetching files from branch: {pr_head_branch}")
        
        files_with_content = []
        for file_info in files:
            if file_info["status"] != "deleted":  # Skip deleted files
                content = get_file_content(state["repo_owner"], state["repo_name"], file_info["filename"], ref=pr_head_branch)
                if content:
                    file_info["content"] = content
                    files_with_content.append(file_info)
                else:
                    print(f"⚠️ Could not fetch content for {file_info['filename']} from branch {pr_head_branch}")
        
        state["files_data"] = files_with_content
        
        # Send initial email
        send_review_started_email(pr_details, len(files_with_content))
        state = add_parallel_email_sent(state, "review_started")
        
        # Set up for parallel agent execution
        state = update_parallel_stage(state, "parallel_analysis")
        state["next"] = "parallel_agents"  # This will trigger parallel execution
        
        print(f"✅ PR detected: {len(files_with_content)} Python files to review")
        print(f"🚀 Launching parallel agents: Security, Quality, Coverage, AI Review")
        return state
        
    except Exception as e:
        print(f"❌ PR detector error: {e}")
        state["error"] = str(e)
        state["next"] = "error_handler"
        return state

def security_analysis_agent(state):
    """Agent 2: Security Vulnerability Analysis (Specialized Agent)"""
    print(f"🔒 SECURITY ANALYSIS AGENT: {state['review_id']}")
    
    try:
        security_results = []
        
        for file_data in state["files_data"]:
            filename = file_data.get("filename", "")
            content = file_data.get("content", "")
            
            if content:
                print(f"🔍 Security scanning {filename}...")
                
                # Security vulnerability detection
                security_issues = detect_security_vulnerabilities(content, filename)
                
                security_results.append({
                    "filename": filename,
                    "security_score": security_issues["security_score"],
                    "vulnerabilities": security_issues["vulnerabilities"],
                    "severity_counts": security_issues["severity_counts"],
                    "recommendations": security_issues["recommendations"]
                })
        
        # CRITICAL: Only update fields specific to this agent
        return {
            "security_results": security_results,
            "agents_completed": ["security"]
        }
        
    except Exception as e:
        print(f"❌ Security agent error: {e}")
        return {
            "security_results": [],
            "agents_completed": ["security"]
        }

def quality_analysis_agent(state):
    """Agent 3: Code Quality Analysis (PyLint + Custom Rules)"""
    print(f"📊 QUALITY ANALYSIS AGENT: {state['review_id']}")
    
    try:
        # Run PyLint analysis
        pylint_results = analyze_multiple_files(state["files_data"])
        
        # Add custom quality metrics
        enhanced_quality_results = []
        for i, result in enumerate(pylint_results):
            file_data = state["files_data"][i] if i < len(state["files_data"]) else {}
            content = file_data.get("content", "")
            
            # Add custom quality metrics
            custom_metrics = analyze_code_complexity(content, result["filename"])
            
            enhanced_result = {
                **result,
                "complexity_score": custom_metrics["complexity_score"],
                "maintainability_index": custom_metrics["maintainability_index"],
                "code_smells": custom_metrics["code_smells"],
                "technical_debt": custom_metrics["technical_debt"]
            }
            enhanced_quality_results.append(enhanced_result)
        
        print(f"✅ Quality analysis complete - {len(enhanced_quality_results)} files analyzed")
        
        # CRITICAL: Only update fields specific to this agent
        return {
            "pylint_results": enhanced_quality_results,
            "agents_completed": ["quality"]
        }
        
    except Exception as e:
        print(f"❌ Quality agent error: {e}")
        return {
            "pylint_results": [],
            "agents_completed": ["quality"]
        }

def coverage_analysis_agent(state):
    """Agent 4: Test Coverage Analysis"""
    print(f"🧪 COVERAGE ANALYSIS AGENT: {state['review_id']}")
    
    try:
        # Run coverage analysis
        coverage_results = analyze_test_coverage(state["files_data"])
        missing_tests = analyze_missing_tests(state["files_data"], coverage_results)
        
        # Enhanced coverage analysis
        enhanced_coverage_results = []
        for i, result in enumerate(coverage_results):
            file_data = state["files_data"][i] if i < len(state["files_data"]) else {}
            content = file_data.get("content", "")
            
            # Add test quality metrics
            test_metrics = analyze_test_quality(content, result["filename"])
            
            enhanced_result = {
                **result,
                "test_quality_score": test_metrics["test_quality_score"],
                "missing_test_types": test_metrics["missing_test_types"],
                "testability_score": test_metrics["testability_score"]
            }
            enhanced_coverage_results.append(enhanced_result)
        
        print(f"✅ Coverage analysis complete - {len(enhanced_coverage_results)} files analyzed")
        
        # CRITICAL: Only update fields specific to this agent
        return {
            "coverage_results": enhanced_coverage_results,
            "missing_tests": missing_tests,
            "agents_completed": ["coverage"]
        }
        
    except Exception as e:
        print(f"❌ Coverage agent error: {e}")
        return {
            "coverage_results": [],
            "missing_tests": [],
            "agents_completed": ["coverage"]
        }

def ai_review_agent(state):
    """Agent 5: AI-Powered Code Review (Gemini 2.0 Flash)"""
    print(f"🤖 AI REVIEW AGENT: {state['review_id']}")
    
    try:
        # Get results from other agents (if available)
        pylint_results = state.get("pylint_results", [])
        coverage_results = state.get("coverage_results", [])
        security_results = state.get("security_results", [])
        
        # Run AI reviews with enhanced context
        ai_reviews = []
        for i, file_data in enumerate(state["files_data"]):
            filename = file_data.get("filename", "")
            content = file_data.get("content", "")
            
            if content:
                print(f"🤖 AI reviewing {filename}...")
                
                # Get corresponding analysis results
                pylint_result = pylint_results[i] if i < len(pylint_results) else None
                coverage_result = coverage_results[i] if i < len(coverage_results) else None
                security_result = security_results[i] if i < len(security_results) else None
                
                # Enhanced AI review with multi-agent context
                ai_review = review_code_with_enhanced_ai(
                    content, filename, pylint_result, coverage_result, security_result
                )
                ai_reviews.append(ai_review)
        
        print(f"✅ AI review complete - {len(ai_reviews)} files analyzed")
        
        # CRITICAL: Only update fields specific to this agent
        return {
            "ai_reviews": ai_reviews,
            "agents_completed": ["ai_review"]
        }
        
    except Exception as e:
        print(f"❌ AI review agent error: {e}")
        return {
            "ai_reviews": [],
            "agents_completed": ["ai_review"]
        }

def documentation_agent(state):
    """Agent 6: Documentation Analysis and Generation"""
    print(f"📚 DOCUMENTATION AGENT: {state['review_id']}")
    
    try:
        documentation_results = []
        
        for file_data in state["files_data"]:
            filename = file_data.get("filename", "")
            content = file_data.get("content", "")
            
            if content:
                print(f"📝 Analyzing documentation for {filename}...")
                
                doc_analysis = analyze_documentation_quality(content, filename)
                documentation_results.append(doc_analysis)
        
        print(f"✅ Documentation analysis complete - {len(documentation_results)} files analyzed")
        
        # CRITICAL: Only update fields specific to this agent
        return {
            "documentation_results": documentation_results,
            "agents_completed": ["documentation"]
        }
        
    except Exception as e:
        print(f"❌ Documentation agent error: {e}")
        return {
            "documentation_results": [],
            "agents_completed": ["documentation"]
        }

def agent_coordinator(state):
    """Coordinator: Aggregate results from all parallel agents"""
    print(f"🎯 AGENT COORDINATOR: {state['review_id']}")
    
    try:
        # Log current agent completion status
        completed_agents = state.get("agents_completed", [])
        print(f"📊 Agents completed: {completed_agents}")
        
        # Note: Waiting logic is handled in route_after_coordination
        # This function only runs when called, routing decides when to proceed
        
        print(f"✅ Coordinator processing results...")
        
        # Generate comprehensive PR summary with all agent results
        pr_summary = generate_multi_agent_pr_summary(
            state.get("pr_details", {}),
            state.get("pylint_results", []),
            state.get("coverage_results", []),
            state.get("ai_reviews", []),
            state.get("security_results", []),
            state.get("documentation_results", [])
        )
        
        print(f"✅ Agent coordination complete - All results aggregated")
        
        # CRITICAL: Return only coordinator-specific updates
        return {
            "pr_summary": pr_summary,
            "stage": "coordination_complete",
            "next": "decision_maker",
            "updated_at": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        print(f"❌ Coordinator error: {e}")
        return {
            "error": str(e),
            "next": "error_handler",
            "stage": "coordination_error",
            "updated_at": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# Helper functions for specialized analysis

def detect_security_vulnerabilities(code, filename):
    """Detect security vulnerabilities in code"""
    vulnerabilities = []
    security_score = 10.0
    
    # Check for common security issues
    security_patterns = [
        (r'eval\s*\(', 'HIGH', 'Use of eval() - Code injection risk'),
        (r'exec\s*\(', 'HIGH', 'Use of exec() - Code execution risk'),
        (r'subprocess.*shell\s*=\s*True', 'HIGH', 'Shell injection vulnerability'),
        (r'pickle\.loads?\s*\(', 'MEDIUM', 'Unsafe deserialization with pickle'),
        (r'input\s*\(.*\)', 'LOW', 'Unvalidated user input'),
        (r'open\s*\([^)]*[\'"]w[\'"]', 'MEDIUM', 'File write operations'),
        (r'requests\..*verify\s*=\s*False', 'MEDIUM', 'SSL verification disabled'),
        (r'password\s*=\s*[\'"][^\'"]+[\'"]', 'HIGH', 'Hardcoded password'),
        (r'api_key\s*=\s*[\'"][^\'"]+[\'"]', 'HIGH', 'Hardcoded API key'),
    ]
    
    for pattern, severity, description in security_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE)
        for match in matches:
            line_num = code[:match.start()].count('\n') + 1
            vulnerabilities.append({
                'line': line_num,
                'severity': severity,
                'description': description,
                'code_snippet': match.group()
            })
            
            # Reduce security score based on severity
            if severity == 'HIGH':
                security_score -= 2.0
            elif severity == 'MEDIUM':
                security_score -= 1.0
            else:
                security_score -= 0.5
    
    security_score = max(0.0, security_score)
    
    severity_counts = {
        'HIGH': len([v for v in vulnerabilities if v['severity'] == 'HIGH']),
        'MEDIUM': len([v for v in vulnerabilities if v['severity'] == 'MEDIUM']),
        'LOW': len([v for v in vulnerabilities if v['severity'] == 'LOW'])
    }
    
    recommendations = []
    if severity_counts['HIGH'] > 0:
        recommendations.append("Address high-severity security vulnerabilities immediately")
    if severity_counts['MEDIUM'] > 0:
        recommendations.append("Review and fix medium-severity security issues")
    if len(vulnerabilities) == 0:
        recommendations.append("No obvious security vulnerabilities detected")
    
    return {
        'security_score': security_score,
        'vulnerabilities': vulnerabilities,
        'severity_counts': severity_counts,
        'recommendations': recommendations
    }

def analyze_code_complexity(code, filename):
    """Analyze code complexity and maintainability"""
    try:
        tree = ast.parse(code)
        
        # Count various complexity metrics
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Calculate complexity score
        complexity_score = 10.0
        code_smells = []
        
        # Check for long functions
        for func in functions:
            func_lines = func.end_lineno - func.lineno if hasattr(func, 'end_lineno') else 0
            if func_lines > 50:
                complexity_score -= 1.0
                code_smells.append(f"Function '{func.name}' is too long ({func_lines} lines)")
        
        # Check for too many parameters
        for func in functions:
            param_count = len(func.args.args)
            if param_count > 7:
                complexity_score -= 0.5
                code_smells.append(f"Function '{func.name}' has too many parameters ({param_count})")
        
        maintainability_index = max(0, complexity_score * 10)
        technical_debt = len(code_smells) * 0.5
        
        return {
            'complexity_score': max(0.0, complexity_score),
            'maintainability_index': maintainability_index,
            'code_smells': code_smells,
            'technical_debt': technical_debt
        }
        
    except Exception:
        return {
            'complexity_score': 5.0,
            'maintainability_index': 50.0,
            'code_smells': ['Unable to analyze code complexity'],
            'technical_debt': 1.0
        }

def analyze_test_quality(code, filename):
    """Analyze test quality and coverage gaps"""
    test_quality_score = 5.0
    missing_test_types = []
    
    # Check if this is a test file
    if 'test' in filename.lower():
        test_quality_score = 8.0
        
        # Check for different types of tests
        if 'unittest' not in code and 'pytest' not in code:
            missing_test_types.append('Unit tests')
        if 'mock' not in code and 'Mock' not in code:
            missing_test_types.append('Mock tests')
        if 'integration' not in code.lower():
            missing_test_types.append('Integration tests')
    else:
        # Non-test file - check if it has corresponding tests
        missing_test_types = ['Unit tests', 'Integration tests', 'Mock tests']
    
    testability_score = 10.0 - len(missing_test_types) * 2.0
    
    return {
        'test_quality_score': test_quality_score,
        'missing_test_types': missing_test_types,
        'testability_score': max(0.0, testability_score)
    }

def analyze_documentation_quality(code, filename):
    """Analyze documentation quality"""
    try:
        tree = ast.parse(code)
        
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        total_items = len(functions) + len(classes)
        documented_items = 0
        
        # Check for docstrings
        for node in functions + classes:
            if (ast.get_docstring(node) is not None):
                documented_items += 1
        
        documentation_coverage = (documented_items / total_items * 100) if total_items > 0 else 100
        
        missing_docs = []
        for func in functions:
            if not ast.get_docstring(func):
                missing_docs.append(f"Function '{func.name}' missing docstring")
        
        for cls in classes:
            if not ast.get_docstring(cls):
                missing_docs.append(f"Class '{cls.name}' missing docstring")
        
        return {
            'filename': filename,
            'documentation_coverage': documentation_coverage,
            'missing_documentation': missing_docs,
            'total_items': total_items,
            'documented_items': documented_items
        }
        
    except Exception:
        return {
            'filename': filename,
            'documentation_coverage': 0,
            'missing_documentation': ['Unable to analyze documentation'],
            'total_items': 0,
            'documented_items': 0
        }

def review_code_with_enhanced_ai(content, filename, pylint_result=None, coverage_result=None, security_result=None):
    """Enhanced AI review with multi-agent context"""
    from gemini_service import review_code_with_ai
    
    # Use the existing AI review function but with enhanced context
    ai_review = review_code_with_ai(content, filename, pylint_result, coverage_result)
    
    # Add security context if available
    if security_result:
        ai_review['security_context'] = {
            'security_score': security_result.get('security_score', 0),
            'vulnerability_count': len(security_result.get('vulnerabilities', [])),
            'high_severity_issues': security_result.get('severity_counts', {}).get('HIGH', 0)
        }
    
    return ai_review

def generate_multi_agent_pr_summary(pr_details, pylint_results, coverage_results, ai_reviews, security_results, documentation_results):
    """Generate comprehensive PR summary from all agents"""
    from gemini_service import generate_pr_summary
    
    # Use existing PR summary generation as base
    base_summary = generate_pr_summary(pr_details, pylint_results, coverage_results, ai_reviews)
    
    # Enhance with multi-agent results
    if security_results:
        total_vulnerabilities = sum(len(result.get('vulnerabilities', [])) for result in security_results)
        high_severity_count = sum(result.get('severity_counts', {}).get('HIGH', 0) for result in security_results)
        
        base_summary['security_analysis'] = {
            'total_vulnerabilities': total_vulnerabilities,
            'high_severity_count': high_severity_count,
            'security_recommendation': 'CRITICAL' if high_severity_count > 0 else 'REVIEW' if total_vulnerabilities > 0 else 'APPROVED'
        }
    
    if documentation_results:
        avg_doc_coverage = sum(result.get('documentation_coverage', 0) for result in documentation_results) / len(documentation_results)
        base_summary['documentation_analysis'] = {
            'average_coverage': avg_doc_coverage,
            'documentation_recommendation': 'NEEDS_IMPROVEMENT' if avg_doc_coverage < 70 else 'GOOD'
        }
    
    return base_summary