import json
import re
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_response(prompt):
    """Generate response from Gemini"""
    try:
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
        response = ""
        for chunk in client.models.generate_content_stream(model=GEMINI_MODEL, contents=contents):
            # CRITICAL FIX: Check if chunk.text is not None before concatenating
            if chunk.text is not None:
                response += chunk.text
            else:
                print(f"⚠️ Gemini chunk returned None text, skipping...")
        return response.strip() if response else "Unable to generate AI response"
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return "Unable to generate AI response due to error"

def review_code_with_ai(file_content, filename, pylint_results=None, coverage_results=None):
    """Review Python code with Gemini AI"""
    
    # Prepare context
    context = f"Filename: {filename}\n"
    
    if pylint_results:
        context += f"PyLint Score: {pylint_results.get('score', 'N/A')}/10\n"
        context += f"Issues Found: {pylint_results.get('total_issues', 0)}\n"
    
    if coverage_results:
        context += f"Test Coverage: {coverage_results.get('coverage_percent', 0)}%\n"
    
    prompt = f"""
    You are an expert Python code reviewer. Analyze this code and provide a comprehensive review.
    
    CONTEXT:
    {context}
    
    CODE TO REVIEW:
    ```python
    {file_content}
    ```
    
    Please provide your review in this exact format:
    
    OVERALL_SCORE: [0.0 to 1.0]
    CONFIDENCE: [0.0 to 1.0]
    
    STRENGTHS:
    • [List 2-3 positive aspects]
    
    ISSUES:
    • [List 2-4 specific issues or improvements needed]
    
    RECOMMENDATIONS:
    • [List 2-4 specific actionable recommendations]
    
    REFACTORING_SUGGESTIONS:
    • [List 1-3 refactoring ideas if applicable]
    
    SECURITY_CONCERNS:
    • [List any security issues or "None identified"]
    
    Focus on code quality, maintainability, performance, and best practices.
    """
    
    response = generate_response(prompt)
    return parse_ai_review(response, filename)

def parse_ai_review(response, filename):
    """Parse Gemini AI review response"""
    try:
        # Extract sections using regex
        overall_score = extract_section(response, r'OVERALL_SCORE:\s*([\d.]+)', float, 0.7)
        confidence = extract_section(response, r'CONFIDENCE:\s*([\d.]+)', float, 0.8)
        
        strengths = extract_list_section(response, r'STRENGTHS:(.*?)(?:ISSUES:|$)')
        issues = extract_list_section(response, r'ISSUES:(.*?)(?:RECOMMENDATIONS:|$)')
        recommendations = extract_list_section(response, r'RECOMMENDATIONS:(.*?)(?:REFACTORING_SUGGESTIONS:|$)')
        refactoring = extract_list_section(response, r'REFACTORING_SUGGESTIONS:(.*?)(?:SECURITY_CONCERNS:|$)')
        security = extract_list_section(response, r'SECURITY_CONCERNS:(.*?)$')
        
        return {
            "filename": filename,
            "overall_score": overall_score,
            "confidence": confidence,
            "strengths": strengths,
            "issues": issues,
            "recommendations": recommendations,
            "refactoring_suggestions": refactoring,
            "security_concerns": security,
            "raw_response": response
        }
        
    except Exception as e:
        print(f"❌ Failed to parse AI review: {e}")
        return create_fallback_ai_review(filename, response)

def extract_section(text, pattern, data_type, default):
    """Extract a single value from text using regex"""
    try:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return data_type(match.group(1))
        return default
    except:
        return default

def extract_list_section(text, pattern):
    """Extract list items from text using regex"""
    try:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1).strip()
            # Extract bullet points
            items = []
            for line in section_text.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    items.append(line[1:].strip())
            return items
        return []
    except:
        return []

def create_fallback_ai_review(filename, raw_response):
    """Create fallback AI review when parsing fails"""
    return {
        "filename": filename,
        "overall_score": 0.7,
        "confidence": 0.6,
        "strengths": ["Code structure appears reasonable"],
        "issues": ["Unable to perform detailed analysis"],
        "recommendations": ["Manual code review recommended"],
        "refactoring_suggestions": [],
        "security_concerns": ["Manual security review needed"],
        "raw_response": raw_response,
        "note": "Fallback review due to parsing error"
    }

