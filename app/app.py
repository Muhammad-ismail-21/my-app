from flask import Flask, jsonify, render_template_string
import datetime
import os

app = Flask(__name__)

START_TIME = datetime.datetime.utcnow()

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #e6edf3; min-height: 100vh; padding: 40px 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 2rem; color: #58a6ff; margin-bottom: 8px; }
        .header p { color: #8b949e; font-size: 0.95rem; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; margin-top: 10px; }
        .badge-dev { background: #1f4068; color: #58a6ff; }
        .badge-prod { background: #1a3a2a; color: #3fb950; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 24px; }
        .card-title { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: #8b949e; margin-bottom: 12px; }
        .card-value { font-size: 1.6rem; font-weight: bold; color: #e6edf3; }
        .card-sub { font-size: 0.8rem; color: #8b949e; margin-top: 6px; }
        .status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #3fb950; margin-right: 8px; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        .stack-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
        .stack-item { background: #21262d; border: 1px solid #30363d; border-radius: 8px; padding: 8px 14px; font-size: 0.85rem; color: #58a6ff; }
        .pipeline-step { display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid #21262d; font-size: 0.88rem; }
        .pipeline-step:last-child { border-bottom: none; }
        .step-icon { width: 24px; height: 24px; border-radius: 50%; background: #1a3a2a; color: #3fb950; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; margin-right: 12px; flex-shrink: 0; }
        .footer { text-align: center; margin-top: 40px; color: #8b949e; font-size: 0.8rem; }
        .refresh-btn { background: #21262d; border: 1px solid #30363d; color: #58a6ff; padding: 8px 20px; border-radius: 8px; cursor: pointer; font-size: 0.85rem; margin-top: 20px; }
        .refresh-btn:hover { background: #30363d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DevOps Dashboard</h1>
            <p>Next-Generation DevOps and Deployment Engine</p>
            <span class="badge {{ badge_class }}">{{ environment }} ENVIRONMENT</span>
        </div>
        <div class="grid">
            <div class="card">
                <div class="card-title">System Status</div>
                <div class="card-value"><span class="status-dot"></span>Operational</div>
                <div class="card-sub">All systems running normally</div>
            </div>
            <div class="card">
                <div class="card-title">Server Uptime</div>
                <div class="card-value">{{ uptime }}</div>
                <div class="card-sub">Since last deployment</div>
            </div>
            <div class="card">
                <div class="card-title">Git Commit SHA</div>
                <div class="card-value" style="font-size:1rem; font-family: monospace;">{{ git_sha }}</div>
                <div class="card-sub">Currently deployed version</div>
            </div>
            <div class="card">
                <div class="card-title">Current Time (UTC)</div>
                <div class="card-value" style="font-size:1.1rem;">{{ current_time }}</div>
                <div class="card-sub">Server time</div>
            </div>
        </div>
        <div class="grid">
            <div class="card">
                <div class="card-title">CI/CD Pipeline Steps</div>
                <div class="pipeline-step"><div class="step-icon">v</div> Checkout code</div>
                <div class="pipeline-step"><div class="step-icon">v</div> Install dependencies</div>
                <div class="pipeline-step"><div class="step-icon">v</div> Lint code (flake8)</div>
                <div class="pipeline-step"><div class="step-icon">v</div> Build Docker image</div>
                <div class="pipeline-step"><div class="step-icon">v</div> Push to AWS ECR</div>
                <div class="pipeline-step"><div class="step-icon">v</div> Deploy to EC2</div>
            </div>
            <div class="card">
                <div class="card-title">Tech Stack</div>
                <div class="stack-grid">
                    <span class="stack-item">GitHub Actions</span>
                    <span class="stack-item">Docker</span>
                    <span class="stack-item">AWS ECR</span>
                    <span class="stack-item">AWS EC2</span>
                    <span class="stack-item">Terraform</span>
                    <span class="stack-item">CloudWatch</span>
                    <span class="stack-item">AWS SNS</span>
                    <span class="stack-item">Python Flask</span>
                </div>
            </div>
        </div>
        <div style="text-align:center;">
            <button class="refresh-btn" onclick="location.reload()">Refresh Dashboard</button>
        </div>
        <div class="footer">
            <p>Deployed via GitHub Actions | Hosted on AWS EC2 t3.micro | Infrastructure by Terraform</p>
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def dashboard():
    uptime_seconds = (datetime.datetime.utcnow() - START_TIME).seconds
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    environment = os.environ.get('ENVIRONMENT', 'PROD')
    badge_class = 'badge-dev' if environment == 'DEV' else 'badge-prod'
    git_sha = os.environ.get('GIT_SHA', 'local')[:7]
    return render_template_string(
        DASHBOARD_HTML,
        uptime=f'{hours}h {minutes}m {seconds}s',
        environment=environment,
        badge_class=badge_class,
        git_sha=git_sha,
        current_time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    )


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'environment': os.environ.get('ENVIRONMENT', 'PROD'),
        'uptime_seconds': (datetime.datetime.utcnow() - START_TIME).seconds,
        'git_sha': os.environ.get('GIT_SHA', 'local')[:7]
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
