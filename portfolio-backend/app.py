"""
Portfolio Backend API
A Flask-based REST API for managing portfolio projects, certificates, and visit tracking.
"""

import os
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)
# Minimal secret key for session support (override in production via SECRET_KEY env)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # Change in production

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================================
# AUTHENTICATION DECORATOR
# ============================================================================

def require_auth(f):
    """Decorator to protect admin endpoints with password authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401
        
        try:
            # Expected format: "Bearer <password>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0] != "Bearer":
                return jsonify({"error": "Invalid Authorization header"}), 401
            
            password = parts[1]
            if password != ADMIN_PASSWORD:
                return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify({"status": "ok", "message": "Portfolio API is running"}), 200


# ============================================================================
# PROJECTS ENDPOINTS
# ============================================================================

@app.route("/api/projetos", methods=["GET"])
def get_projects():
    """Retrieve all projects from the database."""
    try:
        response = supabase.table("projetos").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projetos", methods=["POST"])
@require_auth
def create_project():
    """Create a new project (admin only)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["titulo", "descricao", "tecnologias"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Add created_at timestamp
        data["created_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("projetos").insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projetos/<int:project_id>", methods=["GET"])
def get_project(project_id):
    """Retrieve a specific project by ID."""
    try:
        response = supabase.table("projetos").select("*").eq("id", project_id).execute()
        if not response.data:
            return jsonify({"error": "Project not found"}), 404
        return jsonify(response.data[0]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projetos/<int:project_id>", methods=["PUT"])
@require_auth
def update_project(project_id):
    """Update a specific project (admin only)."""
    try:
        data = request.get_json()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("projetos").update(data).eq("id", project_id).execute()
        if not response.data:
            return jsonify({"error": "Project not found"}), 404
        return jsonify(response.data[0]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projetos/<int:project_id>", methods=["DELETE"])
@require_auth
def delete_project(project_id):
    """Delete a specific project (admin only)."""
    try:
        response = supabase.table("projetos").delete().eq("id", project_id).execute()
        return jsonify({"message": "Project deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CERTIFICATES ENDPOINTS
# ============================================================================

@app.route("/api/certificados", methods=["GET"])
def get_certificates():
    """Retrieve all certificates, optionally filtered by origin."""
    try:
        origem = request.args.get("origem")
        
        if origem:
            response = supabase.table("certificados").select("*").eq("origem", origem).execute()
        else:
            response = supabase.table("certificados").select("*").execute()
        
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/certificados", methods=["POST"])
@require_auth
def create_certificate():
    """Create a new certificate (admin only)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["nome", "instituicao", "data_conclusao"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Add created_at timestamp
        data["created_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("certificados").insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/certificados/<int:cert_id>", methods=["GET"])
def get_certificate(cert_id):
    """Retrieve a specific certificate by ID."""
    try:
        response = supabase.table("certificados").select("*").eq("id", cert_id).execute()
        if not response.data:
            return jsonify({"error": "Certificate not found"}), 404
        return jsonify(response.data[0]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/certificados/<int:cert_id>", methods=["PUT"])
@require_auth
def update_certificate(cert_id):
    """Update a specific certificate (admin only)."""
    try:
        data = request.get_json()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("certificados").update(data).eq("id", cert_id).execute()
        if not response.data:
            return jsonify({"error": "Certificate not found"}), 404
        return jsonify(response.data[0]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/certificados/<int:cert_id>", methods=["DELETE"])
@require_auth
def delete_certificate(cert_id):
    """Delete a specific certificate (admin only)."""
    try:
        response = supabase.table("certificados").delete().eq("id", cert_id).execute()
        return jsonify({"message": "Certificate deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# VISIT TRACKING ENDPOINTS
# ============================================================================

@app.route("/api/visitas", methods=["GET"])
def get_visits():
    """Retrieve the total number of visits."""
    try:
        response = supabase.table("visitas").select("total").execute()
        if response.data:
            return jsonify({"total": response.data[0]["total"]}), 200
        else:
            return jsonify({"total": 0}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/visitas", methods=["POST"])
def increment_visits():
    """Increment the visit counter."""
    try:
        # Get current visit count
        response = supabase.table("visitas").select("*").execute()
        
        if response.data:
            # Update existing record
            current_total = response.data[0]["total"]
            new_total = current_total + 1
            update_response = supabase.table("visitas").update({"total": new_total}).eq("id", response.data[0]["id"]).execute()
            return jsonify({"total": new_total}), 200
        else:
            # Create new record if it doesn't exist
            insert_response = supabase.table("visitas").insert({"total": 1}).execute()
            return jsonify({"total": 1}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

@app.route("/", methods=["GET", "POST"])
def index():
    """Root endpoint: show login page for browsers, handle login POST, or provide a small API description.

    POST: expects form field `password`. If matches ADMIN_PASSWORD, render admin dashboard.
    GET: render `login.html` if present, otherwise return JSON description.
    """
    # Handle form login submission
    if request.method == "POST":
        password = request.form.get("password")
        if password and password == ADMIN_PASSWORD:
            # Mark session as logged in and redirect to admin dashboard
            session["logged_in"] = True
            # Redirecting gives cleaner behavior (avoids form resubmit on refresh)
            return redirect(url_for("admin_dashboard"))
        else:
            # Invalid password: show login again with error message (if template available)
            login_path = os.path.join(app.root_path, "templates", "login.html")
            if os.path.exists(login_path):
                try:
                    return render_template("login.html", error="Senha inválida"), 200
                except Exception:
                    pass
            return jsonify({"error": "Senha inválida"}), 401

    # GET: render login page when available, otherwise return small JSON API description.
    template_path = os.path.join(app.root_path, "templates", "login.html")
    if os.path.exists(template_path):
        try:
            return render_template("login.html"), 200
        except Exception:
            # If rendering fails for any reason, fall back to the JSON response below.
            pass

    return jsonify({
        "message": "Portfolio API — use /health or /api/projetos",
        "endpoints": ["/health", "/api/projetos", "/api/certificados", "/api/visitas"]
    }), 200


@app.route("/admin", methods=["GET"])
def admin_dashboard():
    """Serve the admin dashboard only when user is logged in (session flag)."""
    if session.get("logged_in"):
        dashboard_path = os.path.join(app.root_path, "templates", "admin_dashboard.html")
        if os.path.exists(dashboard_path):
            try:
                return render_template("admin_dashboard.html"), 200
            except Exception:
                pass
        # If template missing, return a minimal JSON for admin
        return jsonify({"message": "Admin dashboard"}), 200
    # Not logged in -> redirect to login
    return redirect(url_for("index"))


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    """Clear session and redirect to login. Accepts POST from dashboard logout form."""
    session.pop("logged_in", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Respect environment variables for production vs development
    flask_env = os.getenv("FLASK_ENV", "development")
    flask_debug_raw = os.getenv("FLASK_DEBUG", "False")
    flask_debug = str(flask_debug_raw).lower() in ("1", "true", "yes")

    # Warn if running with default admin password
    if ADMIN_PASSWORD == "admin123":
        print("WARNING: ADMIN_PASSWORD is set to the default 'admin123'. Change it in production!", flush=True)

    if flask_env == "production":
        print("FLASK_ENV=production detected. Recommended to run with a WSGI server (e.g. gunicorn).", flush=True)

    app.run(debug=flask_debug, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

