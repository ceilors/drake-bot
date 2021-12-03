import os

TOKEN = os.environ.get('TOKEN')
PORT = int(os.environ.get('PORT', '8443'))
APP = os.environ.get('HEROKU_APP_NAME')
