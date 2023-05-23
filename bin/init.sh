#!/usr/bin/env sh
##
# Initialise CKAN data for testing.
#
set -e

. ${APP_DIR}/bin/activate
CLICK_ARGS="--yes" ckan_cli db clean
ckan_cli db init
ckan_cli db upgrade

# Initialise validation tables
PASTER_PLUGIN=ckanext-validation ckan_cli validation init-db

# Create some base test data
. $APP_DIR/bin/create-test-data.sh
