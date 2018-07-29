from datetime import datetime, timedelta
import logging
import mimetypes

import cloudstorage as gcs
from flask import Flask, request
from google.appengine.api import app_identity


app = Flask(__name__)
app.config.from_envvar('FLASK_CONFIG')

logging.basicConfig(level=app.config['LOG_LEVEL'])


@app.route('/download/<filename>')
def download(filename):
    bucket_name = app.config.get('GCS_BUCKET',
        app_identity.get_default_gcs_bucket_name()
    )

    user_key = request.args.get('key', '')

    content_type, _ = mimetypes.guess_type(request.path)

    gcs_path = '/%s/downloads/%s' % (bucket_name, filename)
    gcs_key_path = '%s.key.txt' % gcs_path

    try:
        with gcs.open(gcs_key_path, mode='r') as fh:
            line = fh.readline()
            stored_key, timeout = line.rsplit('|', 1)
            stored_key = stored_key.strip()
            timeout = timeout.strip()

    except gcs.NotFoundError:
        logging.exception('Could not read key file')
        return 'Error validating request.', 500

    if not stored_key:
        return 'Error validating request.', 500

    if user_key != stored_key:
        logging.debug('Invalid user key: %s' % user_key)
        return 'Invalid key.', 401

    logging.info('timeout: %s' % timeout)

    try:
        ttl = int(timeout)
        expires_at = datetime.now() + timedelta(seconds=ttl)
        with gcs.open(gcs_key_path,
                      mode='w',
                      content_type='text/plain') as fh:
            logging.debug(
                'Updating key file with expire time: %s' % expires_at)
            fh.write('%s|%s' % (stored_key, expires_at.isoformat()))
    except ValueError:
        logging.info('Checking expiration time')
        expires_at = datetime.strptime(timeout, '%Y-%m-%dT%H:%M:%S.%f')
        if datetime.now() > expires_at:
            return 'File has expired.', 401

    with gcs.open(gcs_path, mode='r') as fh:
        data = fh.read()

    return data, 200, {'Content-Type': content_type}


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
