from metatube import create_app, socketio
from gevent.pywsgi import WSGIServer
from gevent.event import Event
import os
if __name__ == "__main__":
    app = create_app()
    port = os.environ.get('port') or 5000
    host = os.environ.get('host') or '127.0.0.1'
    debug = os.environ.get('debug') or False
    log_output = os.environ.get('log') or False
    try:
        print(u'Starting the webserver on http://%s:%s...'%(host, port))
        socketio.run(app, str(host), int(port), debug=bool(debug), log_output=bool(log_output))
    except KeyboardInterrupt:
        print('Stopped server because of KeyboardInterrupt')