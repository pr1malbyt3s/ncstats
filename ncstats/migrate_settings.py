from .settings import *

DATABASES["default"]["USER"] = os.getenv('MIGRATE_USER')
DATABASES["default"]["PASSWORD"] = os.getenv('MIGRATE_PASS')