from flask import Flask, redirect, url_for
from routes.meetings import meetings_bp
from routes.auth_routes import auth_bp

app = Flask(__name__)
app.register_blueprint(meetings_bp, url_prefix='/meetings')
app.register_blueprint(auth_bp)

if __name__ == '__main__':
  app.run('0.0.0.0', port=5001, debug=True)