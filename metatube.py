from metatube import create_app, socketio
import os, sys
if __name__ == "__main__":
    app = create_app()
    port = os.environ.get('port') or 5000
    host = os.environ.get('host') or '127.0.0.1'
    debug = os.environ.get('debug') or False
    log_output = os.environ.get('log') or False
    os.environ["FLASK_APP"] = 'metatube.py'
    os.environ["TEMPLATES_AUTO_RELOAD"] = str(True)
    os.environ["SECRET_KEY"] = str(os.urandom(24))
    os.environ["DATABASE_URL"] = "sqlite:///app.db" if os.environ.get('DATABASE_URL') is None else os.environ.get('DATABASE_URL')
    try:
        print(u'Starting the webserver on http://%s:%s...'%(host, port))
        socketio.run(app, str(host), int(port), debug=bool(debug), log_output=bool(log_output))
    except KeyboardInterrupt:
        print('Stopped server because of KeyboardInterrupt')