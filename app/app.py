from flask import Flask
app = Flask(__name__)
def home():
    return '<h1>Next-Gen DevOps Pipeline</h1>'
