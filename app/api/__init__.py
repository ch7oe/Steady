"""API blueprint. Internal endpoints for Chart.js & Twilio"""

from flask import Blueprint

bp = Blueprint("api", __name__)

from app.api import routes