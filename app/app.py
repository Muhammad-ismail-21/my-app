from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Next-Gen DevOps Pipeline</h1><p>Deployed via GitHub Actions + AWS EC2</p>'

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
