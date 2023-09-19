import decouple as dc


class Config:
    host = dc.config("HOST", default="localhost")
    port = dc.config("PORT", default=3000, cast=int)
    debug = dc.config("ENV", default="development") == "development"

    # db configuration
    db_uri = dc.config("DB_HOST", default='sqlite:///database.db')

    # auth configuration
    jwt_secret = dc.config("JWT_SECRET")
    jwt_algorithm = dc.config("JWT_ALGORITHM")
