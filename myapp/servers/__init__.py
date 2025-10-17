from flask import Blueprint

servers = Blueprint('servers', __name__)

from . import routes