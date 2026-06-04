import os
from flask import Flask, jsonify, send_from_directory

from flask_cors import CORS
from backend.config import Config
from backend.extensions import db, jwt, mail, limiter

# Chemin vers le frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
# Chemin vers le dossier static
STATIC_SECHAGE_DIR = os.path.join(os.path.dirname(__file__), "static", "sechage")
# Chemin vers le dossier templates (dans backend/)
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "backend", "templates")


def create_app():
    app = Flask(__name__, template_folder=TEMPLATES_DIR)
    app.config.from_object(Config)

    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    CORS(app)

    # Initialize Swagger documentation
    from backend.swagger_config import init_swagger
    init_swagger(app)

    # Initialize security middleware
    from backend.middlewares.security_middleware import init_security_middleware
    init_security_middleware(app)
    
    # Initialize rate limiter
    from backend.middlewares.rate_limiter import init_rate_limiter
    init_rate_limiter(app)

    # Initialize performance profiler
    from backend.utils.performance_profiler import init_performance_profiler
    init_performance_profiler(app)

    # Register existing blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.user import user_bp
    from backend.routes.admin import admin_bp
    from backend.routes.calculations import calculations_bp
    from backend.routes.mccabe_simulator import mccabe_simulator_bp
    from backend.routes.history import history_bp
    from backend.routes.assistant import assistant_bp
    from backend.routes.cross_current_simulator import cross_current_simulator_bp
    from backend.routes.contact import contact_bp
    from backend.routes.sechage import sechage_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(calculations_bp, url_prefix="/api/calculations")
    app.register_blueprint(mccabe_simulator_bp, url_prefix="/api/mccabe")
    app.register_blueprint(history_bp, url_prefix="/api")
    app.register_blueprint(assistant_bp, url_prefix="/api/assistant")
    app.register_blueprint(cross_current_simulator_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(sechage_bp)

    # Register new REST API routes
    from backend.routes.api import register_api_routes
    register_api_routes(app)

    # Create tables
    with app.app_context():
        db.create_all()

    # Serve frontend pages
    @app.route("/")
    def root_index():
        return send_from_directory(os.path.join(FRONTEND_DIR, "public"), "index.html")

    @app.route("/public/")
    def public_index():
        return send_from_directory(os.path.join(FRONTEND_DIR, "public"), "index.html")

    @app.route("/anonymous/")
    def anonymous_index():
        return send_from_directory(os.path.join(FRONTEND_DIR, "public"), "index.html")

    @app.route("/public/<path:filename>")
    def public_pages(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, "public"), filename)

    @app.route("/mccabe-thiele/")
    def mccabe_thiele():
        return send_from_directory(os.path.join(FRONTEND_DIR, "public"), "mccabe_thiele.html")

    @app.route("/user/")
    def user_index():
        return send_from_directory(os.path.join(FRONTEND_DIR, "user"), "login.html")

    @app.route("/user/<path:filename>")
    def user_pages(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, "user"), filename)

    @app.route("/admin/")
    def admin_index():
        return send_from_directory(os.path.join(FRONTEND_DIR, "admin"), "dashboard.html")

    @app.route("/admin/<path:filename>")
    def admin_pages(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, "admin"), filename)

    @app.route("/css/<path:filename>")
    def css_files(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, "css"), filename)

    @app.route("/js/<path:filename>")
    def js_files(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, "js"), filename)

    @app.route("/static/sechage/<path:filename>")
    def sechage_static_files(filename):
        response = send_from_directory(STATIC_SECHAGE_DIR, filename)
        # Empêcher la mise en cache pour les images PNG
        if filename.endswith('.png'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    # Legacy flat URLs — redirect to new structure
    ADMIN_MAP   = {
        "admin-dashboard.html": "dashboard.html",
        "admin-users.html":     "users.html",
        "admin-audit.html":     "audit.html",
        "admin-archive.html":   "archive.html",
        "admin-ip.html":        "ip.html",
    }

    from flask import redirect

    @app.route("/<path:filename>")
    def legacy_redirect(filename):
        if filename in ADMIN_MAP:
            return redirect(f"/admin/{ADMIN_MAP[filename]}")
        # user pages
        user_file = os.path.join(FRONTEND_DIR, "user", filename)
        if os.path.isfile(user_file):
            return send_from_directory(os.path.join(FRONTEND_DIR, "user"), filename)
        return jsonify({"success": False, "message": "Ressource introuvable"}), 404

    # Global error handlers
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"success": False, "message": "Authentification requise"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "message": "Accès refusé"}), 403

    @app.errorhandler(404)
    def not_found(e):
        # Return HTML 404 page for browser requests, JSON for API
        from flask import request as req
        if req.path.startswith("/api/"):
            return jsonify({"success": False, "message": "Ressource introuvable"}), 404
        return send_from_directory(os.path.join(FRONTEND_DIR, "user"), "404.html"), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"success": False, "message": "Trop de tentatives. Veuillez réessayer dans quelques minutes."}), 429

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "message": "Erreur interne du serveur"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
