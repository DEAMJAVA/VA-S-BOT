if not os.path.isfile('replit.py'):
    data = '''
from flask import Flask, render_template
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
    return "VA-S-BOT-REPLIT-PLUGIN"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
'''

    with open('replit.py', 'w') as replit:
        replit.write(data)

from replit import keep_alive
keep_alive()
