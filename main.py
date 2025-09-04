#!/usr/bin/env python3
"""
Smart Code Review Pipeline
Parallel Multi-Agent implementation with LangGraph + Gemini 2.0 Flash + GitHub API + Gmail
Specialized agents working in parallel for comprehensive code analysis
"""

import sys
import os
from review_workflow import review_pull_request
from local_file_review import review_local_files

def main():
    """Main application entry point"""
    
    if len(sys.argv) == 1:
        # Interactive mode
        interactive_mode()
    
    elif len(sys.argv) == 2:
        arg = sys.argv[1].lower()
        
        if arg == "help":
            print_help()
        elif arg == "demo":
            run_demo()
        else:
            print("❌ Invalid argument. Use 'help' for usage information.")
    
    elif len(sys.argv) >= 4 and sys.argv[1].lower() == "--pr":
        # Review specific PR using parallel multi-agent workflow
        # python main.py --pr <repo_url> <pr_number>
        repo_url = sys.argv[2]
        try:
            pr_number = int(sys.argv[3])
            print("🎯 Using Parallel Multi-Agent Workflow")
            review_pull_request(repo_url, pr_number)
        except ValueError:
            print("❌ PR number must be an integer")
    
    elif len(sys.argv) >= 3 and sys.argv[1].lower() == "--files":
        # Review local files: python main.py --files file1.py file2.py
        file_paths = sys.argv[2:]
        
        # Check if files exist
        valid_files = []
        for file_path in file_paths:
            if os.path.exists(file_path) and file_path.endswith('.py'):
                valid_files.append(file_path)
            else:
                print(f"⚠️ Skipping {file_path} (not found or not a Python file)")
        
        if valid_files:
            review_local_files(valid_files)
        else:
            print("❌ No valid Python files to review")
    
    else:
        print("❌ Invalid arguments. Use 'help' for usage information.")

def interactive_mode():
    """Interactive mode for code review"""
    print("🔍 Smart Code Review Pipeline - Parallel Multi-Agent Mode")
    print("=" * 60)
    print("1. Review GitHub PR (Parallel Multi-Agent)")
    print("2. Review Local Files")
    print("3. Run Demo")
    print("0. Exit")
    
    choice = input("\nSelect option (0-3): ")
    
    if choice == "0":
        print("👋 Goodbye!")
        return
    
    elif choice == "1":
        repo_url = input("Enter GitHub repository URL: ").strip()
        pr_number_str = input("Enter PR number: ").strip()
        
        try:
            pr_number = int(pr_number_str)
            print("🎯 Using Parallel Multi-Agent Workflow")
            review_pull_request(repo_url, pr_number)
        except ValueError:
            print("❌ Invalid PR number")
    
    elif choice == "2":
        file_paths_str = input("Enter Python file paths (space-separated): ").strip()
        if file_paths_str:
            file_paths = file_paths_str.split()
            valid_files = [f for f in file_paths if os.path.exists(f) and f.endswith('.py')]
            
            if valid_files:
                review_local_files(valid_files)
            else:
                print("❌ No valid Python files found")
        else:
            print("❌ No files specified")
    
    elif choice == "3":
        run_demo()
    
    else:
        print("❌ Invalid choice")

def run_demo():
    """Run demo with sample scenarios"""
    print("🎬 DEMO MODE - Smart Code Review Pipeline")
    print("=" * 50)
    
    demo_scenarios = [
        {
            "name": "Sample Python Function Review",
            "description": "Review a simple Python function with potential issues"
        },
        {
            "name": "GitHub PR Review",
            "description": "Review a real GitHub PR (requires valid repo and PR number)"
        }
    ]
    
    print("Available Demo Scenarios:")
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   {scenario['description']}")
    
    choice = input(f"\nSelect demo scenario (1-{len(demo_scenarios)}): ")
    
    try:
        choice_num = int(choice)
        
        if choice_num == 1:
            run_sample_code_demo()
        elif choice_num == 2:
            run_github_pr_demo()
        else:
            print("❌ Invalid choice")
    
    except ValueError:
        print("❌ Invalid input")

