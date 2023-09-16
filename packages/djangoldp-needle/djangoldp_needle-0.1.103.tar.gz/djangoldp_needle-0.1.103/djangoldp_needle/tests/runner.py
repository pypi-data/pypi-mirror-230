import sys

import django
from django.conf import settings as django_settings
from djangoldp.conf.ldpsettings import LDPSettings

# Pycharm debug related code
# import pydevd_pycharm
# pydevd_pycharm.settrace('host.docker.internal', port=9000, stdoutToServer=True, stderrToServer=True, suspend=False)

# create a test configuration
config = {
    # add the packages to the reference list
    'ldppackages': [
        'djangoldp_account',
        'djangoldp_needle',
        'djangoldp_needle.tests'
    ],

    # required values for server
    'server': {
        'AUTH_USER_MODEL': 'djangoldp_account.LDPUser',
        'REST_FRAMEWORK': {
            'DEFAULT_PAGINATION_CLASS': 'djangoldp.pagination.LDPPagination',
            'PAGE_SIZE': 5
        },
        # map the config of the core settings (avoid asserts to fail)
        'SITE_URL': 'http://happy-dev.fr',
        'BASE_URL': 'http://happy-dev.fr',
        'INSTANCE_DEFAULT_CLIENT': 'http://front',

        'NEEDLE_AVATARS': {
            'chenille': {
                'name': 'Chenille',
                'image': 'https://unpkg.com/@startinblox/component-needle/src/img/animals/chenille.png',
                'selectable': False,
                'level': 1
            },
            'phalene': {
                'name': 'Phalene',
                'image': 'https://unpkg.com/@startinblox/component-needle/src/img/animals/phalene.png',
                'selectable': False,
                'level': 2
            }
        }
    }
}

ldpsettings = LDPSettings(config)
django_settings.configure(ldpsettings)

django.setup()
from django.test.runner import DiscoverRunner

test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests([
    'djangoldp_needle.tests.test_first_annotation_on_user_creation',
    'djangoldp_needle.tests.test_annotation_target_add',
    'djangoldp_needle.tests.test_annotation_yarn',
    'djangoldp_needle.tests.test_annotation_activity',
    'djangoldp_needle.tests.test_date_parser',
    'djangoldp_needle.tests.test_annotation_intersection',
    'djangoldp_needle.tests.test_user_contact',
    'djangoldp_needle.tests.test_booklet_contributor_pending',
    'djangoldp_needle.tests.test_booklet_contributors_patch',
    'djangoldp_needle.tests.test_booklet_contributors_post',
    'djangoldp_needle.tests.test_booklet_contributors_delete',
    'djangoldp_needle.tests.test_booklets_add',
    'djangoldp_needle.tests.test_booklets_list',
    'djangoldp_needle.tests.test_booklets_add_annotation',
    'djangoldp_needle.tests.test_booklets_quit',
    'djangoldp_needle.tests.test_booklets_tags_list_all',
    'djangoldp_needle.tests.test_booklets_tags_list_from_booklet',
    'djangoldp_needle.tests.test_booklets_tags_add_all',
    'djangoldp_needle.tests.test_booklets_tags_get',
    'djangoldp_needle.tests.test_booklets_tag_targets_list_all',
    'djangoldp_needle.tests.test_booklets_tag_targets_list_from_booklet',
    'djangoldp_needle.tests.test_booklets_tag_targets_add_all',
    'djangoldp_needle.tests.test_booklets_tag_targets_get',
    'djangoldp_needle.tests.test_booklets_tag_targets_remove',
    'djangoldp_needle.tests.test_booklets_invitation',
    'djangoldp_needle.tests.test_booklets_bulk_delete',
    'djangoldp_needle.tests.test_needle_user_contact',
    'djangoldp_needle.tests.test_needle_user_contact_pending',
    'djangoldp_needle.tests.test_user_mail_change_token',
    'djangoldp_needle.tests.test_user_mail_change_token_validate',
    'djangoldp_needle.tests.test_user_serializer',
])
if failures:
    sys.exit(failures)

