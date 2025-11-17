from logging import config
import os, yaml, json
import fnmatch
from pathlib import Path
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

def loadConfig():
    default = {
        "severity_threshold": os.getenv("GUARDIAN_SEVERITY_THRESHOLD", "medium"),
        "fail_on_severity": os.getenv("GUARDIAN_FAIL_ON_SEVERITY", "high"),
        "ignore": [],
    }

    cfg_path = os.getenv("GUARDIAN_CONFIG_PATH", ".github/guardian.yml")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path) as f:
                yaml_cfg = yaml.safe_load(f) or {}
            default.update(yaml_cfg)
        except Exception:
            pass

    return default


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

    config = loadConfig()
    ignore_patterns = config.get("ignore", [])

    def isIgnored(finding):
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(finding.get("file", ""), pattern):
                return True
        return False
        
    #drop ignored findings:
    allFindings = [f for f in allFindings if not isIgnored(f)]    
    
    #score findings:
    allFindings = scoreFindings(allFindings)
    severity = highestSeverity(allFindings)

    severity_threshold = config.get("severity_threshold", "medium")
    order = {"low":0, "medium":1, "high":2}

    # Drop findings below threshold
    allFindings = [
        f for f in allFindings
        if order[f["severity"]] >= order[severity_threshold]
    ]

    fail_on = config.get("fail_on_severity", "high")

    # Declare failure according to config severity
    if order[severity] >= order.get(fail_on, 99):
        conclusion = "failure"
    else:
        conclusion = "success"

    body = makeReport(allFindings)

    if GITHUB_TOKEN and REPO and HEAD_SHA:
        createCheckRun( repoFullName= REPO,
                         name="Guardian - Workflow Scanner",
                         headSHA=HEAD_SHA,
                         conclusion=conclusion,
                         outputTitle=f"Guardian result: {severity.upper()}",
                         outputSummary=body,
                         ghToken=GITHUB_TOKEN)

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