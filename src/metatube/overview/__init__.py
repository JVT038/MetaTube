from flask import Blueprint
from config import Config

bp = Blueprint(
    "overview",
    __name__,
    static_folder="../static",
    template_folder="../templates/",
    url_prefix=Config.URL_SUBPATH,
)
from metatube.overview import routes