def review_multiple_files(files_data, pylint_results=None, coverage_results=None):
    """Review multiple files with AI"""
    reviews = []
    
    for i, file_data in enumerate(files_data):
        filename = file_data.get("filename", "")
        content = file_data.get("content", "")
        
        if content:
            print(f"🤖 AI reviewing {filename}...")
            
            # Get corresponding analysis results
            pylint_result = pylint_results[i] if pylint_results and i < len(pylint_results) else None
            coverage_result = coverage_results[i] if coverage_results and i < len(coverage_results) else None
            
            review = review_code_with_ai(content, filename, pylint_result, coverage_result)
            reviews.append(review)
        else:
            print(f"⚠️ No content for {filename}, skipping AI review...")
    
    return reviews

def generate_pr_summary(pr_details, pylint_results, coverage_results, ai_reviews):
    """Generate overall PR summary with AI"""
    
    # Prepare summary data
    overall_pylint_score = sum(r.get('score', 0) for r in pylint_results) / len(pylint_results) if pylint_results else 0
    overall_coverage = sum(r.get('coverage_percent', 0) for r in coverage_results) / len(coverage_results) if coverage_results else 0
    overall_ai_score = sum(r.get('overall_score', 0) for r in ai_reviews) / len(ai_reviews) if ai_reviews else 0
    
    prompt = f"""
    Generate a comprehensive PR review summary based on the analysis results.
    
    PR DETAILS:
    Title: {pr_details.get('title', 'N/A')}
    Author: {pr_details.get('author', 'N/A')}
    Files Changed: {len(pylint_results) if pylint_results else 0}
    
    ANALYSIS RESULTS:
    PyLint Score: {overall_pylint_score:.2f}/10
    Test Coverage: {overall_coverage:.1f}%
    AI Quality Score: {overall_ai_score:.2f}/1.0
    
    Provide a summary in this format:
    
    OVERALL_RECOMMENDATION: [APPROVE/NEEDS_WORK/REJECT]
    PRIORITY: [HIGH/MEDIUM/LOW]
    
    KEY_FINDINGS:
    • [2-3 most important findings]
    
    ACTION_ITEMS:
    • [2-4 specific actions needed]
    
    APPROVAL_CRITERIA:
    • [What needs to be fixed before approval]
    """
    
    response = generate_response(prompt)
    return parse_pr_summary(response)

def parse_pr_summary(response):
    """Parse PR summary response"""
    try:
        recommendation = extract_section(response, r'OVERALL_RECOMMENDATION:\s*(\w+)', str, "NEEDS_WORK")
        priority = extract_section(response, r'PRIORITY:\s*(\w+)', str, "MEDIUM")
        
        key_findings = extract_list_section(response, r'KEY_FINDINGS:(.*?)(?:ACTION_ITEMS:|$)')
        action_items = extract_list_section(response, r'ACTION_ITEMS:(.*?)(?:APPROVAL_CRITERIA:|$)')
        approval_criteria = extract_list_section(response, r'APPROVAL_CRITERIA:(.*?)$')
        
        return {
            "recommendation": recommendation.upper(),
            "priority": priority.upper(),
            "key_findings": key_findings,
            "action_items": action_items,
            "approval_criteria": approval_criteria,
            "raw_response": response
        }
        
    except Exception as e:
        print(f"❌ Failed to parse PR summary: {e}")
        return {
            "recommendation": "NEEDS_WORK",
            "priority": "MEDIUM",
            "key_findings": ["Analysis completed with limitations"],
            "action_items": ["Manual review recommended"],
            "approval_criteria": ["Address identified issues"],
            "raw_response": response
        }

def determine_critical_issues(pylint_results, coverage_results, ai_reviews):
    """Determine if there are critical issues requiring human review"""
    from config import PYLINT_THRESHOLD, COVERAGE_THRESHOLD, AI_CONFIDENCE_THRESHOLD
    
    # Check PyLint scores
    if pylint_results:
        avg_pylint_score = sum(r.get('score', 0) for r in pylint_results) / len(pylint_results)
        if avg_pylint_score < PYLINT_THRESHOLD:
            return True, f"PyLint score too low: {avg_pylint_score:.2f} < {PYLINT_THRESHOLD}"
    
    # Check coverage
    if coverage_results:
        avg_coverage = sum(r.get('coverage_percent', 0) for r in coverage_results) / len(coverage_results)
        if avg_coverage < COVERAGE_THRESHOLD:
            return True, f"Test coverage too low: {avg_coverage:.1f}% < {COVERAGE_THRESHOLD}%"
    
    # Check AI confidence
    if ai_reviews:
        avg_confidence = sum(r.get('confidence', 0) for r in ai_reviews) / len(ai_reviews)
        if avg_confidence < AI_CONFIDENCE_THRESHOLD:
            return True, f"AI confidence too low: {avg_confidence:.2f} < {AI_CONFIDENCE_THRESHOLD}"
    
    return False, "No critical issues detected"