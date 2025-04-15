from flask import Blueprint, render_template

docs_bp = Blueprint("docs", __name__, template_folder="../templates")

@docs_bp.route("/api/redoc")
def redoc_ui():
    print("🔧 Redoc route hit!")
    return render_template("redoc.html", spec_url="/static/combined_docs.yaml")
