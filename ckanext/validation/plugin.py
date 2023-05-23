# encoding: utf-8

import json
import logging
import os

import ckantoolkit as tk

import ckan.plugins as p
from ckan.lib.plugins import DefaultTranslation

from . import settings as s, utils, validators
from .helpers import _get_helpers
from .logic import action, auth
from .model import tables_exist
from .plugin_mixins.flask_plugin import MixinPlugin

log = logging.getLogger(__name__)


class ValidationPlugin(MixinPlugin, p.SingletonPlugin, DefaultTranslation):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IResourceController, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IValidators)
    p.implements(p.ITranslation, inherit=True)

    # ITranslation
    def i18n_directory(self):
        u'''Change the directory of the .mo translation files'''
        return os.path.join(
            os.path.dirname(__file__),
            'i18n'
        )

    # IConfigurer

    def update_config(self, config_):
        if not tables_exist():
            init_command = 'ckan validation init-db'
            log.critical(u'''
The validation extension requires a database setup.
Validation pages will not be enabled.
Please run the following to create the database tables:
    %s''', init_command)

        tk.add_template_directory(config_, u'templates')
        tk.add_resource(u'assets', 'ckanext-validation')

    # IActions

    def get_actions(self):
        return action.get_actions()

    # IAuthFunctions

    def get_auth_functions(self):
        return auth.get_auth_functions()

    # ITemplateHelpers

    def get_helpers(self):
        return _get_helpers()

    # IValidators

    def get_validators(self):
        return validators.get_validators()

    # IResourceController

    # CKAN < 2.10
    def before_create(self, context, data_dict):
        return self.before_resource_create(context, data_dict)

    # CKAN >= 2.10
    def before_resource_create(self, context, data_dict):
        context['_resource_validation'] = True

        data_dict = utils.process_schema_fields(data_dict)

        if s.get_create_mode(context, data_dict) == s.ASYNC_MODE:
            return

        if utils.is_resource_could_be_validated(context, data_dict):
            utils.validate_resource(context, data_dict, new_resource=True)

    def _data_dict_is_dataset(self, data_dict):
        return (
            u'creator_user_id' in data_dict
            or u'owner_org' in data_dict
            or u'resources' in data_dict
            or data_dict.get(u'type') == u'dataset')

    # CKAN < 2.10
    def after_create(self, context, data_dict):
        if (self._data_dict_is_dataset(data_dict)):
            return self.after_dataset_create(context, data_dict)
        else:
            return self.after_resource_create(context, data_dict)

    # CKAN >= 2.10
    def after_resource_create(self, context, data_dict):
        if data_dict.pop('_success_validation', False):
            return utils.create_success_validation_job(data_dict["id"])

        if s.get_create_mode(context, data_dict) == s.SYNC_MODE:
            return

        if utils.is_resource_could_be_validated(context, data_dict):
            utils.validate_resource(context, data_dict, new_resource=True)

    # CKAN < 2.10
    def before_update(self, context, current_resource, updated_resource):
        return self.before_resource_update(context, current_resource, updated_resource)

    # CKAN >= 2.10
    def before_resource_update(self, context, current_resource, updated_resource):
        context['_resource_validation'] = True
        # avoid circular update, because validation job calls `resource_patch`
        # (which calls package_update)
        if context.get('_validation_performed'):
            return

        updated_resource = utils.process_schema_fields(updated_resource)
        validation_requires = utils.is_resource_requires_validation(
            context, current_resource, updated_resource)

        if not validation_requires:
            updated_resource['_do_not_validate'] = True
            return

        # if it's a sync mode, it's better run it before updating, because
        # the new uploaded file will be here
        if s.get_update_mode(context, updated_resource) == s.SYNC_MODE:
            utils.validate_resource(context, updated_resource)
        else:
            # if it's an async mode, gather ID's and use it in `after_update`
            # because only here we are able to compare current data with new
            context.setdefault("_resources_to_validate", [])

            if validation_requires:
                context['_resources_to_validate'].append(
                    updated_resource["id"])

    # CKAN < 2.10
    def after_update(self, context, data_dict):
        if (self._data_dict_is_dataset(data_dict)):
            return self.after_dataset_update(context, data_dict)
        else:
            return self.after_resource_update(context, data_dict)

    # CKAN >= 2.10
    def after_resource_update(self, context, data_dict):
        context.pop('_resource_validation', None)

        if context.pop('_validation_performed', None) \
                or data_dict.pop(u'_do_not_validate', False) \
                or data_dict.pop('_success_validation', False):
            return

        validation_possible = utils.is_resource_could_be_validated(
            context, data_dict)

        if not validation_possible:
            return

        if data_dict["id"] not in context.get('_resources_to_validate', []):
            return

        utils.validate_resource(context, data_dict)

        context.pop('_resources_to_validate', None)

    # CKAN < 2.10
    def before_delete(self, context, resource, resources):
        return self.before_resource_delete(context, resource, resources)

    # CKAN >= 2.10
    def before_resource_delete(self, context, resource, resources):
        context['_resource_validation'] = True

    # CKAN >= 2.10
    def after_dataset_create(self, context, data_dict):
        for resource in data_dict.get(u'resources', []):
            if utils.is_resource_could_be_validated(context, resource):
                utils.validate_resource(context, resource)

    # CKAN < 2.10
    # def after_update(self, context, data_dict):
    #     return self.after_dataset_update(context, data_dict)

    # CKAN >= 2.10
    def after_dataset_update(self, context, data_dict):
        if context.pop('_validation_performed', None) \
                or context.pop('_resource_validation', None):
            return

        for resource in data_dict.get('resources', []):
            if resource.pop(u'_do_not_validate', False) \
                    or resource.pop('_success_validation', False):
                continue

            if not utils.is_resource_could_be_validated(context, resource):
                continue

            utils.validate_resource(context, resource)

    def before_index(self, index_dict):
        if (self._data_dict_is_dataset(index_dict)):
            return self.before_dataset_index(index_dict)

    # CKAN >= 2.10
    def before_dataset_index(self, index_dict):

        res_status = []
        dataset_dict = json.loads(index_dict['validated_data_dict'])
        for resource in dataset_dict.get('resources', []):
            if resource.get('validation_status'):
                res_status.append(resource['validation_status'])

        if res_status:
            index_dict['vocab_validation_status'] = res_status

        return index_dict
