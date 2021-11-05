from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_fontawesome import FontAwesome
from flask_jsglue import JSGlue
from flask_migrate import Migrate
from config import Config
app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
fontawesome = FontAwesome(app)
csrf = CSRFProtect(app)
jsglue = JSGlue(app)


from picardtube import routes
