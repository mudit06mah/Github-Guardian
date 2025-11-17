SEVERITY_MAP = {
    "unpinned_action": "high", 
    "curl_pipe_bash": "high",           
    "base64_obfuscation": "medium",      
    "long_inline_scripts": "medium",     
    "secret_exposure": "critical",       
    "dangerous_permissions": "high"      
}


def scoreFindings(findings):
    out = []
    for f in findings:
        sev = SEVERITY_MAP.get(f['type'],'low')
        f['severity'] = sev
        out.append(f)
    return out

def highestSeverity(findings):
    order = {"low": 0, "medium":1, "high":2, "critical":3}
    maxv = "low"
    for f in findings:
        if order[f['severity']]> order[maxv]:
            maxv = f['severity']
    return maxv
