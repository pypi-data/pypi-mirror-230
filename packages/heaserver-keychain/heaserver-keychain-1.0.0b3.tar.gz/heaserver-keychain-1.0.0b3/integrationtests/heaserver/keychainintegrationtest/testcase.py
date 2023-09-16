"""
Creates a test case class for use with the unittest library that is built into Python.
"""

from heaserver.service.testcase.microservicetestcase import get_test_case_cls_default
from heaserver.service.testcase.dockermongo import DockerMongoManager
from heaserver.keychain import service
from heaobject.user import NONE_USER
from heaserver.service.testcase.expectedvalues import Action

db_store = {
    service.MONGODB_CREDENTIALS_COLLECTION: [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'invites': [],
        'modified': None,
        'name': 'reximus',
        'owner': NONE_USER,
        'shares': [],
        'source': None,
        'type': 'heaobject.keychain.Credentials',
        'created': None,
        'account': None,
        'where': None,
        'password': None
    },
        {
            'id': '0123456789ab0123456789ab',
            'created': None,
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'Luximus',
            'invites': [],
            'modified': None,
            'name': 'luximus',
            'owner': NONE_USER,
            'shares': [],
            'source': None,
            'type': 'heaobject.keychain.Credentials',
            'created': None,
            'account': None,
            'where': None,
            'password': None
        }]}

TestCase = get_test_case_cls_default(coll=service.MONGODB_CREDENTIALS_COLLECTION,
                                     href='http://localhost:8080/credentials',
                                     wstl_package=service.__package__,
                                     db_manager_cls=DockerMongoManager,
                                     fixtures=db_store,
                                     get_actions=[Action(name='heaserver-keychain-credentials-get-properties',
                                                         rel=['hea-properties']),
                                                  Action(name='heaserver-keychain-credentials-open',
                                                         url='http://localhost:8080/credentials/{id}/opener',
                                                         rel=['hea-opener']),
                                                  Action(name='heaserver-keychain-credentials-duplicate',
                                                         url='http://localhost:8080/credentials/{id}/duplicator',
                                                         rel=['hea-duplicator']),
                                                  Action(name='heaserver-keychain-credentials-get-self',
                                                             url='http://localhost:8080/credentials/{id}',
                                                             rel=['self'])
                                                  ],
                                     get_all_actions=[Action(name='heaserver-keychain-credentials-get-properties',
                                                             rel=['hea-properties']),
                                                      Action(name='heaserver-keychain-credentials-open',
                                                             url='http://localhost:8080/credentials/{id}/opener',
                                                             rel=['hea-opener']),
                                                      Action(name='heaserver-keychain-credentials-duplicate',
                                                             url='http://localhost:8080/credentials/{id}/duplicator',
                                                             rel=['hea-duplicator']),
                                                      Action(name='heaserver-keychain-credentials-get-self',
                                                             url='http://localhost:8080/credentials/{id}',
                                                             rel=['self'])],
                                     duplicate_action_name='heaserver-keychain-credentials-duplicate-form')
