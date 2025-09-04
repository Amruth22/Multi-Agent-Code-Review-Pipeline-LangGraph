# 🔍 Smart Code Review Pipeline - Parallel Multi-Agent System

Automated code review system using **LangGraph Multi-Agent Orchestration** + **Gemini 2.0 Flash** + **GitHub API** + **Gmail** for comprehensive Python code analysis with specialized agents working in parallel.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Interactive mode (Parallel Multi-Agent)
python main.py

# Review GitHub PR (Parallel Multi-Agent)
python main.py --pr https://github.com/user/repo 123

# Review local files (Multi-Agent Analysis)
python main.py --files src/main.py src/utils.py

# Run demo (Parallel Multi-Agent Demo)
python main.py demo
```

## 🤖 Parallel Multi-Agent Workflow

1. **PR Detector Agent** → Fetch PR details and extract Python files
2. **Parallel Agent Execution** → 5 specialized agents working simultaneously:
   - 🔒 **Security Analysis Agent** → Vulnerability detection and security scoring
   - 📊 **Quality Analysis Agent** → PyLint + complexity metrics + code smells
   - 🧪 **Coverage Analysis Agent** → Test coverage + missing test identification
   - 🤖 **AI Review Agent** → Gemini 2.0 Flash with cross-agent context
   - 📚 **Documentation Agent** → Docstring coverage + API documentation
3. **Agent Coordinator** → Aggregate and correlate all agent results
4. **Decision Maker** → Multi-dimensional threshold evaluation
5. **Report Generator** → Comprehensive email report with all agent findings

## 📧 Email Notifications

- **🔍 Review Started**: PR analysis initiated
- **📊 Analysis Complete**: PyLint + coverage results
- **🤖 AI Review Complete**: Gemini recommendations
- **✅/🔴 Final Report**: Approval or escalation decision

## 🎯 Enhanced Quality Thresholds

- **PyLint Score**: ≥ 7.0/10.0
- **Test Coverage**: ≥ 80%
- **AI Confidence**: ≥ 0.8
- **Security Score**: ≥ 8.0/10.0 (NEW)
- **Documentation Coverage**: ≥ 70% (NEW)

## 🔧 Multi-Dimensional Conditional Branching

- **All thresholds met** → Auto-approve
- **Security issues (< 8.0 or high-severity vulnerabilities)** → Critical escalation
- **Quality issues (PyLint < 7.0, Coverage < 80%, AI < 0.8)** → Human review required
- **Documentation issues (< 70% coverage)** → Documentation review
- **Critical vulnerabilities (eval, exec, shell injection)** → Immediate escalation

## 📊 Features

### **🔗 GitHub Integration**
- Real PR analysis via GitHub API
- Changed files detection
- Python file filtering
- Content extraction

### **🐍 Static Analysis**
- PyLint code quality scoring
- Code smell detection
- Complexity analysis
- Best practices validation

### **🧪 Test Coverage**
- pytest coverage analysis
- Missing test identification
- Function/class coverage mapping
- Coverage percentage calculation

### **🤖 AI Code Review**
- Gemini 2.0 Flash intelligent analysis
- Code improvement suggestions
- Security vulnerability detection
- Refactoring recommendations
- Confidence scoring

### **📧 Email Reports**
- Gmail SMTP integration
- Stage-by-stage notifications
- Comprehensive final reports
- Critical issue alerts

## 📁 Project Structure

```
smart-code-review/
├── main.py                    # CLI application
├── config.py                  # Configuration settings
├── github_service.py          # GitHub API integration
├── pylint_service.py          # PyLint analysis
├── coverage_service.py        # Test coverage analysis
├── gemini_service.py          # AI code review
├── email_service.py           # Gmail notifications
├── review_state.py            # State management
├── workflow_nodes.py          # LangGraph nodes
├── review_workflow.py         # Main workflow
└── requirements.txt           # Dependencies
```

## ⚙️ Configuration

The application uses environment variables for secure credential management. Configuration is loaded from a `.env` file:

### 🔧 Environment Setup

1. **Copy the template file:**
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` with your credentials:**
   ```bash
   # GitHub API Configuration
   GITHUB_TOKEN=your_github_token_here
   
   # Email Configuration
   EMAIL_FROM=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password-here
   EMAIL_TO=recipient@gmail.com
   
   # Gemini AI Configuration
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Validate configuration:**
   ```python
   from config import validate_config
   validate_config()  # Check if all required variables are set
   ```

**Security Note:** Never commit your `.env` file to version control. It's already included in `.gitignore`.

### 📧 Gmail App Password Setup

To enable email notifications, you need to create a Google App Password:

1. **Enable 2-Factor Authentication**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already enabled

2. **Generate App Password**
   - Visit [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" as the app
   - Select "Other" as the device and enter "Code Review Pipeline"
   - Click "Generate"

3. **Copy the Generated Password**
   - Google will display a 16-character password
   - Copy this password (it won't be shown again)

4. **Update config.py**
   ```python
   EMAIL_FROM = "your-email@gmail.com"
   EMAIL_PASSWORD = "your-16-char-app-password"  # Use app password, not regular password
   EMAIL_TO = "recipient@gmail.com"
   ```

**Important**: Use the App Password, not your regular Gmail password, for SMTP authentication.

### 🔑 GitHub Personal Access Token Setup

To access GitHub repositories and PRs, you need to create a fine-grained personal access token:

1. **Navigate to Developer Settings**
   - Go to [GitHub Settings](https://github.com/settings/profile)
   - Click on "Developer settings" in the left sidebar
   - Select "Personal access tokens" → "Fine-grained tokens"

2. **Generate New Token**
   - Click "Generate new token"
   - Enter a descriptive name: "Code Review Pipeline"
   - Set expiration (recommended: 90 days for security)
   - Select resource owner (your account or organization)

3. **Configure Repository Access**
   - Choose "Selected repositories" for security
   - Select the repositories you want to analyze
   - Or choose "All repositories" if needed

4. **Set Required Permissions**
   - **Repository permissions:**
     - Contents: Read (to access file contents)
     - Metadata: Read (to access repository info)
     - Pull requests: Read (to access PR details)
   - **Account permissions:** None required

5. **Generate and Copy Token**
   - Click "Generate token"
   - Copy the generated token immediately (it won't be shown again)
   - Token format: `github_pat_11XXXXXXXXXX...`

6. **Update config.py**
   ```python
   GITHUB_TOKEN = "github_pat_11XXXXXXXXXX..."  # Your fine-grained token
   GITHUB_API_URL = "https://api.github.com"
   ```

**Security Notes:**
- Fine-grained tokens are more secure than classic tokens
- Set appropriate expiration dates and renew regularly
- Only grant minimum required permissions

### 🤖 Gemini API Key Setup

To enable AI-powered code review, you need to create a Google Gemini API key:

1. **Visit Google AI Studio**
   - Open your web browser
   - Go to [Google AI Studio](https://aistudio.google.com)
   - Sign in with your Google account

2. **Navigate to API Key Section**
   - Look at the left sidebar in Google AI Studio
   - Click on "Get API Key" (usually near the top-left corner)
   - You'll see the API Key management interface

3. **Create New API Key**
   - Click the "Create API Key" button
   - A pop-up will appear with project options:
     - Select "Create API Key in new project" (recommended)
     - Or choose an existing Google Cloud project if you have one
   - Click "Create" to generate the key

4. **Copy the Generated API Key**
   - Once created, the API key will appear on screen
   - Click the "Copy" button next to the key
   - **Important**: Save it immediately in a secure location
   - The key won't be shown again for security reasons
   - Key format: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

5. **Update config.py**
   ```python
   GEMINI_API_KEY = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Your Gemini API key
   GEMINI_MODEL = "gemini-2.0-flash"
   ```

6. **Verify API Access**
   - Test the API key by running a simple code review
   - Check your usage in [Google AI Studio](https://aistudio.google.com)
   - Monitor your API quota and usage limits

**Important Notes:**
- Gemini API has free tier limits - monitor your usage
- Keep your API key secure and never commit it to version control
- Consider setting up billing alerts in Google Cloud Console
- Free tier may have rate limits - upgrade if needed for production use
- Never commit tokens to version control

## 🎬 Demo Scenarios

1. **Sample Code Review** - Analyze generated Python code
2. **GitHub PR Review** - Real repository PR analysis

## 📊 Usage Examples

### **GitHub PR Review**
```bash
python main.py --pr https://github.com/django/django 15234
```

### **Local Files Review**
```bash
python main.py --files app.py utils.py models.py
```

### **Interactive Mode**
```bash
python main.py
# Follow prompts for PR or file selection
```

## 🔍 What Gets Analyzed

- **Code Quality**: PyLint scoring, code smells, complexity
- **Test Coverage**: Missing tests, coverage percentages
- **AI Review**: Improvement suggestions, security issues
- **Best Practices**: Python conventions, maintainability
- **Performance**: Optimization opportunities

## 📈 Success Metrics

- **Automated Quality Scoring**: PyLint + AI combined scores
- **Coverage Analysis**: Identify untested code paths
- **Smart Recommendations**: AI-powered improvement suggestions
- **Conditional Approval**: Automatic vs human review decisions
- **Email Workflow**: Complete notification pipeline

## 🧪 Testing

```bash
# Test individual components
python github_service.py
python pylint_service.py
python gemini_service.py

# Run demo scenarios
python main.py demo
```

**Simple, intelligent, and automated code review!** 🎉