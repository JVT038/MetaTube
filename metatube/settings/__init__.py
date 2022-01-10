from flask import Blueprint
from metatube import Config
bp = Blueprint('settings', __name__, static_folder='../static', template_folder='../templates/', url_prefix=Config.URL_SUBPATH)
from metatube.settings import routes