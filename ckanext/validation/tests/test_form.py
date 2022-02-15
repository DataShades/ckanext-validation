import json
import io
import mock
import datetime
import unittest

from nose.tools import assert_in, assert_equals, with_setup

from ckantoolkit.tests import factories, helpers
from ckantoolkit.tests.helpers import (
    submit_and_follow, webtest_submit, call_action,
    reset_db
)

from ckanext.validation.model import create_tables, tables_exist
from ckanext.validation.tests.helpers import (
    VALID_CSV, INVALID_CSV, mock_uploads
)


def _get_resource_new_page_as_sysadmin(app, id):
    user = factories.Sysadmin()
    env = {'REMOTE_USER': user['name'].encode('ascii')}
    response = app.get(
        url='/dataset/new_resource/{}'.format(id),
        extra_environ=env,
    )
    return env, response


def _get_resource_update_page_as_sysadmin(app, id, resource_id):
    user = factories.Sysadmin()
    env = {'REMOTE_USER': user['name'].encode('ascii')}
    response = app.get(
        url='/dataset/{}/resource_edit/{}'.format(id, resource_id),
        extra_environ=env,
    )
    return env, response


def _setup_function(self):
    reset_db()
    if not tables_exist():
        create_tables()
    self.owner_org = factories.Organization(name='test-org')


@with_setup(_setup_function)
class TestResourceSchemaForm(object):

    def test_resource_form_includes_json_fields(self):
        dataset = factories.Dataset(owner_org=self.owner_org['id'])

        app = helpers._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']
        assert_in('schema', form.fields)
        assert_equals(form.fields['schema'][0].tag, 'input')
        assert_equals(form.fields['schema_json'][0].tag, 'textarea')
        assert_equals(form.fields['schema_url'][0].tag, 'input')

    def test_resource_form_create(self):
        dataset = factories.Dataset(owner_org=self.owner_org['id'])

        app = helpers._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']

        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'}
            ]
        }
        json_value = json.dumps(value)

        form['url'] = 'https://example.com/data.csv'
        form['schema'] = json_value

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['schema'], value)

    def test_resource_form_create_json(self):
        dataset = factories.Dataset(owner_org=self.owner_org['id'])

        app = helpers._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']

        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'}
            ]
        }
        json_value = json.dumps(value)

        form['url'] = 'https://example.com/data.csv'
        form['schema_json'] = json_value

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['schema'], value)

    @mock_uploads
    def test_resource_form_create_upload(self, mock_open):
        dataset = factories.Dataset(owner_org=self.owner_org['id'])

        app = helpers._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']

        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'}
            ]
        }
        json_value = json.dumps(value)

        upload = ('schema_upload', 'schema.json', json_value)
        form['url'] = 'https://example.com/data.csv'

        webtest_submit(
            form, 'save', upload_files=[upload], extra_environ=env)

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['schema'], value)

    def test_resource_form_create_url(self):
        dataset = factories.Dataset(owner_org=self.owner_org['id'])

        app = helpers._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']

        value = 'https://example.com/schemas.json'

        form['url'] = 'https://example.com/data.csv'
        form['schema_json'] = value

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['schema'], value)

    def test_resource_form_update(self):
        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'}
            ]
        }
        dataset = factories.Dataset(
            owner_org=self.owner_org['id'],
            resources=[{
                'url': 'https://example.com/data.csv',
                'schema': value
            }]
        )

        app = helpers._get_test_app()
        env, response = _get_resource_update_page_as_sysadmin(
            app, dataset['id'], dataset['resources'][0]['id'])
        form = response.forms['resource-edit']

        assert_equals(
            form['schema'].value, json.dumps(value, indent=None))

        # Clear current value
        form['schema_json'] = ''

        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'},
                {'name': 'date'}
            ]
        }

        json_value = json.dumps(value)

        form['schema'] = json_value

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['schema'], value)

    def test_resource_form_update_json(self):
        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'}
            ]
        }
        dataset = factories.Dataset(
            owner_org=self.owner_org['id'],
            resources=[{
                'url': 'https://example.com/data.csv',
                'schema': value
            }]
        )

        app = helpers._get_test_app()
        env, response = _get_resource_update_page_as_sysadmin(
            app, dataset['id'], dataset['resources'][0]['id'])
        form = response.forms['resource-edit']

        assert_equals(
            form['schema_json'].value, json.dumps(value, indent=2))

        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'},
                {'name': 'date'}
            ]
        }

        json_value = json.dumps(value)

        form['schema_json'] = json_value

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['schema'], value)

    def test_resource_form_update_url(self):
        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'}
            ]
        }
        dataset = factories.Dataset(
            owner_org=self.owner_org['id'],
            resources=[{
                'url': 'https://example.com/data.csv',
                'schema': value
            }]
        )

        app = helpers._get_test_app()
        env, response = _get_resource_update_page_as_sysadmin(
            app, dataset['id'], dataset['resources'][0]['id'])
        form = response.forms['resource-edit']

        assert_equals(
            form['schema_json'].value, json.dumps(value, indent=2))

        value = 'https://example.com/schema.json'

        form['schema_url'] = value

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['schema'], value)

    def test_resource_form_update_upload(self):
        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'}
            ]
        }
        dataset = factories.Dataset(
            owner_org=self.owner_org['id'],
            resources=[{
                'url': 'https://example.com/data.csv',
                'schema': value
            }]
        )

        app = helpers._get_test_app()
        env, response = _get_resource_update_page_as_sysadmin(
            app, dataset['id'], dataset['resources'][0]['id'])
        form = response.forms['resource-edit']

        assert_equals(
            form['schema_json'].value, json.dumps(value, indent=2))

        value = {
            'fields': [
                {'name': 'code'},
                {'name': 'department'},
                {'name': 'date'}
            ]
        }

        json_value = json.dumps(value)

        upload = ('schema_upload', 'schema.json', json_value)
        form['url'] = 'https://example.com/data.csv'

        webtest_submit(
            form, 'save', upload_files=[upload], extra_environ=env)

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['schema'], value)


