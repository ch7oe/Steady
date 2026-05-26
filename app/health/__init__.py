"""Health blueprint."""

from flask import Blueprint

bp = Blueprint("health", __name__)

from app.health import routes