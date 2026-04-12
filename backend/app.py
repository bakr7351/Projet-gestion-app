from flask import Flask
from routes.auth import auth_bp

app = Flask(__name__)

# Register routes
app.register_blueprint(auth_bp, url_prefix="/api")

@app.route("/")
def home():
    return {"message": "Backend running"}

if __name__ == "__main__":
    app.run(debug=True)