#!/usr/bin/env python3
# GMG Copyright 2022 - Alexandre Díaz
import os
from gmg import create_app
from gmgl.configs import GMGConfig
from logging.handlers import RotatingFileHandler
import logging

logging.basicConfig()

# Preventing user disappointment
try:
    if os.getlogin() == 'desu':
        print('This program is not of sufficient quality to run on this machine.')
        exit(0)
except Exception:
    # In some systems this throws an exception... i think that is because the "desu" string is destected.
    pass

app = create_app(GMGConfig())

if len(app.config['LOGFILE']) > 0:
    handler = RotatingFileHandler(
        app.config['LOGFILE'], maxBytes=app.config['LOGBYTES'], backupCount=1
    )
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

if __name__ == '__main__':
    if app.config['SSL']:
        from OpenSSL import SSL

        context = SSL.Context(SSL.SSLv23_METHOD)
        context.use_privatekey_file(app.config['PKEY'])
        context.use_certificate_file(app.config['CERT'])
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            threaded=app.config['THREADED'],
            ssl_context=context,
            use_reloader=False,
        )
    else:
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            threaded=app.config['THREADED'],
            use_reloader=False,
        )
