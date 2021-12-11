#!/usr/bin/env python3
# coding: utf-8

from metatube import create_app, socketio, logger
from gevent import get_hub
from gevent.pywsgi import WSGIServer
import os
if __name__ == "__main__":
    app = create_app()
    port = os.environ.get('PORT') or 5000
    host = os.environ.get('HOST') or '127.0.0.1'
    debug = os.environ.get('DEBUG') or False
    log_output = os.environ.get('LOG') or False
    get_hub().NOT_ERROR += (KeyboardInterrupt,)
    try:
        logger.info(u'Starting the webserver on http://%s:%s...'%(host, port))
        socketio.run(app, str(host), int(port), log_output=bool(log_output))
    except KeyboardInterrupt:
        logger.info('Stopped server because of KeyboardInterrupt')