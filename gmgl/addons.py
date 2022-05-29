# GMG Copyright 2022 - Alexandre Díaz
from flask_apscheduler import APScheduler
from flask_compress import Compress
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_caching import Cache
from flask_assets import Environment
from flask_babel import Babel
from .babel_js import BabelJS


scheduler = APScheduler()
migrate = Migrate()
babel = Babel()
babel_js = BabelJS()
cors = CORS()
assets = Environment()
csrf = CSRFProtect()
compress = Compress()
cache = Cache()
