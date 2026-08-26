from flask import Flask, redirect, url_for
from routes.posts_routes import posts_bp
from routes.auth_routes import auth_bp

app = Flask(__name__)
app.register_blueprint(posts_bp, url_prefix='/posts')
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    return redirect(url_for('posts.get_posts'))

if __name__ == '__main__':
  app.run('0.0.0.0', port=5001, debug=True)