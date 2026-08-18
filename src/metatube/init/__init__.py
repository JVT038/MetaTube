import os

from metatube import Config
from metatube.init.create import Default


def init(app):
    db_url = Config.SQLALCHEMY_DATABASE_URI
    if db_url.startswith("sqlite:///"):
        relative_url = "sqlite:///" + os.path.join(
            "metatube", db_url.replace("sqlite:///", "")
        )
        default = Default(app, relative_url)
        migrationsPath = os.path.join(Config.BASE_DIR, "migrations")
        if (
            os.path.exists(migrationsPath)
            and os.path.isdir(migrationsPath)
            and (
                os.path.exists(os.path.join(migrationsPath, "env.py"))
                and os.path.exists(os.path.join(migrationsPath, "versions"))
            )
        ):
            default.init_db()
        else:
            default.init_db(False)
