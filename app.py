from flask import Flask, redirect, url_for
from routes.posts import posts_bp

app = Flask(__name__)
app.register_blueprint(posts_bp, url_prefix='/posts')

@app.route('/')
def index():
  return redirect(url_for('posts.get_posts'))

if __name__ == '__main__':
  app.run('0.0.0.0', port=5001, debug=True)