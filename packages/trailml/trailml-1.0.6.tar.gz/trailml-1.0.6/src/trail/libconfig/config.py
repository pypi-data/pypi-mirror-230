class Config:
    FIREBASE_API_KEY = 'AIzaSyDBbIiCyAFkz_bZQb0hbP5wFB-ioF6xOyw'
    FIREBASE_AUTH_DOMAIN = 'trail-ml-9e15e.firebaseapp.com'
    GQL_ENDPOINT_URL = ''

    PRIMARY_USER_CONFIG_PATH = 'trailconfig.yml'
    SECONDARY_USER_CONFIG_PATH = '~/.config/trail.yml'


DEVELOPMENT_ENDPOINT_URL = 'http://127.0.0.1:5002'
PRODUCTION_ENDPOINT_URL = 'https://trail-ml-9e15e.ew.r.appspot.com'


class ProductionConfig(Config):
    PRESIGNED_URL_ENDPOINT = f'{PRODUCTION_ENDPOINT_URL}/generate_presigned_bucket_url'
    GQL_ENDPOINT_URL = f'{PRODUCTION_ENDPOINT_URL}/graphql'


class DevelopmentConfig(Config):
    PRESIGNED_URL_ENDPOINT = f'{DEVELOPMENT_ENDPOINT_URL}/generate_presigned_bucket_url'
    GQL_ENDPOINT_URL = f'{DEVELOPMENT_ENDPOINT_URL}/graphql'
