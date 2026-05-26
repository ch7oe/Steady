"""Meals blueprint."""

from flask import Blueprint

bp = Blueprint("meals", __name__)

from app.meals import routes