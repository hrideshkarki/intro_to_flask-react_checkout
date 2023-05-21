from flask import Blueprint

ig = Blueprint('ig', __name__)

from . import routes