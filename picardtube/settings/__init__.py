from flask import Blueprint
bp = Blueprint('setings', __name__, static_folder='../static', template_folder='../templates/')

from . import routes