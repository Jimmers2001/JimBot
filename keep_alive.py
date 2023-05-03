from flask import Flask
from threading import Thread

# this file creates a webapp on replit and is pinged by uptimerobot every 50 minutes 
# so the replit stays active permanently (shuts down after 60 minutes of no use)
# making the discord bot live permanently
app = Flask('')

@app.route('/')
def home():
    return "Hello, I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()