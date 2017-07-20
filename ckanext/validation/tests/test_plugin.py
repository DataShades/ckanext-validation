import mock
from nose.tools import assert_equals

from ckan.tests.helpers import call_action, reset_db
from ckan.tests import factories

import ckantoolkit

from ckanext.validation.model import create_tables, tables_exist
from ckanext.validation.jobs import run_validation_job


class TestResourceControllerHooks(object):

    def setup(self):
        reset_db()
        if not tables_exist():
            create_tables()

    @mock.patch.object(ckantoolkit, 'enqueue_job')
    def test_validation_does_not_run_on_other_fields(self, mock_enqueue):

        resource = factories.Resource(format='CSV')

        resource['description'] = 'Some resource'

        call_action('resource_update', {}, **resource)

        mock_enqueue.assert_not_called()

    @mock.patch.object(ckantoolkit, 'enqueue_job')
    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):

        resource = factories.Resource(format='PDF')

        call_action('resource_update', {}, **resource)

        mock_enqueue.assert_not_called()

    @mock.patch.object(ckantoolkit, 'enqueue_job')
    def test_validation_run_on_upload(self, mock_enqueue):

        resource = factories.Resource(format='CSV')

        resource['upload'] = 'mock_upload'

        call_action('resource_update', {}, **resource)

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])

    @mock.patch.object(ckantoolkit, 'enqueue_job')
    def test_validation_run_on_url_change(self, mock_enqueue):

        resource = factories.Resource(format='CSV')

        resource['url'] = 'http://some.new.url'

        call_action('resource_update', {}, **resource)

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])

    @mock.patch.object(ckantoolkit, 'enqueue_job')
    def test_validation_run_on_schema_change(self, mock_enqueue):

        resource = factories.Resource(format='CSV', schema={'a': 'b'})

        resource['schema'] = {'c': 'd'}

        call_action('resource_update', {}, **resource)

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])

    @mock.patch.object(ckantoolkit, 'enqueue_job')
    def test_validation_run_on_format_change(self, mock_enqueue):

        resource = factories.Resource()

        resource['format'] = 'CSV'

        call_action('resource_update', {}, **resource)

        assert_equals(mock_enqueue.call_count, 1)

        assert_equals(mock_enqueue.call_args[0][0], run_validation_job)
        assert_equals(mock_enqueue.call_args[0][1][0]['id'], resource['id'])
