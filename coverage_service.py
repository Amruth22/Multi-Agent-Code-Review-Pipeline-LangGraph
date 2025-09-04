import subprocess
import json
import tempfile
import os
import ast

def analyze_test_coverage(files_data, test_files=None):
    """Analyze test coverage for Python files"""
    try:
        # Create temporary directory for analysis
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write files to temp directory
            file_paths = []
            for file_data in files_data:
                filename = file_data.get("filename", "temp.py")
                content = file_data.get("content", "")
                
                # Create file path
                file_path = os.path.join(temp_dir, os.path.basename(filename))
                
                with open(file_path, 'w') as f:
                    f.write(content)
                file_paths.append(file_path)
            
            # Create simple test file if none provided
            if not test_files:
                test_content = create_basic_test_file(files_data)
                test_path = os.path.join(temp_dir, "test_generated.py")
                with open(test_path, 'w') as f:
                    f.write(test_content)
            
            # Run pytest with coverage
            try:
                result = subprocess.run([
                    'python', '-m', 'pytest', 
                    '--cov=' + temp_dir,
                    '--cov-report=json',
                    '--cov-report=term-missing',
                    temp_dir
                ], capture_output=True, text=True, timeout=30, cwd=temp_dir)
                
                # Try to read coverage.json
                coverage_file = os.path.join(temp_dir, 'coverage.json')
                if os.path.exists(coverage_file):
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                    return parse_coverage_data(coverage_data, files_data)
                else:
                    return create_fallback_coverage(files_data)
                    
            except subprocess.TimeoutExpired:
                print("⚠️ Coverage analysis timeout")
                return create_fallback_coverage(files_data)
                
    except Exception as e:
        print(f"❌ Coverage analysis failed: {e}")
        return create_fallback_coverage(files_data)

def create_basic_test_file(files_data):
    """Create a basic test file for coverage analysis"""
    test_content = """
import pytest
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

def test_basic_import():
    \"\"\"Basic test to check if files can be imported\"\"\"
    try:
"""
    
    for file_data in files_data:
        filename = file_data.get("filename", "")
        if filename.endswith(".py"):
            module_name = os.path.basename(filename).replace(".py", "")
            test_content += f"        import {module_name}\n"
    
    test_content += """        assert True
    except ImportError as e:
        pytest.skip(f"Import failed: {e}")

def test_placeholder():
    \"\"\"Placeholder test\"\"\"
    assert True
"""
    
    return test_content

def parse_coverage_data(coverage_data, files_data):
    """Parse coverage.json data into readable format"""
    results = []
    
    for file_data in files_data:
        filename = file_data.get("filename", "")
        
        # Find matching coverage data
        file_coverage = None
        for file_path, data in coverage_data.get("files", {}).items():
            if filename in file_path or os.path.basename(filename) in file_path:
                file_coverage = data
                break
        
        if file_coverage:
            summary = file_coverage.get("summary", {})
            results.append({
                "filename": filename,
                "coverage_percent": summary.get("percent_covered", 0),
                "lines_covered": summary.get("covered_lines", 0),
                "lines_total": summary.get("num_statements", 0),
                "missing_lines": file_coverage.get("missing_lines", []),
                "has_tests": True
            })
        else:
            results.append(create_file_fallback_coverage(filename))
    
    return results

def create_file_fallback_coverage(filename):
    """Create fallback coverage data for a single file"""
    return {
        "filename": filename,
        "coverage_percent": 0,
        "lines_covered": 0,
        "lines_total": count_lines_in_file(filename),
        "missing_lines": [],
        "has_tests": False,
        "note": "No coverage data available"
    }

def create_fallback_coverage(files_data):
    """Create fallback coverage data when analysis fails"""
    return [create_file_fallback_coverage(f.get("filename", "")) for f in files_data]

def count_lines_in_file(filename):
    """Estimate number of lines in file"""
    try:
        # This is a rough estimate since we don't have the actual file
        return 50  # Default estimate
    except:
        return 0

def analyze_missing_tests(files_data, coverage_results):
    """Analyze what tests are missing based on code structure"""
    missing_tests = []
    
    for i, file_data in enumerate(files_data):
        filename = file_data.get("filename", "")
        content = file_data.get("content", "")
        
        if content:
            functions = extract_functions_from_code(content)
            classes = extract_classes_from_code(content)
            
            coverage_result = coverage_results[i] if i < len(coverage_results) else {}
            coverage_percent = coverage_result.get("coverage_percent", 0)
            
            missing_tests.append({
                "filename": filename,
                "functions": functions,
                "classes": classes,
                "coverage_percent": coverage_percent,
                "needs_tests": coverage_percent < 80
            })
    
    return missing_tests

def extract_functions_from_code(code):
    """Extract function names from Python code"""
    try:
        tree = ast.parse(code)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):  # Skip private functions
                    functions.append(node.name)
        
        return functions
    except:
        return []

def extract_classes_from_code(code):
    """Extract class names from Python code"""
    try:
        tree = ast.parse(code)
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        return classes
    except:
        return []

def get_overall_coverage_score(coverage_results):
    """Calculate overall coverage percentage"""
    if not coverage_results:
        return 0.0
    
    total_lines = sum(result.get("lines_total", 0) for result in coverage_results)
    covered_lines = sum(result.get("lines_covered", 0) for result in coverage_results)
    
    if total_lines == 0:
        return 0.0
    
    return round((covered_lines / total_lines) * 100, 2)

def format_coverage_summary(coverage_results, missing_tests):
    """Format coverage results into readable summary"""
    summary = []
    summary.append("TEST COVERAGE ANALYSIS")
    summary.append("=" * 30)
    
    overall_coverage = get_overall_coverage_score(coverage_results)
    summary.append(f"Overall Coverage: {overall_coverage}%")
    summary.append("")
    
    for i, result in enumerate(coverage_results):
        summary.append(f"File: {result['filename']}")
        summary.append(f"  Coverage: {result['coverage_percent']}%")
        summary.append(f"  Lines: {result['lines_covered']}/{result['lines_total']}")
        
        if i < len(missing_tests):
            missing = missing_tests[i]
            if missing['functions']:
                summary.append(f"  Functions: {', '.join(missing['functions'])}")
            if missing['classes']:
                summary.append(f"  Classes: {', '.join(missing['classes'])}")
            
            if missing['needs_tests']:
                summary.append("  ⚠️ Needs more test coverage")
        
        summary.append("")
    
    return "\n".join(summary)