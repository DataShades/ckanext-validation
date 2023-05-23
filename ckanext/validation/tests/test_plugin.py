# encoding: utf-8
import io

import mock
import pytest

from ckan.tests.helpers import call_action
from ckan.tests import factories

import ckanext.validation.settings as s
import ckanext.validation.tests.helpers as helpers
from ckanext.validation.jobs import run_validation_job


def _assert_validation_enqueued(mock_enqueue, resource_id):
    assert mock_enqueue.call_count == 1

    assert mock_enqueue.call_args[1]['fn'] == run_validation_job
    assert mock_enqueue.call_args[1]['kwargs']['resource'] == resource_id


@pytest.mark.usefixtures("clean_db", "validation_setup")
@pytest.mark.ckan_config(s.ASYNC_UPDATE_KEY, True)
@pytest.mark.ckan_config(s.ASYNC_CREATE_KEY, True)
@mock.patch(helpers.MOCK_ENQUEUE_JOB, return_value=True)
class TestResourceControllerHooksUpdate(object):

    def test_validation_does_not_run_on_other_fields(self, mock_enqueue):
        """Validation should not be triggered during an update, asa description
        change is not a sufficient change to revalidate the resource"""
        resource = factories.Resource(format="CSV",
                                      schema=helpers.SCHEMA,
                                      url="https://some.url")

        mock_enqueue.assert_called_once()

        resource['description'] = 'Some resource'

        call_action('resource_update', {}, **resource)

        mock_enqueue.assert_called_once()

    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):
        """PDF and TTF formats are not supported"""
        resource = factories.Resource(format="PDF")

        mock_enqueue.assert_not_called()

        resource["format"] = "TTF"

        call_action('resource_update', {}, **resource)

        mock_enqueue.assert_not_called()

    def test_validation_run_on_upload(self, mock_enqueue, resource_factory):
        """Validation must be triggered during update on upload new file"""
        mock_upload = helpers.MockFileStorage(io.BytesIO(helpers.VALID_CSV),
                                              'valid.csv')

        resource = resource_factory(format="pdf")

        resource['format'] = 'csv'
        resource['upload'] = mock_upload

        call_action('resource_update', {}, **resource)

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_on_url_change(self, mock_enqueue,
                                          resource_factory):
        """Validation must be triggered during update on changing URL"""
        resource = resource_factory(format="PDF")

        resource['url'] = "https://some.new.url"
        resource['format'] = "CSV"

        call_action('resource_update', {}, **resource)

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_on_schema_change(self, mock_enqueue,
                                             resource_factory):
        """Validation must be triggered during update on changing URL"""
        resource = resource_factory(format="PDF")

        resource['schema'] = helpers.NEW_SCHEMA
        resource['format'] = "CSV"

        call_action('resource_update', {}, **resource)

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_on_format_change(self, mock_enqueue,
                                             resource_factory):
        """Validation must be triggered during update on changing format"""
        resource = resource_factory(format="PDF")

        mock_enqueue.assert_not_called()

        resource['format'] = 'CSV'

        call_action('resource_update', {}, **resource)

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_on_validation_options_change(
            self, mock_enqueue, resource_factory):
        """Validation must be triggered during update on changing
        validation_options"""
        resource = resource_factory(format="PDF")

        mock_enqueue.assert_not_called()

        resource['validation_options'] = {'headers': 1, 'skip_rows': ['#']}
        resource['format'] = 'CSV'

        call_action('resource_update', {}, **resource)

        _assert_validation_enqueued(mock_enqueue, resource['id'])


@pytest.mark.usefixtures("clean_db", "validation_setup")
@pytest.mark.ckan_config(s.ASYNC_UPDATE_KEY, True)
@pytest.mark.ckan_config(s.ASYNC_CREATE_KEY, True)
@mock.patch(helpers.MOCK_ENQUEUE_JOB)
class TestResourceControllerHooksCreate(object):

    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):
        factories.Resource(format='PDF')

        mock_enqueue.assert_not_called()

    def test_validation_runs_with_upload(self, mock_enqueue, resource_factory):
        resource_factory()

        mock_enqueue.assert_called()

    def test_validation_run_with_url(self, mock_enqueue, resource_factory):
        resource = resource_factory(url='http://some.data')

        _assert_validation_enqueued(mock_enqueue, resource['id'])


