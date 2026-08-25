from flask import Flask, redirect, url_for
from routes.meetings import meetings_bp

app = Flask(__name__)
app.register_blueprint(meetings_bp, url_prefix='/meetings')

@app.route('/')
def index():
  return redirect(url_for('meetings.get_meetings'))

if __name__ == '__main__':
  app.run('0.0.0.0', port=5001, debug=True)