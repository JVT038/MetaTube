from picardtube import create_app, socketio
from gevent.pywsgi import WSGIServer
from gevent.event import Event
if __name__ == "__main__":
    app = create_app()
    try:
        print('Starting the  webserver on http://0.0.0.0:5000...')
        socketio.run(app)
        # server = WSGIServer(('0.0.0.0', 5000), app)
        # server.serve_forever()
        
    except KeyboardInterrupt:
        print('Stop server')