@with_setup(_setup_function)
class TestResourceValidationOptionsForm(object):

    def test_resource_form_includes_json_fields(self):
        dataset = factories.Dataset(owner_org=self.owner_org['id'])

        app = helpers._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']
        assert_in('validation_options', form.fields)
        assert_equals(form.fields['validation_options'][0].tag, 'textarea')

    def test_resource_form_create(self):
        dataset = factories.Dataset(owner_org=self.owner_org['id'])

        app = helpers._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']

        value = {
            'delimiter': ';',
            'headers': 2,
            'skip_rows': ['#'],
        }
        json_value = json.dumps(value)

        form['url'] = 'https://example.com/data.csv'
        form['validation_options'] = json_value

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['validation_options'], value)

    def test_resource_form_update(self):
        value = {
            'delimiter': ';',
            'headers': 2,
            'skip_rows': ['#'],
        }

        dataset = factories.Dataset(
            owner_org=self.owner_org['id'],
            resources=[{
                'url': 'https://example.com/data.csv',
                'validation_options': value
            }]
        )

        app = helpers._get_test_app()
        env, response = _get_resource_update_page_as_sysadmin(
            app, dataset['id'], dataset['resources'][0]['id'])
        form = response.forms['resource-edit']

        assert_equals(
            form['validation_options'].value, json.dumps(
                value, indent=2, sort_keys=True))

        value = {
            'delimiter': ';',
            'headers': 2,
            'skip_rows': ['#'],
            'skip_tests': ['blank-rows'],
        }

        json_value = json.dumps(value)

        form['url'] = 'https://example.com/data.csv'
        form['validation_options'] = json_value

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['validation_options'], value)


