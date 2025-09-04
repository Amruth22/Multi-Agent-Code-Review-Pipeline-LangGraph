import smtplib
from email.mime.text import MIMEText
from config import EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO, SMTP_SERVER, SMTP_PORT

def send_email(subject, body):
    """Send email notification"""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent: {subject}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def send_review_started_email(pr_details, files_count):
    """Send initial review started notification"""
    subject = f"🔍 Code Review Started: PR #{pr_details.get('pr_number', 'N/A')}"
    body = f"""
CODE REVIEW STARTED
==================
PR Title: {pr_details.get('title', 'N/A')}
Author: {pr_details.get('author', 'N/A')}
Files to Review: {files_count} Python files

Status: Analysis in progress
Next Update: PyLint and coverage analysis results

This is an automated notification from the Smart Code Review Pipeline.
    """
    return send_email(subject, body)

def send_analysis_complete_email(pr_details, pylint_summary, coverage_summary):
    """Send analysis complete notification"""
    subject = f"📊 Analysis Complete: PR #{pr_details.get('pr_number', 'N/A')}"
    body = f"""
STATIC ANALYSIS COMPLETE
=======================
PR Title: {pr_details.get('title', 'N/A')}
Author: {pr_details.get('author', 'N/A')}

PYLINT RESULTS:
{pylint_summary}

COVERAGE RESULTS:
{coverage_summary}

Status: AI review in progress
Next Update: AI recommendations and final report

This is an automated notification from the Smart Code Review Pipeline.
    """
    return send_email(subject, body)

def send_ai_review_complete_email(pr_details, ai_summary):
    """Send AI review complete notification"""
    subject = f"🤖 AI Review Complete: PR #{pr_details.get('pr_number', 'N/A')}"
    body = f"""
AI CODE REVIEW COMPLETE
======================
PR Title: {pr_details.get('title', 'N/A')}
Author: {pr_details.get('author', 'N/A')}

AI REVIEW SUMMARY:
{ai_summary}

Status: Generating final report
Next Update: Final recommendation and action items

This is an automated notification from the Smart Code Review Pipeline.
    """
    return send_email(subject, body)

def send_final_report_email(pr_details, final_report, is_critical):
    """Send final review report"""
    status_emoji = "🔴" if is_critical else "✅"
    status_text = "HUMAN REVIEW REQUIRED" if is_critical else "AUTO-APPROVED"
    
    subject = f"{status_emoji} Final Report: PR #{pr_details.get('pr_number', 'N/A')} - {status_text}"
    body = f"""
FINAL MULTI-AGENT CODE REVIEW REPORT
===================================
PR Title: {pr_details.get('title', 'N/A')}
Author: {pr_details.get('author', 'N/A')}

FINAL STATUS: {status_text}

{final_report}

{'⚠️ IMMEDIATE ATTENTION REQUIRED ⚠️' if is_critical else '✅ REVIEW COMPLETED SUCCESSFULLY'}

This is the final report from the Parallel Multi-Agent Code Review Pipeline.
Analyzed by: Security Agent, Quality Agent, Coverage Agent, AI Review Agent, Documentation Agent
    """
    return send_email(subject, body)

def format_ai_reviews_summary(ai_reviews):
    """Format AI reviews into email-friendly summary"""
    if not ai_reviews:
        return "No AI reviews available"
    
    summary = []
    summary.append("AI REVIEW SUMMARY")
    summary.append("=" * 20)
    
    # Overall scores
    avg_score = sum(r.get('overall_score', 0) for r in ai_reviews) / len(ai_reviews)
    avg_confidence = sum(r.get('confidence', 0) for r in ai_reviews) / len(ai_reviews)
    
    summary.append(f"Average Quality Score: {avg_score:.2f}/1.0")
    summary.append(f"Average Confidence: {avg_confidence:.2f}/1.0")
    summary.append("")
    
    # File-by-file summary
    for review in ai_reviews:
        summary.append(f"File: {review['filename']}")
        summary.append(f"  Quality Score: {review['overall_score']:.2f}/1.0")
        summary.append(f"  Confidence: {review['confidence']:.2f}/1.0")
        
        if review.get('issues'):
            summary.append("  Key Issues:")
            for issue in review['issues'][:2]:  # Top 2 issues
                if issue and issue.strip():  # Filter out empty issues
                    summary.append(f"    • {issue}")
        
        if review.get('recommendations'):
            summary.append("  Top Recommendations:")
            for rec in review['recommendations'][:2]:  # Top 2 recommendations
                if rec and rec.strip():  # Filter out empty recommendations
                    summary.append(f"    • {rec}")
        
        summary.append("")
    
    return "\n".join(summary)

