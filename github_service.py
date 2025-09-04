import requests
from config import GITHUB_TOKEN, GITHUB_API_URL

def get_pr_details(repo_owner, repo_name, pr_number):
    """Get PR details from GitHub API"""
    try:
        url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        pr_data = response.json()
        return {
            "title": pr_data["title"],
            "description": pr_data["body"] or "",
            "author": pr_data["user"]["login"],
            "state": pr_data["state"],
            "created_at": pr_data["created_at"],
            "head_branch": pr_data["head"]["ref"],
            "head_sha": pr_data["head"]["sha"],
            "base_branch": pr_data["base"]["ref"]
        }
    except Exception as e:
        print(f"❌ Failed to get PR details: {e}")
        return None

def get_pr_files(repo_owner, repo_name, pr_number):
    """Get list of changed files in PR"""
    try:
        url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        files_data = response.json()
        python_files = []
        
        for file_data in files_data:
            filename = file_data["filename"]
            if filename.endswith(".py"):
                python_files.append({
                    "filename": filename,
                    "status": file_data["status"],  # added, modified, deleted
                    "additions": file_data["additions"],
                    "deletions": file_data["deletions"],
                    "patch": file_data.get("patch", "")
                })
        
        return python_files
    except Exception as e:
        print(f"❌ Failed to get PR files: {e}")
        return []

def get_file_content(repo_owner, repo_name, file_path, ref="main"):
    """Get file content from GitHub"""
    try:
        url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        params = {"ref": ref}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        file_data = response.json()
        if file_data["type"] == "file":
            import base64
            content = base64.b64decode(file_data["content"]).decode('utf-8')
            return content
        return None
    except Exception as e:
        print(f"❌ Failed to get file content: {e}")
        return None

def parse_repo_url(repo_url):
    """Parse GitHub repo URL to extract owner and name"""
    try:
        # Handle different URL formats
        if repo_url.startswith("https://github.com/"):
            repo_url = repo_url.replace("https://github.com/", "")
        elif repo_url.startswith("git@github.com:"):
            repo_url = repo_url.replace("git@github.com:", "")
        
        repo_url = repo_url.rstrip(".git")
        parts = repo_url.split("/")
        
        if len(parts) >= 2:
            return parts[0], parts[1]
        return None, None
    except Exception as e:
        print(f"❌ Failed to parse repo URL: {e}")
        return None, None