@with_setup(_setup_function)
class TestResourceValidationOnCreateForm(object):

    @mock_uploads
    @helpers.change_config('ckanext.validation.run_on_create_sync', True)
    def test_resource_form_create_valid(self, mock_open):
        dataset = factories.Dataset(owner_org=self.owner_org['id'])

        app = helpers._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']

        upload = ('upload', 'valid.csv', VALID_CSV)

        valid_stream = io.BufferedReader(io.BytesIO(VALID_CSV))

        with mock.patch('io.open', return_value=valid_stream):

            submit_and_follow(app, form, env, 'save', upload_files=[upload])

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['validation_status'], 'success')
        assert 'validation_timestamp' in dataset['resources'][0]

    @mock_uploads
    @helpers.change_config('ckanext.validation.run_on_create_sync', True)
    def test_resource_form_create_invalid(self, mock_open):
        dataset = factories.Dataset(owner_org=self.owner_org['id'])

        app = helpers._get_test_app()
        env, response = _get_resource_new_page_as_sysadmin(app, dataset['id'])
        form = response.forms['resource-edit']

        upload = ('upload', 'invalid.csv', INVALID_CSV)

        invalid_stream = io.BufferedReader(io.BytesIO(INVALID_CSV))

        with mock.patch('io.open', return_value=invalid_stream):

            response = webtest_submit(
                form, 'save', upload_files=[upload], extra_environ=env)

        assert_in('validation', response.body)
        assert_in('missing-value', response.body)
        assert_in('Row 2 has a missing value in column 4', response.body)


@with_setup(_setup_function)
class TestResourceValidationOnUpdateForm(object):

    @mock_uploads
    @helpers.change_config('ckanext.validation.run_on_update_sync', True)
    def test_resource_form_update_valid(self, mock_open):

        dataset = factories.Dataset(
            owner_org=self.owner_org['id'],
            resources=[{
                'url': 'https://example.com/data.csv'
            }]
        )

        app = helpers._get_test_app()
        env, response = _get_resource_update_page_as_sysadmin(
            app, dataset['id'], dataset['resources'][0]['id'])
        form = response.forms['resource-edit']

        upload = ('upload', 'valid.csv', VALID_CSV)

        valid_stream = io.BufferedReader(io.BytesIO(VALID_CSV))

        with mock.patch('io.open', return_value=valid_stream):

            submit_and_follow(app, form, env, 'save', upload_files=[upload])

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['validation_status'], 'success')
        assert 'validation_timestamp' in dataset['resources'][0]

    @unittest.skip("TODO debug this later")
    @mock_uploads
    @helpers.change_config('ckanext.validation.run_on_update_sync', True)
    def test_resource_form_update_invalid(self, mock_open):

        dataset = factories.Dataset(
            owner_org=self.owner_org['id'],
            resources=[{
                'url': 'https://example.com/data.csv'
            }]
        )

        app = helpers._get_test_app()
        env, response = _get_resource_update_page_as_sysadmin(
            app, dataset['id'], dataset['resources'][0]['id'])
        form = response.forms['resource-edit']

        upload = ('upload', 'invalid.csv', INVALID_CSV)

        invalid_stream = io.BufferedReader(io.BytesIO(INVALID_CSV))

        with mock.patch('io.open', return_value=invalid_stream):

            response = webtest_submit(
                form, 'save', upload_files=[upload], extra_environ=env)

        assert_in('validation', response.body)
        assert_in('missing-value', response.body)
        assert_in('Row 2 has a missing value in column 4', response.body)


@with_setup(_setup_function)
class TestResourceValidationFieldsPersisted(object):

    @helpers.change_config('ckanext.validation.run_on_update_sync', False)
    def test_resource_form_fields_are_persisted(self):

        dataset = factories.Dataset(
            owner_org=self.owner_org['id'],
            resources=[{
                'url': 'https://example.com/data.csv',
                'validation_status': 'success',
                'validation_timestamp': datetime.datetime.now().isoformat()
            }]
        )

        app = helpers._get_test_app()
        env, response = _get_resource_update_page_as_sysadmin(
            app, dataset['id'], dataset['resources'][0]['id'])
        form = response.forms['resource-edit']

        form['description'] = 'test desc'

        submit_and_follow(app, form, env, 'save')

        dataset = call_action('package_show', id=dataset['id'])

        assert_equals(dataset['resources'][0]['validation_status'], 'success')
        assert 'validation_timestamp' in dataset['resources'][0]
        assert_equals(dataset['resources'][0]['description'], 'test desc')
