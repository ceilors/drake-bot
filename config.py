import os


USE_HEROKU = True
TOKEN = os.environ.get('TOKEN')
PORT = int(os.environ.get('PORT', '8443'))
APP = os.environ.get('APP_NAME')
