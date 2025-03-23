
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache


# Instantiate your Marshmallow object
ma = Marshmallow()

# Instantiate your Limiter object
limiter = Limiter(key_func=get_remote_address)

# , default_limits=["20 per hour"] add to above

# Instantiate your Cache object
cache = Cache()