def format_final_report(pr_summary, pylint_results, coverage_results, ai_reviews, security_results=None, documentation_results=None):
    """Format comprehensive final report with all multi-agent results"""
    report = []
    report.append("COMPREHENSIVE MULTI-AGENT CODE REVIEW REPORT")
    report.append("=" * 50)
    
    # Overall recommendation
    report.append(f"RECOMMENDATION: {pr_summary.get('recommendation', 'NEEDS_WORK')}")
    report.append(f"PRIORITY: {pr_summary.get('priority', 'MEDIUM')}")
    report.append("")
    
    # Multi-Agent Analysis Results
    report.append("MULTI-AGENT ANALYSIS RESULTS:")
    report.append("=" * 35)
    
    # Security Analysis
    if security_results:
        total_vulns = sum(len(r.get('vulnerabilities', [])) for r in security_results)
        avg_security_score = sum(r.get('security_score', 0) for r in security_results) / len(security_results)
        high_severity = sum(r.get('severity_counts', {}).get('HIGH', 0) for r in security_results)
        
        report.append(f"🔒 Security Score: {avg_security_score:.2f}/10.0")
        report.append(f"🚨 Total Vulnerabilities: {total_vulns} (High Severity: {high_severity})")
    
    # Quality Analysis
    if pylint_results:
        avg_pylint = sum(r.get('score', 0) for r in pylint_results) / len(pylint_results)
        report.append(f"📊 PyLint Score: {avg_pylint:.2f}/10.0")
    
    # Coverage Analysis
    if coverage_results:
        avg_coverage = sum(r.get('coverage_percent', 0) for r in coverage_results) / len(coverage_results)
        report.append(f"🧪 Test Coverage: {avg_coverage:.1f}%")
    
    # AI Analysis
    if ai_reviews:
        avg_ai_score = sum(r.get('overall_score', 0) for r in ai_reviews) / len(ai_reviews)
        avg_confidence = sum(r.get('confidence', 0) for r in ai_reviews) / len(ai_reviews)
        report.append(f"🤖 AI Quality Score: {avg_ai_score:.2f}/1.0 (Confidence: {avg_confidence:.2f})")
    
    # Documentation Analysis
    if documentation_results:
        avg_doc_coverage = sum(r.get('documentation_coverage', 0) for r in documentation_results) / len(documentation_results)
        total_missing_docs = sum(len(r.get('missing_documentation', [])) for r in documentation_results)
        report.append(f"📚 Documentation Coverage: {avg_doc_coverage:.1f}% (Missing: {total_missing_docs} items)")
    
    report.append("")
    
    # Critical Security Issues (if any)
    if security_results and any(r.get('severity_counts', {}).get('HIGH', 0) > 0 for r in security_results):
        report.append("🚨 CRITICAL SECURITY VULNERABILITIES:")
        for result in security_results:
            for vuln in result.get('vulnerabilities', []):
                if vuln.get('severity') == 'HIGH':
                    report.append(f"• {vuln['description']} (Line {vuln['line']})")
        report.append("")
    
    # Key findings from AI analysis
    if pr_summary.get('key_findings'):
        report.append("KEY FINDINGS:")
        for finding in pr_summary['key_findings']:
            if finding and finding.strip() and finding != '*':  # Filter out empty/invalid findings
                report.append(f"• {finding}")
        report.append("")
    
    # Enhanced action items with multi-agent context
    report.append("ACTION ITEMS:")
    
    # Security-specific actions
    if security_results:
        total_vulns = sum(len(r.get('vulnerabilities', [])) for r in security_results)
        if total_vulns > 0:
            report.append(f"• 🔒 SECURITY: Address {total_vulns} security vulnerabilities immediately")
    
    # Quality-specific actions
    if pylint_results:
        avg_pylint = sum(r.get('score', 0) for r in pylint_results) / len(pylint_results)
        if avg_pylint < 7.0:
            report.append(f"• 📊 QUALITY: Improve PyLint score from {avg_pylint:.2f} to ≥7.0/10.0")
    
    # Coverage-specific actions
    if coverage_results:
        avg_coverage = sum(r.get('coverage_percent', 0) for r in coverage_results) / len(coverage_results)
        if avg_coverage < 80.0:
            report.append(f"• 🧪 TESTING: Increase test coverage from {avg_coverage:.1f}% to ≥80%")
    
    # Documentation-specific actions
    if documentation_results:
        avg_doc_coverage = sum(r.get('documentation_coverage', 0) for r in documentation_results) / len(documentation_results)
        if avg_doc_coverage < 70.0:
            report.append(f"• 📚 DOCUMENTATION: Improve documentation coverage from {avg_doc_coverage:.1f}% to ≥70%")
    
    # AI-specific actions
    if ai_reviews:
        avg_ai_score = sum(r.get('overall_score', 0) for r in ai_reviews) / len(ai_reviews)
        if avg_ai_score < 0.8:
            report.append(f"• 🤖 CODE QUALITY: Address AI-identified issues to improve score from {avg_ai_score:.2f} to ≥0.8")
    
    # Add original action items if they exist and are valid
    if pr_summary.get('action_items'):
        for item in pr_summary['action_items']:
            if item and item.strip() and item != '*':  # Filter out empty/invalid items
                report.append(f"• {item}")
    
    report.append("")
    
    # Enhanced approval criteria
    report.append("APPROVAL CRITERIA:")
    report.append("• Security score must be ≥8.0/10.0 with no high-severity vulnerabilities")
    report.append("• PyLint score must reach ≥7.0/10.0")
    report.append("• Test coverage must achieve ≥80%")
    report.append("• AI quality score must improve to ≥0.8/1.0")
    report.append("• Documentation coverage must reach ≥70%")
    
    # Add original approval criteria if they exist and are valid
    if pr_summary.get('approval_criteria'):
        for criteria in pr_summary['approval_criteria']:
            if criteria and criteria.strip() and criteria != '*':  # Filter out empty/invalid criteria
                report.append(f"• {criteria}")
    
    report.append("")
    
    return "\n".join(report)