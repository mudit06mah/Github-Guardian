from github import Github

def makeReport(findings):
    if not findings:
        return "No issues found."
    lines = ["### Github Guardian Findings:\n"]
    for f in findings:
        lines.append(f"- **{f['severity'].upper()}**: {f['message']}")
        if 'snippet' in f:
            lines.append(f"  ```\n  {f['snippet'][:500]}\n   ```")
    return "\n".join(lines)

def prComment(repoFullName, prNumber, body, ghToken):
    g = Github(ghToken)
    repo = g.get_repo(repoFullName)
    pr = repo.get_pull(prNumber)
    pr.create_issue_comment(body)

def createCheckRun(repoFullName, name, headSHA, conclusion, outputTitle, outputSummary, ghToken):
    g = Github(ghToken)
    repo = g.get_repo(repoFullName)
    repo.create_check_run(name=name,
                          head_sha=headSHA,
                          status="completed",
                          conclusion=conclusion,
                          output={"title":outputTitle, "summary": outputSummary})
