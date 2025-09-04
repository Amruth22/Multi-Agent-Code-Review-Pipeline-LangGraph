#!/usr/bin/env python3
"""
Local File Review for Parallel Multi-Agent System
Simplified local file analysis using parallel agents
"""

from pylint_service import analyze_multiple_files, format_pylint_summary
from coverage_service import analyze_test_coverage, format_coverage_summary
from multi_agent_nodes import (
    detect_security_vulnerabilities, analyze_documentation_quality,
    analyze_code_complexity
)
from gemini_service import review_multiple_files
from email_service import format_ai_reviews_summary

def review_local_files(file_paths):
    """Review local Python files using parallel multi-agent analysis"""
    print("🚀 STARTING LOCAL FILE REVIEW - PARALLEL MULTI-AGENT")
    print(f"📁 Files: {', '.join(file_paths)}")
    print("=" * 70)
    
    try:
        # Prepare file data
        files_data = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                files_data.append({
                    "filename": file_path,
                    "content": content
                })
            except Exception as e:
                print(f"⚠️ Failed to read {file_path}: {e}")
        
        if not files_data:
            print("❌ No files to analyze")
            return None
        
        print(f"🎯 Analyzing {len(files_data)} files with parallel multi-agent system...")
        print("🚀 Launching agents: Security, Quality, Coverage, AI Review, Documentation")
        
        # Run parallel analysis (simulated for local files)
        print("\n🔒 Security Analysis Agent...")
        security_results = []
        for file_data in files_data:
            security_analysis = detect_security_vulnerabilities(
                file_data["content"], file_data["filename"]
            )
            security_results.append({
                "filename": file_data["filename"],
                **security_analysis
            })
        
        print("📊 Quality Analysis Agent...")
        pylint_results = analyze_multiple_files(files_data)
        
        # Add complexity metrics
        enhanced_quality_results = []
        for i, result in enumerate(pylint_results):
            file_data = files_data[i] if i < len(files_data) else {}
            content = file_data.get("content", "")
            
            complexity_metrics = analyze_code_complexity(content, result["filename"])
            enhanced_result = {
                **result,
                **complexity_metrics
            }
            enhanced_quality_results.append(enhanced_result)
        
        print("🧪 Coverage Analysis Agent...")
        coverage_results = analyze_test_coverage(files_data)
        
        print("📚 Documentation Analysis Agent...")
        documentation_results = []
        for file_data in files_data:
            doc_analysis = analyze_documentation_quality(
                file_data["content"], file_data["filename"]
            )
            documentation_results.append(doc_analysis)
        
        print("🤖 AI Review Agent...")
        ai_reviews = review_multiple_files(files_data, enhanced_quality_results, coverage_results)
        
        # Print comprehensive results
        print("\n" + "=" * 70)
        print("🎯 PARALLEL MULTI-AGENT ANALYSIS RESULTS")
        print("=" * 70)
        
        # Security Results
        print("\n🔒 SECURITY ANALYSIS:")
        total_vulnerabilities = sum(len(result.get('vulnerabilities', [])) for result in security_results)
        avg_security_score = sum(result.get('security_score', 0) for result in security_results) / len(security_results)
        print(f"Total Vulnerabilities: {total_vulnerabilities}")
        print(f"Average Security Score: {avg_security_score:.2f}/10.0")
        
        for result in security_results:
            print(f"  {result['filename']}: {result['security_score']:.1f}/10.0 ({len(result.get('vulnerabilities', []))} vulnerabilities)")
        
        # Quality Results
        print("\n📊 QUALITY ANALYSIS:")
        print(format_pylint_summary(enhanced_quality_results))
        
        # Coverage Results
        print("\n🧪 COVERAGE ANALYSIS:")
        print(format_coverage_summary(coverage_results, []))
        
        # Documentation Results
        print("\n📚 DOCUMENTATION ANALYSIS:")
        avg_doc_coverage = sum(result.get('documentation_coverage', 0) for result in documentation_results) / len(documentation_results)
        print(f"Average Documentation Coverage: {avg_doc_coverage:.1f}%")
        
        for result in documentation_results:
            print(f"  {result['filename']}: {result['documentation_coverage']:.1f}% ({result['documented_items']}/{result['total_items']} items)")
        
        # AI Review Results
        print("\n🤖 AI REVIEW:")
        print(format_ai_reviews_summary(ai_reviews))
        
        # Overall Assessment
        print("\n" + "=" * 70)
        print("🎯 OVERALL ASSESSMENT")
        print("=" * 70)
        
        # Check thresholds
        avg_pylint = sum(result.get('score', 0) for result in enhanced_quality_results) / len(enhanced_quality_results)
        avg_coverage = sum(result.get('coverage_percent', 0) for result in coverage_results) / len(coverage_results)
        avg_ai_score = sum(review.get('overall_score', 0) for review in ai_reviews) / len(ai_reviews)
        
        print(f"PyLint Score: {avg_pylint:.2f}/10.0 {'✅' if avg_pylint >= 7.0 else '❌'}")
        print(f"Test Coverage: {avg_coverage:.1f}% {'✅' if avg_coverage >= 80.0 else '❌'}")
        print(f"AI Quality Score: {avg_ai_score:.2f}/1.0 {'✅' if avg_ai_score >= 0.8 else '❌'}")
        print(f"Security Score: {avg_security_score:.2f}/10.0 {'✅' if avg_security_score >= 8.0 else '❌'}")
        print(f"Documentation Coverage: {avg_doc_coverage:.1f}% {'✅' if avg_doc_coverage >= 70.0 else '❌'}")
        
        # Final recommendation
        critical_issues = []
        if avg_security_score < 8.0:
            critical_issues.append("Security vulnerabilities detected")
        if avg_pylint < 7.0:
            critical_issues.append("Code quality below threshold")
        if avg_coverage < 80.0:
            critical_issues.append("Insufficient test coverage")
        if avg_ai_score < 0.8:
            critical_issues.append("AI identified significant issues")
        if avg_doc_coverage < 70.0:
            critical_issues.append("Poor documentation coverage")
        
        if critical_issues:
            print(f"\n🔴 RECOMMENDATION: NEEDS IMPROVEMENT")
            print("Issues found:")
            for issue in critical_issues:
                print(f"  • {issue}")
        else:
            print(f"\n✅ RECOMMENDATION: CODE QUALITY ACCEPTABLE")
            print("All quality thresholds met!")
        
        return {
            "files_analyzed": len(files_data),
            "security_results": security_results,
            "pylint_results": enhanced_quality_results,
            "coverage_results": coverage_results,
            "documentation_results": documentation_results,
            "ai_reviews": ai_reviews,
            "overall_recommendation": "NEEDS_IMPROVEMENT" if critical_issues else "APPROVED"
        }
        
    except Exception as e:
        print(f"❌ Local file review failed: {e}")
        return None