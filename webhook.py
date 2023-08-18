from fastapi import FastAPI, Request, HTTPException
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# GitHub configurations
TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("GITHUB_OWNER")
REPO = os.environ.get("GITHUB_REPO")
OPEN_PR_WORKFLOW_ID =   os.environ.get("OPEN_PR_WORKFLOW_ID")
CLOSE_PR_WORKFLOW_ID = os.environ.get("CLOSE_PR_WORKFLOW_ID")

@app.post("/webhook")
async def handle_webhook(request: Request):
    event_type = request.headers.get("X-GitHub-Event")

    if event_type != "pull_request":
        return {"detail": "Not a pull_request event"}

    # Parse the payload
    payload = await request.json()
    action = payload.get("action")

    if action in ["opened", "synchronize", "reopened"]:
        result = await handle_opened_pr(payload)
    elif action == "closed":
        result = await handle_closed_pr(payload)
    else:
        result = {"detail": "Not an interesting PR action"}

    return result

async def handle_opened_pr(payload):
    branch_name = payload.get("pull_request", {}).get("head", {}).get("ref")
    return await trigger_workflow(branch_name, OPEN_PR_WORKFLOW_ID)

async def handle_closed_pr(payload):
    branch_name = payload.get("pull_request", {}).get("head", {}).get("ref")
    return await trigger_workflow(branch_name, CLOSE_PR_WORKFLOW_ID)

async def trigger_workflow(branch_name, workflow_id):
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{OPEN_PR_WORKFLOW_ID }"

    data = {
        "ref": "test-pr"
        # "inputs": {
        #     "name": "Mona the Octocat",
        #     "home": "San Francisco, CA"
        # }
    }
    response = requests.post(url, headers=headers, json=data)


    if response.status_code == 204:
        return {"detail": "Workflow dispatched successfully!"}
    else:
        return {"detail": f"Error {response.status_code}: {response.text}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
