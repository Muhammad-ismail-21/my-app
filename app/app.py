from flask import Flask, jsonify, render_template_string
import datetime
import os
import json
import boto3

app = Flask(__name__)

START_TIME = datetime.datetime.utcnow()
S3_BUCKET = os.environ.get('S3_BUCKET', '')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #0d1117;
            color: #e6edf3;
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 2rem; color: #58a6ff; margin-bottom: 8px; }
        .header p { color: #8b949e; font-size: 0.95rem; }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-top: 10px;
        }
        .badge-dev { background: #1f4068; color: #58a6ff; }
        .badge-prod { background: #1a3a2a; color: #3fb950; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 24px;
        }
        .card-title {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #8b949e;
            margin-bottom: 12px;
        }
        .card-value { font-size: 1.6rem; font-weight: bold; color: #e6edf3; }
        .card-sub { font-size: 0.8rem; color: #8b949e; margin-top: 6px; }
        .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #3fb950;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }
        .stack-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
        .stack-item {
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 0.85rem;
            color: #58a6ff;
        }
        .pipeline-step {
            display: flex;
            align-items: center;
            padding: 12px 10px;
            border-bottom: 1px solid #21262d;
            border-radius: 8px;
            font-size: 0.88rem;
            opacity: 0;
            transform: translateX(-10px);
            transition: opacity 0.5s ease, transform 0.5s ease, background 0.3s ease;
            margin-bottom: 2px;
        }
        .pipeline-step.active {
            background: #1f3a1f;
            border: 1px solid #238636;
            opacity: 1;
            transform: translateX(0);
        }
        .pipeline-step.active .step-icon {
            background: #238636;
            box-shadow: 0 0 10px #3fb950;
            animation: glow 1s ease-in-out;
        }
        .pipeline-step.done {
            opacity: 1;
            transform: translateX(0);
            background: #161b22;
        }
        @keyframes glow {
            0% { box-shadow: 0 0 5px #3fb950; }
            50% { box-shadow: 0 0 20px #3fb950, 0 0 40px #3fb950; }
            100% { box-shadow: 0 0 5px #3fb950; }
        }
        .step-label { flex: 1; }
        .step-status {
            font-size: 0.75rem;
            color: #3fb950;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .pipeline-step.done .step-status,
        .pipeline-step.active .step-status { opacity: 1; }
        .step-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #1a3a2a;
            color: #3fb950;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            margin-right: 12px;
            flex-shrink: 0;
        }
        .history-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            margin-top: 10px;
        }
        .history-table th {
            text-align: left;
            color: #8b949e;
            padding: 6px 8px;
            border-bottom: 1px solid #30363d;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        .history-table td {
            padding: 8px;
            border-bottom: 1px solid #21262d;
            color: #e6edf3;
        }
        .history-table tr:last-child td { border-bottom: none; }
        .env-prod { color: #3fb950; font-weight: bold; }
        .env-dev { color: #58a6ff; font-weight: bold; }
        .footer { text-align: center; margin-top: 40px; color: #8b949e; font-size: 0.8rem; }
        .refresh-info {
            text-align: center;
            color: #8b949e;
            font-size: 0.8rem;
            margin-top: 16px;
        }
        .countdown { color: #58a6ff; font-weight: bold; }
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
                <div class="card-value" id="uptime">{{ uptime }}</div>
                <div class="card-sub">Since last deployment</div>
            </div>
            <div class="card">
                <div class="card-title">Git Commit SHA</div>
                <div class="card-value" style="font-size:1rem; font-family:monospace;">
                    {{ git_sha }}
                </div>
                <div class="card-sub">Currently deployed version</div>
            </div>
            <div class="card">
                <div class="card-title">Current Time (UTC)</div>
                <div class="card-value" style="font-size:1.1rem;" id="clock">
                    {{ current_time }}
                </div>
                <div class="card-sub">Server time</div>
            </div>
        </div>
        <div class="grid">
            <div class="card">
                <div class="card-title">CI/CD Pipeline Steps</div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">Code pushed to GitHub</span>
                    <span class="step-status">done</span>
                </div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">GitHub Actions triggered</span>
                    <span class="step-status">done</span>
                </div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">Install dependencies</span>
                    <span class="step-status">done</span>
                </div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">Configure AWS credentials</span>
                    <span class="step-status">done</span>
                </div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">Lint code — flake8 quality gate</span>
                    <span class="step-status">done</span>
                </div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">Login to AWS ECR</span>
                    <span class="step-status">done</span>
                </div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">Build Docker image (tagged by Git SHA)</span>
                    <span class="step-status">done</span>
                </div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">Push image to AWS ECR</span>
                    <span class="step-status">done</span>
                </div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">SSH into EC2 and deploy container</span>
                    <span class="step-status">done</span>
                </div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">Write deployment log to AWS S3</span>
                    <span class="step-status">done</span>
                </div>
                <div class="pipeline-step">
                    <div class="step-icon">&#10003;</div>
                    <span class="step-label">Email alert on failure via SNS</span>
                    <span class="step-status">done</span>
                </div>
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
                    <span class="stack-item">AWS S3</span>
                    <span class="stack-item">Python Flask</span>
                </div>
            </div>
        </div>
        <div class="card" style="margin-bottom:30px;">
            <div class="card-title">Deployment History (from AWS S3)</div>
            <table class="history-table">
                <thead>
                    <tr>
                        <th>SHA</th>
                        <th>Environment</th>
                        <th>Deployed At (UTC)</th>
                        <th>By</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for log in deployment_logs %}
                    <tr>
                        <td style="font-family:monospace;">{{ log.sha }}</td>
                        <td class="{{ 'env-prod' if log.environment == 'PROD' else 'env-dev' }}">
                            {{ log.environment }}
                        </td>
                        <td>{{ log.timestamp }}</td>
                        <td>{{ log.actor }}</td>
                        <td style="color:#3fb950;">{{ log.status }}</td>
                    </tr>
                    {% endfor %}
                    {% if not deployment_logs %}
                    <tr>
                        <td colspan="5" style="color:#8b949e; text-align:center; padding:16px;">
                            No deployments yet
                        </td>
                    </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
        <div class="refresh-info">
            Auto-refreshing in <span class="countdown" id="countdown">30</span>s
        </div>
        <div class="footer">
            <p>
                Deployed via GitHub Actions |
                Hosted on AWS EC2 t3.micro |
                Infrastructure by Terraform
            </p>
        </div>
    </div>
    <script>
        const steps = document.querySelectorAll('.pipeline-step');
        let currentStep = 0;

        function runNextStep() {
            if (currentStep > 0) {
                steps[currentStep - 1].classList.remove('active');
                steps[currentStep - 1].classList.add('done');
            }
            if (currentStep < steps.length) {
                steps[currentStep].classList.add('active');
                currentStep++;
                setTimeout(runNextStep, 800);
            }
        }

        setTimeout(runNextStep, 500);

        function updateClock() {
            const now = new Date();
            const pad = n => String(n).padStart(2, '0');
            document.getElementById('clock').textContent =
                now.getUTCFullYear() + '-' +
                pad(now.getUTCMonth() + 1) + '-' +
                pad(now.getUTCDate()) + ' ' +
                pad(now.getUTCHours()) + ':' +
                pad(now.getUTCMinutes()) + ':' +
                pad(now.getUTCSeconds());
        }
        setInterval(updateClock, 1000);

        let count = 30;
        setInterval(() => {
            count--;
            document.getElementById('countdown').textContent = count;
            if (count <= 0) location.reload();
        }, 1000);
    </script>
</body>
</html>
"""


def get_deployment_logs():
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        all_files = []
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=S3_BUCKET, Prefix='logs/'):
            all_files.extend(page.get('Contents', []))
        if not all_files:
            return []
        files = sorted(
            all_files,
            key=lambda x: x['LastModified'],
            reverse=True
        )[:5]
        logs = []
        for f in files:
            obj = s3.get_object(Bucket=S3_BUCKET, Key=f['Key'])
            data = json.loads(obj['Body'].read().decode('utf-8'))
            logs.append(data)
        return logs
    except Exception:
        return []


@app.route('/')
def dashboard():
    uptime_seconds = (datetime.datetime.utcnow() - START_TIME).seconds
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    environment = os.environ.get('ENVIRONMENT', 'PROD')
    badge_class = 'badge-dev' if environment == 'DEV' else 'badge-prod'
    git_sha = os.environ.get('GIT_SHA', 'local')[:7]
    deployment_logs = get_deployment_logs()
    return render_template_string(
        DASHBOARD_HTML,
        uptime=f'{hours}h {minutes}m {seconds}s',
        environment=environment,
        badge_class=badge_class,
        git_sha=git_sha,
        current_time=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        deployment_logs=deployment_logs
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
