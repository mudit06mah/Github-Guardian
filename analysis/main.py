import os, sys, yaml, json
from pathlib import Path
from github import Github
from detector import(
    detectUnpinnedActions,
    detectCurlBash,
    detectBase64Obfuscation,
    detectInlineScripts
)
from scoring import(
    scoreFindings,
    highestSeverity
)
from reporter import(
    makeReport,
    createCheckRun,
    prComment   
)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("GITHUB_REPOSITORY")
HEAD_SHA = os.environ.get("GITHUB_SHA")
EVENT_PATH = os.environ.get("GITHUB_EVENT_PATH")

def loadChangedWorkflows():
    files = []
    if EVENT_PATH and os.path.exists(EVENT_PATH):
        with open(EVENT_PATH,'r') as f:
            event = json.load(f)

    wf_dir = Path('.github/workflows')
    for p in wf_dir.glob('*.yml'):
        files.append(p)
    for p in wf_dir.glob('*.yaml'):
        files.append(p)
    return files

def analyzeFile(path: Path):
    txt = path.read_text()
    findings = []
    findings += detectUnpinnedActions(txt)
    findings += detectCurlBash(txt)
    findings += detectBase64Obfuscation(txt)

    try:
        parsed = yaml.safe_load(txt) or {}
        findings += detectInlineScripts(parsed)
    except Exception:
        findings.append({
            "type":"parse_error",
            "message":"Failed to parse YAML",
            "match":""})
    return findings 

def main():
    files = loadChangedWorkflows()
    allFindings = [] 
    
    for f in files:
        findings = analyzeFile(f)
        for item in findings:
            item['file'] = str(f)
        allFindings.extend(findings)
    
    allFindings = scoreFindings(allFindings)
    severity = highestSeverity(allFindings)

    body = makeReport(allFindings)

    if severity == 'high':
        conclusion = 'failure'
    elif severity == 'medium':
        conclusion = 'warning'
    else:
        conclusion = 'success'

    if GITHUB_TOKEN and REPO and HEAD_SHA:
        createCheckRun( repoFullName= REPO,
                         name="Guardian - Workflow Scanner",
                         head_sha=HEAD_SHA,
                         conclusion=conclusion,
                         output_title=f"Guardian result: {severity.upper()}",
                         output_summary=body,
                         gh_token=GITHUB_TOKEN)

        # If running in a PR, post comment (best-effort: read event)
        if os.path.exists(EVENT_PATH):
            try:
                with open(EVENT_PATH) as evf:
                    ev = json.load(evf)
                pr_number = ev.get('pull_request',{}).get('number')
                if pr_number:
                    prComment(REPO, pr_number, body, GITHUB_TOKEN)
            except Exception:
                pass

    else:
        print(body)

if __name__ == "__main__":
    main()