@pytest.mark.usefixtures("clean_db", "validation_setup")
@pytest.mark.ckan_config(s.ASYNC_UPDATE_KEY, True)
@pytest.mark.ckan_config(s.ASYNC_CREATE_KEY, True)
@mock.patch(helpers.MOCK_ENQUEUE_JOB)
class TestPackageControllerHooksCreate(object):

    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):
        factories.Dataset(resources=[{'format': 'PDF'}])

        mock_enqueue.assert_not_called()

    def test_validation_run_with_upload(self, mock_enqueue):
        resource = {
            'id': 'test-resource-id',
            'format': 'CSV',
            'url_type': 'upload',
            'schema': helpers.SCHEMA
        }
        factories.Dataset(resources=[resource])

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_with_url(self, mock_enqueue):
        resource = {
            'id': 'test-resource-id',
            'format': 'CSV',
            'url': 'http://some.data',
            'schema': helpers.SCHEMA
        }

        factories.Dataset(resources=[resource])

        _assert_validation_enqueued(mock_enqueue, resource['id'])

    def test_validation_run_only_supported_formats(self, mock_enqueue):

        resource1 = {
            'id': 'test-resource-id-1',
            'format': 'CSV',
            'url': 'http://some.data',
            'schema': helpers.SCHEMA
        }
        resource2 = {
            'id': 'test-resource-id-2',
            'format': 'PDF',
            'url': 'http://some.doc',
            'schema': helpers.SCHEMA
        }

        factories.Dataset(resources=[resource1, resource2])

        _assert_validation_enqueued(mock_enqueue, resource1['id'])


@pytest.mark.usefixtures("clean_db", "validation_setup")
@pytest.mark.ckan_config(s.ASYNC_UPDATE_KEY, True)
@pytest.mark.ckan_config(s.ASYNC_CREATE_KEY, True)
@mock.patch(helpers.MOCK_ENQUEUE_JOB, return_value=True)
class TestPackageControllerHooksUpdate(object):

    def test_validation_runs_with_url(self, mock_enqueue):
        package = factories.Dataset(resources=[{
            "format": "PDF",
            "schema": helpers.SCHEMA,
            "url": "http://some.data"
        }])

        assert mock_enqueue.call_count == 0

        package['resources'][0]['format'] = 'CSV'
        package['resources'][0]['url'] = 'http://some.other.data'

        call_action('package_update', **package)

        assert mock_enqueue.call_count == 1

    def test_validation_does_not_run_on_other_formats(self, mock_enqueue):

        resource = {
            'id': 'test-resource-id',
            'format': 'PDF',
            'url': 'http://some.doc'
        }
        dataset = factories.Dataset(resources=[resource])

        mock_enqueue.assert_not_called()

        dataset['resources'][0]['url'] = 'http://some.other.doc'

        call_action('package_update', {}, **dataset)

        mock_enqueue.assert_not_called()

    def test_validation_run_only_supported_formats(self, mock_enqueue):

        resource1 = {
            'id': 'test-resource-id-1',
            'format': 'CSV',
            'url': 'http://some.data',
            'schema': helpers.SCHEMA
        }
        resource2 = {
            'id': 'test-resource-id-2',
            'format': 'PDF',
            'url': 'http://some.doc',
            'schema': helpers.SCHEMA
        }

        dataset = factories.Dataset(resources=[resource1, resource2])

        # one resource must be validated during package + resources creation
        mock_enqueue.assert_called()

        dataset['resources'][0]['url'] = 'http://some.other.data'

        call_action('package_update', {}, **dataset)

        _assert_validation_enqueued(mock_enqueue, resource1['id'])