def run_sample_code_demo():
    """Demo with sample Python code"""
    print("\n🎬 Running Sample Code Demo...")
    
    # Create sample Python file
    sample_code = '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total

def process_order(order_data):
    if not order_data:
        return None
    
    items = order_data.get('items', [])
    total = calculate_total(items)
    
    # Apply discount
    discount = order_data.get('discount', 0)
    final_total = total - (total * discount / 100)
    
    return {
        'order_id': order_data.get('id'),
        'total': final_total,
        'items_count': len(items)
    }

class OrderProcessor:
    def __init__(self):
        self.processed_orders = []
    
    def add_order(self, order):
        result = process_order(order)
        if result:
            self.processed_orders.append(result)
        return result
'''
    
    # Write to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(sample_code)
        temp_file_path = temp_file.name
    
    try:
        print(f"📁 Analyzing sample code: {temp_file_path}")
        review_local_files([temp_file_path])
    finally:
        # Clean up
        os.unlink(temp_file_path)

def run_github_pr_demo():
    """Demo with GitHub PR"""
    print("\n🎬 Running GitHub PR Demo...")
    print("Note: This requires a valid GitHub repository and PR number")
    
    # Example repositories (you can modify these)
    example_repos = [
        "https://github.com/Amruth22/lung-disease-prediction-yolov10 (Demo PR with flawed code)",
        "https://github.com/python/cpython",
        "https://github.com/django/django",
        "https://github.com/pallets/flask"
    ]
    
    print("\nExample repositories:")
    for repo in example_repos:
        print(f"  - {repo}")
    
    repo_url = input("\nEnter repository URL: ").strip()
    pr_number_str = input("Enter PR number: ").strip()
    
    if repo_url and pr_number_str:
        try:
            pr_number = int(pr_number_str)
            print("🎯 Running Parallel Multi-Agent Demo")
            review_pull_request(repo_url, pr_number)
        except ValueError:
            print("❌ Invalid PR number")
    else:
        print("❌ Repository URL and PR number required")

def print_help():
    """Print help information"""
    print("""
Smart Code Review Pipeline - Parallel Multi-Agent System
=======================================================

Usage:
  python main.py                                    # Interactive mode
  python main.py --pr <repo_url> <pr_number>       # Review GitHub PR
  python main.py --files <file1.py> <file2.py>     # Review local files
  python main.py demo                               # Run demo scenarios
  python main.py help                               # Show this help

Examples:
  python main.py --pr https://github.com/user/repo 123
  python main.py --files src/main.py src/utils.py
  python main.py demo

Parallel Multi-Agent Architecture:
• 🔒 Security Analysis Agent - Vulnerability detection and security scoring
• 📊 Quality Analysis Agent - PyLint + custom complexity metrics
• 🧪 Coverage Analysis Agent - Test coverage + quality assessment
• 🤖 AI Review Agent - Gemini 2.0 Flash intelligent analysis
• 📚 Documentation Agent - Documentation coverage and quality
• 🎯 Agent Coordinator - Aggregates and coordinates all agent results

Key Features:
• Parallel agent execution for comprehensive analysis
• GitHub PR analysis with API integration
• Multi-dimensional quality assessment
• AI-powered code review with cross-agent context
• Gmail email notifications with escalation alerts
• LangGraph multi-agent orchestration
• Conditional branching with specialized routing

Quality Thresholds:
• PyLint Score: ≥ 7.0/10.0
• Test Coverage: ≥ 80%
• AI Confidence: ≥ 0.8
• Security Score: ≥ 8.0/10.0
• Documentation Coverage: ≥ 70%

The system automatically determines if human review is required based on these thresholds.
Specialized agents provide enhanced analysis with security vulnerability detection and documentation quality assessment.
    """)

if __name__ == "__main__":
    main()