import subprocess
import json
import tempfile
import os

def analyze_code_with_pylint(file_content, filename="temp.py"):
    """Analyze Python code with PyLint"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Run pylint with JSON output
            result = subprocess.run([
                'pylint', 
                '--output-format=json',
                '--disable=C0114,C0115,C0116',  # Disable missing docstring warnings
                temp_file_path
            ], capture_output=True, text=True, timeout=30)
            
            # Parse JSON output
            if result.stdout:
                try:
                    issues = json.loads(result.stdout)
                except json.JSONDecodeError:
                    issues = []
            else:
                issues = []
            
            # Get overall score from stderr (pylint prints score there)
            score = extract_pylint_score(result.stderr)
            
            return {
                "filename": filename,
                "score": score,
                "issues": issues,
                "total_issues": len(issues),
                "error_count": len([i for i in issues if i.get("type") == "error"]),
                "warning_count": len([i for i in issues if i.get("type") == "warning"]),
                "convention_count": len([i for i in issues if i.get("type") == "convention"])
            }
            
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
            
    except subprocess.TimeoutExpired:
        print(f"⚠️ PyLint timeout for {filename}")
        return create_fallback_analysis(filename)
    except Exception as e:
        print(f"❌ PyLint analysis failed for {filename}: {e}")
        return create_fallback_analysis(filename)

def extract_pylint_score(stderr_output):
    """Extract PyLint score from stderr output"""
    try:
        for line in stderr_output.split('\n'):
            if 'Your code has been rated at' in line:
                # Extract score like "Your code has been rated at 8.50/10"
                parts = line.split('rated at')[1].split('/')[0].strip()
                return float(parts)
        return 5.0  # Default score if not found
    except:
        return 5.0

def create_fallback_analysis(filename):
    """Create fallback analysis when PyLint fails"""
    return {
        "filename": filename,
        "score": 5.0,
        "issues": [],
        "total_issues": 0,
        "error_count": 0,
        "warning_count": 0,
        "convention_count": 0,
        "note": "Analysis failed, using default values"
    }

def analyze_multiple_files(files_data):
    """Analyze multiple Python files"""
    results = []
    
    for file_data in files_data:
        filename = file_data.get("filename", "unknown.py")
        content = file_data.get("content", "")
        
        if content:
            print(f"🔍 Analyzing {filename} with PyLint...")
            analysis = analyze_code_with_pylint(content, filename)
            results.append(analysis)
        else:
            print(f"⚠️ No content for {filename}, skipping...")
    
    return results

def get_overall_quality_score(pylint_results):
    """Calculate overall quality score from PyLint results"""
    if not pylint_results:
        return 0.0
    
    total_score = sum(result["score"] for result in pylint_results)
    average_score = total_score / len(pylint_results)
    
    return round(average_score, 2)

def format_pylint_summary(pylint_results):
    """Format PyLint results into readable summary"""
    if not pylint_results:
        return "No PyLint analysis results available"
    
    summary = []
    summary.append("PYLINT ANALYSIS SUMMARY")
    summary.append("=" * 30)
    
    overall_score = get_overall_quality_score(pylint_results)
    summary.append(f"Overall Score: {overall_score}/10.0")
    summary.append("")
    
    for result in pylint_results:
        summary.append(f"File: {result['filename']}")
        summary.append(f"  Score: {result['score']}/10.0")
        summary.append(f"  Issues: {result['total_issues']} (Errors: {result['error_count']}, Warnings: {result['warning_count']})")
        
        # Show top 3 issues
        if result['issues']:
            summary.append("  Top Issues:")
            for issue in result['issues'][:3]:
                summary.append(f"    - Line {issue.get('line', '?')}: {issue.get('message', 'Unknown issue')}")
        summary.append("")
    
    return "\n".join(summary)