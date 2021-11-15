from metatube import create_app, socketio
from gevent.pywsgi import WSGIServer
from gevent.event import Event
if __name__ == "__main__":
    app = create_app()
    try:
        print('Starting the webserver on http://0.0.0.0:5000...')
        socketio.run(app)        
    except KeyboardInterrupt:
        print('Stop server')