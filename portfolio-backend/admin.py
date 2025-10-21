"""
Portfolio Admin CRUD Interface
A simple web-based interface for managing projects and certificates.
Protected by password authentication.
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
CORS(app)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================================
# AUTHENTICATION
# ============================================================================

def login_required(f):
    """Decorator to require login for admin pages."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "authenticated" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    """Admin login page."""
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("login.html", error="Invalid password")
    
    return render_template("login.html")


@app.route("/admin/logout", methods=["POST"])
def logout():
    """Logout from admin panel."""
    session.clear()
    return redirect(url_for("login"))


# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

@app.route("/admin", methods=["GET"])
@login_required
def admin_dashboard():
    """Admin dashboard main page."""
    return render_template("admin_dashboard.html")


# ============================================================================
# PROJECTS CRUD
# ============================================================================

@app.route("/admin/api/projetos", methods=["GET"])
@login_required
def admin_get_projects():
    """Get all projects for admin panel."""
    try:
        response = supabase.table("projetos").select("*").order("created_at", desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/api/projetos", methods=["POST"])
@login_required
def admin_create_project():
    """Create a new project."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["titulo", "descricao", "tecnologias"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Add timestamp
        data["created_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("projetos").insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/api/projetos/<int:project_id>", methods=["PUT"])
@login_required
def admin_update_project(project_id):
    """Update a project."""
    try:
        data = request.get_json()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("projetos").update(data).eq("id", project_id).execute()
        if not response.data:
            return jsonify({"error": "Project not found"}), 404
        return jsonify(response.data[0]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/api/projetos/<int:project_id>", methods=["DELETE"])
@login_required
def admin_delete_project(project_id):
    """Delete a project."""
    try:
        supabase.table("projetos").delete().eq("id", project_id).execute()
        return jsonify({"message": "Project deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CERTIFICATES CRUD
# ============================================================================

@app.route("/admin/api/certificados", methods=["GET"])
@login_required
def admin_get_certificates():
    """Get all certificates for admin panel."""
    try:
        response = supabase.table("certificados").select("*").order("created_at", desc=True).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/api/certificados", methods=["POST"])
@login_required
def admin_create_certificate():
    """Create a new certificate."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["nome", "instituicao", "data_conclusao"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Add timestamp
        data["created_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("certificados").insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/api/certificados/<int:cert_id>", methods=["PUT"])
@login_required
def admin_update_certificate(cert_id):
    """Update a certificate."""
    try:
        data = request.get_json()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("certificados").update(data).eq("id", cert_id).execute()
        if not response.data:
            return jsonify({"error": "Certificate not found"}), 404
        return jsonify(response.data[0]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/api/certificados/<int:cert_id>", methods=["DELETE"])
@login_required
def admin_delete_certificate(cert_id):
    """Delete a certificate."""
    try:
        supabase.table("certificados").delete().eq("id", cert_id).execute()
        return jsonify({"message": "Certificate deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Page not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

