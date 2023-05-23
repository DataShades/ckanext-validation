# encoding: utf-8

from werkzeug.datastructures import FileStorage as MockFileStorage  # noqa

MOCK_COULD_BE_VALIDATED = "ckanext.validation.utils.is_resource_could_be_validated"
MOCK_SYNC_VALIDATE = "ckanext.validation.utils.validate"
MOCK_ASYNC_VALIDATE = "ckanext.validation.jobs.validate"
MOCK_ENQUEUE_JOB = "ckantoolkit.enqueue_job"

INVALID_CSV = b'a,b,c,d\n1,2,3'
VALID_CSV = b'a,b,c,d\n1,2,3,4'

SCHEMA = {
    "fields": [{
        "type": "integer",
        "name": "a",
        "format": "default"
    }, {
        "type": "integer",
        "name": "b",
        "format": "default"
    }, {
        "type": "integer",
        "name": "c",
        "format": "default"
    }, {
        "type": "integer",
        "name": "d",
        "format": "default"
    }]
}

NEW_SCHEMA = {
    "fields": [{
        "type": "integer",
        "name": "a",
        "format": "default"
    }, {
        "type": "integer",
        "name": "b",
        "format": "default"
    }]
}

VALID_REPORT = {
    'error-count': 0,
    'table-count': 1,
    'tables': [{
        'error-count': 0,
        'errors': [],
        'headers': ['name', 'ward', 'party', 'other'],
        'row-count': 79,
        'source': 'http://example.com/valid.csv',
        'time': 0.007,
        'valid': True
    }],
    'time': 0.009,
    'valid': True,
    'warnings': []
}

INVALID_REPORT = {
    'error-count': 2,
    'table-count': 1,
    'tables': [{
        'error-count': 2,
        'errors': [
            {
                'code': 'blank-header',
                'column-number': 3,
                'message': 'Header in column 3 is blank',
                'row': None,
                'row-number': None
            },
            {
                'code': 'duplicate-header',
                'column-number': 4,
                'message': 'Header in column 4 is duplicated to ...',
                'row': None,
                'row-number': None
            },
        ],
        'headers': ['name', 'ward', 'party', 'other'],
        'row-count': 79,
        'source': 'http://example.com/invalid.csv',
        'time': 0.007,
        'valid': False,
    }],
    'time': 0.009,
    'valid': False,
    'warnings': [],
}

ERROR_REPORT = {
    'error-count': 0,
    'table-count': 0,
    'warnings': ['Some warning'],
}

VALID_REPORT_LOCAL_FILE = {
    'error-count': 0,
    'table-count': 1,
    'tables': [{
        'error-count': 0,
        'errors': [],
        'headers': ['name', 'ward', 'party', 'other'],
        'row-count': 79,
        'source': '/data/resources/31f/d4c/1e-9c82-424b-b78b-48cd08db6e64',
        'time': 0.007,
        'valid': True
    }],
    'time': 0.009,
    'valid': True,
    'warnings': []
}
