from flask import Blueprint
bp = Blueprint('overview', __name__, static_folder='../static', template_folder='../templates/')
from picardtube.overview import routes