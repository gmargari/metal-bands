# -*- coding: utf-8 -*-
import os

# Eve configuration global settings: http://python-eve.org/config.html

URL_PREFIX = 'rest'
API_VERSION = 'v1'
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = '5000'

# DB connection and other settings are stored in environment variables
DEBUG = bool(os.environ.get('SOCIALCAR_DEBUG', False))
MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))
MONGO_USERNAME = os.environ.get('MONGO_USERNAME', '')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', '')
MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'metalbands' + API_VERSION.replace('.', '-'))
# USE_SENTRY = bool(os.environ.get('USE_SENTRY', False))
# SENTRY_DSN = os.environ.get('SENTRY_DSN', 'https://ccbeb003ed194f0bab837d8c33269cef:ad3c0bdbe07740799fcf3a30fe491449@sentry.io/136957')
# FCM_HOST = os.environ.get('FCM_HOST', 'localhost')
# FCM_PORT = int(os.environ.get('FCM_PORT', 8081))
# FCM_API_KEY = os.environ.get('FCM_API_KEY', 'AAAAzxz0MLQ:APA91bEUjKy-Qi8xhmQUnX0r_38Ui-7GPw9SMqBOanlTbCc995q6zXi4pzWGyXbRtSsNNIKwgkSHSca_58nQlwGSVpOQLkgiKjcRg7gEq1QiXhLkWGFi2b8mHPhPexbv6GEX6RLpa-zQLtJLKLton39zw7TeYoMq2w')

# Disable XML support (use only JSON)
XML = False

# Show database schema at this endpoint
SCHEMA_ENDPOINT = 'schema'

# Methods enabled for resources/collections (e.g. url.com/resource)
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Methods enabled for individual items (e.g. url.com/resource/item)
ITEM_METHODS = ['GET', 'PUT', 'PATCH', 'DELETE']

# Hypermedia as the Engine of Application State
# http://python-eve.org/features.html#hateoas
HATEOAS = False

# When serving requests, matching JSON strings will be parsed and stored as
# datetime values. In responses, datetime values will be rendered as JSON
# strings using this format.
DATE_FORMAT = '%d/%m/%Y %H:%M:%S'

# Disable concurrency control
IF_MATCH = False

# Versioning: when we edit an object we also keep its previous version.
# http://python-eve.org/features.html#document-versioning
# TODO: Probably disable in production
# VERSIONING = True

# Soft deletes: When deleting an object keep it in database but remove it from
# results on API requests
# http://python-eve.org/features.html#soft-delete
# SOFT_DELETE = True

# Log all edit operations (POST, PATCH PUT and DELETE)
# OPLOG = False

# When True, POST, PUT, and PATCH responses only return automatically handled
# meta fields such as object id, date_created. etc. When False, the entire
# document will be sent.
BANDWIDTH_SAVER = False

# Enable pagination for GET requests.
PAGINATION = True
# Each GET request returns at most these many objects
PAGINATION_DEFAULT = 10
# User can change the number of objects return on GET request using query
# parameter 'max_results' (e.g., &max_results=30). Values exceeding this
# pagination limit will be silently replaced with this value.
# PAGINATION_LIMIT = 100
# Key for the pages query parameter
QUERY_PAGE = 'page'
# Key for the max results query parameter.
QUERY_MAX_RESULTS = 'limit'

# Enable Embedded Resource Serialization: if a document field is referencing
# a document in another resource, clients can request the referenced document
# to be embedded within the requested document.
# http://python-eve.org/features.html#embedded-docs
# EMBEDDING = True
# Keyword to use for embedding a field. E.g. url.com/users?embed={'cars':1}
# QUERY_EMBEDDED = 'embed'

# List of fields on which filtering is allowed. Can be set to [] (no filters
# allowed) or ['*'] (filters allowed on every field).
ALLOWED_FILTERS = [ ]

# Serving media files at a dedicated endpoint
# http://python-eve.org/features.html#serving-media-files-at-a-dedicated-endpoint
# Disable default behaviour, return media as URL instead
RETURN_MEDIA_AS_BASE64_STRING = False
RETURN_MEDIA_AS_URL = True
MEDIA_ENDPOINT = 'media'

#===============================================================================
# bands
#===============================================================================
bands = {
    'schema': {
        'id': {
            'type': 'integer',
            'required': True,
            'unique': True,
        },
        'name': {
            'type': 'string',
            'required': True,
        },
        'url': {
            'type': 'string',
            # 'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            'required': True,
        },
        'country': {
            'type': 'string',
            'required': True,
        },
        'genre': {
            'type': 'string',
            'required': True,
        },
        'status': {
            'type': 'string',
            # 'allowed': [ 'Active', 'Inactive',  ],
            'required': True,
        },
        'albums': {
            'type': 'list',
            'required': True,
            'schema': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                        'required': True,
                    },
                    'url': {
                        'type': 'string',
                        'required': True,
                    },
                    'type': {
                        'type': 'string',
                        'required': True,
                    },
                    'year': {
                        'type': 'string', # integer
                        'required': True,
                    },
                    'songs': {
                        'type': 'list',
                        'required': True,
                        'schema': {
                            'type': 'list',
                        },
                    },
                },
            },
        },
        'info': {
            'type': 'dict',
            'schema': {
                "country of origin:": {
                    'type': 'string',
                },
                "location:":  {
                    'type': 'string',
                },
                "status:":  {
                    'type': 'string',
                },
                "formed in:":  {
                    'type': 'integer',
                },
                "genre:":  {
                    'type': 'string',
                },
                "lyrical themes:":  {
                    'type': 'string',
                },
                "current label:":  {
                    'type': 'string',
                },
                "last label:":  {
                    'type': 'string',
                },
                "years active:":  {
                    'type': 'string',
                },
            },
        },
        'similar_bands': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                        'required': True,
                    },
                    'country': {
                        'type': 'string',
                        'required': True,
                    },
                    'genre': {
                        'type': 'string',
                        'required': True,
                    },
                    'score': {
                        'type': 'string', # integer
                        'required': True,
                    },
                },
            },
        },
    },
}

# The DOMAIN dict explains which resources will be available and how they will
# be accessible to the API consumer.
DOMAIN = {
    'bands': bands,
}
