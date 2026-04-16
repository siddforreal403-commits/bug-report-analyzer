from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
    <title>Bug Report Analyzer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; max-width: 900px; }
        textarea { width: 100%; height: 220px; }
        button { padding: 10px 16px; margin-top: 10px; }
        .box { margin-top: 20px; padding: 16px; border: 1px solid #ccc; border-radius: 10px; }
        pre { white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>Bug Report Analyzer</h1>
    <p>Paste a bug report below. The tool extracts a rough category, likely component, severity guess, and summary.</p>
    <form method="post">
        <textarea name="report" placeholder="Paste bug report here...">{{ report }}</textarea><br>
        <button type="submit">Analyze</button>
    </form>

    {% if result %}
    <div class="box">
        <h2>Analysis</h2>
        <pre>{{ result }}</pre>
    </div>
    {% endif %}
</body>
</html>
"""

CATEGORY_RULES = {
    "authentication": [r"login", r"password", r"otp", r"authentication", r"session"],
    "authorization": [r"idor", r"unauthorized", r"permission", r"access control", r"privilege"],
    "xss": [r"xss", r"script injection", r"javascript execution", r"stored xss", r"reflected xss"],
    "sqli": [r"sql injection", r"sqli", r"database error", r"union select"],
    "csrf": [r"csrf", r"cross-site request forgery"],
    "ssrf": [r"ssrf", r"server-side request forgery", r"internal request"],
    "file upload": [r"upload", r"file", r"extension bypass", r"content-type bypass"],
    "rce": [r"rce", r"remote code execution", r"command injection", r"code execution"],
    "information disclosure": [r"disclosure", r"leak", r"sensitive data", r"metadata", r"token exposed"],
    "business logic": [r"business logic", r"workflow bypass", r"race condition", r"abuse"]
}

COMPONENT_RULES = {
    "auth flow": [r"login", r"signup", r"password", r"otp", r"token", r"session"],
    "api": [r"/api/", r"graphql", r"endpoint", r"json response", r"rest"],
    "file handling": [r"upload", r"attachment", r"file", r"image", r"document"],
    "admin panel": [r"admin", r"dashboard", r"management console"],
    "sharing / permissions": [r"share", r"permission", r"invite", r"access", r"acl"],
    "payment flow": [r"payment", r"checkout", r"wallet", r"withdrawal"],
    "profile / account": [r"profile", r"account", r"user settings", r"email change"]
}

def score_rules(text, rules):
    scores = {}
    for label, patterns in rules.items():
        score = 0
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                score += 1
        scores[label] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"

def guess_severity(text):
    text_l = text.lower()
    critical_terms = ["rce", "remote code execution", "auth bypass", "account takeover", "arbitrary file read"]
    high_terms = ["idor", "unauthorized access", "xss", "sqli", "ssrf", "privilege escalation"]
    medium_terms = ["csrf", "metadata leak", "rate limit bypass", "workflow bypass"]
    low_terms = ["ui issue", "misleading error", "cosmetic", "minor leak"]

    if any(t in text_l for t in critical_terms):
        return "critical"
    if any(t in text_l for t in high_terms):
        return "high"
    if any(t in text_l for t in medium_terms):
        return "medium"
    if any(t in text_l for t in low_terms):
        return "low"
    return "needs manual review"

def summarize(text):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= 220:
        return text
    return text[:217] + "..."

def analyze_report(report):
    category = score_rules(report, CATEGORY_RULES)
    component = score_rules(report, COMPONENT_RULES)
    severity = guess_severity(report)
    summary = summarize(report)

    return {
        "category": category,
        "likely_component": component,
        "severity_guess": severity,
        "summary": summary
    }

@app.route("/", methods=["GET", "POST"])
def home():
    report = ""
    result = None
    if request.method == "POST":
        report = request.form.get("report", "")
        result = analyze_report(report)
    return render_template_string(HTML, report=report, result=result)

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(force=True)
    report = data.get("report", "")
    return jsonify(analyze_report(report))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
