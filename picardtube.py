from picardtube import create_app
from gevent.pywsgi import WSGIServer
if __name__ == "__main__":
    app = create_app(address='0.0.0.0:5000')
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()