import re
from typing import List, Dict, Any

UNPINNED_REGEX = re.compile(r'uses:\s*([\w./-]+)(?:@([\w.-]+))?', re.IGNORECASE)    #Catches uses: owner/repo@ref

CURL_BASH_REGEX = re.compile(r'\b(curl|wget)\b.*\|\s*(bash|sh)\b',re.IGNORECASE)    #Catches curl or bash

BASE64_REGEX = re.compile(r'base64\s+-d|[A-Za-z0-9+/]{40,}={0,2}')    #Catches base64

LONG_INLINE_THRESHOLD = 200

def detectUnpinnedActions(yamlText: str) -> List[Dict[str,Any]]:
    findings = []
    for m in UNPINNED_REGEX.finditer(yamlText):
        uses = m.group(1)
        ref = m.group(2)
        if not ref:
            #No pinned ref:
            findings.append({
                "type": "unpinned_actions",
                "message": f"Action `{uses}` used without a pinned ref (no @sha or tag).",
                "match": m.group(0),
            })
        else:
            #Tags:
            if not re.match(r'^[0-9a-f]{7,40}$',ref):
                findings.append({
                    "type":"unpinned_action",
                    "message": f"Action `{uses}@ref` is not  pinned to a commit SHA,",
                    "match": m.group(0),
                })
    return findings

def detectCurlBash(yamlText: str) -> List[Dict[str,Any]]:
    findings = []
    for m in CURL_BASH_REGEX.finditer(yamlText):
        findings.append({
            "type": "curl_pipe_bash",
            "message": "Use of curl/wget piped to shell detected.",
            "match": m.group(0),
        })
    return findings

def detectBase64Obfuscation(yamlText: str) -> List[Dict[str,Any]]:
    findings = []
    for m in BASE64_REGEX.finditer(yamlText):
        if len(m.group(0)) > 60:
            findings.append({
                "type": "base64_obfuscation",
                "message": "Possible base64 Obsucation detected",
                "match": m.group(0)[:200],
            })
    return findings

def detectInlineScripts(yamlParsed: str) -> List[Dict[str,Any]]:
    findings = []
    jobs = yamlParsed.get('jobs',{})
    for jobName, job in jobs.items():
        steps = job.get('steps',[])
        for step in steps:
            run = step.get('run')
            if run and isinstance(run,str) and len(run) > LONG_INLINE_THRESHOLD:
                findings.append({
                    "type": "long_inline_scripts",
                    "message": f"Long inline script in job `{jobName}` step `{step.get('name','(unnamed)')}` ({len(run)} chars).",
                    "length": len(run),
                    "snippet": run[:200]
                })
    return findings

