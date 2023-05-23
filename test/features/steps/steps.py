from behave import step
from behaving.personas.steps import *  # noqa: F401, F403
from behaving.web.steps import *  # noqa: F401, F403
from behaving.web.steps.basic import should_see
from behaving.web.steps.url import when_i_visit_url


@step(u'I go to homepage')
def go_to_home(context):
    when_i_visit_url(context, '/')


@step(u'I should see text containing quotes `{text}`')
def should_see_backquoted(context, text):
    should_see(context, text)


@step(u'I log in')
def log_in(context):
    assert context.persona
    context.execute_steps(u"""
        When I go to homepage
        And I click the link with text that contains "Log in"
        And I log in directly
    """)


@step(u'I log in directly')
def log_in_directly(context):
    """
    This differs to the `log_in` function above by logging in directly to a page where the user login form is presented
    :param context:
    :return:
    """

    assert context.persona
    context.execute_steps(u"""
        When I attempt to log in with password "$password"
        Then I should see an element with xpath "//a[@title='Log out']"
    """)


@step(u'I attempt to log in with password "{password}"')
def attempt_login(context, password):
    assert context.persona
    context.execute_steps(u"""
        When I fill in "login" with "$name"
        And I fill in "password" with "{}"
        And I press the element with xpath "//button[contains(string(), 'Login')]"
    """.format(password))


@step(u'I open the new resource form for dataset "{name}"')
def go_to_new_resource_form(context, name):
    context.execute_steps(u"""
        When I edit the "{name}" dataset
        And I click the link with text that contains "Resources"
        And I click the link with text that contains "Add new resource"
    """.format(name=name))


@step(u'I create a resource with name "{name}" and URL "{url}"')
def add_resource(context, name, url):
    context.execute_steps(u"""
        When I log in
        And I open the new resource form for dataset "warandpeace"
        And I execute the script "$('#resource-edit [name=url]').val('{url}')"
        And I fill in "name" with "{name}"
        And I fill in "description" with "description"
        And I execute the script "document.getElementById('field-format').value='HTML'"
        And I press the element with xpath "//form[contains(@class, 'resource-form')]//button[contains(@class, 'btn-primary')]"
    """.format(name=name, url=url))


@step(u'I go to dataset page')
def go_to_dataset_page(context):
    when_i_visit_url(context, '/dataset')


@step(u'I go to dataset "{name}"')
def go_to_dataset(context, name):
    when_i_visit_url(context, '/dataset/' + name)


@step(u'I edit the "{name}" dataset')
def edit_dataset(context, name):
    context.execute_steps(u"""
        When I go to dataset "{name}"
        And I click the link with text that contains "Manage"
    """.format(name=name))


@step(u'I go to organisation page')
def go_to_organisation_page(context):
    when_i_visit_url(context, '/organization')


@step(u'I go to register page')
def go_to_register_page(context):
    when_i_visit_url(context, '/user/register')


@step(u'I search the autocomplete API for user "{username}"')
def go_to_user_autocomplete(context, username):
    when_i_visit_url(context, '/api/2/util/user/autocomplete?q={}'.format(username))


@step(u'I go to the user list API')
def go_to_user_list(context):
    when_i_visit_url(context, '/api/3/action/user_list')


@step(u'I go to the "{user_id}" profile page')
def go_to_user_profile(context, user_id):
    when_i_visit_url(context, '/user/{}'.format(user_id))


@step(u'I go to the dashboard')
def go_to_dashboard(context):
    context.execute_steps(u"""
        When I visit "/dashboard/datasets"
    """)


@step(u'I should see my datasets')
def dashboard_datasets(context):
    context.execute_steps(u"""
        Then I should see an element with xpath "//li[contains(@class, 'active') and contains(string(), 'My Datasets')]"
    """)


@step(u'I go to the "{user_id}" user API')
def go_to_user_show(context, user_id):
    when_i_visit_url(context, '/api/3/action/user_show?id={}'.format(user_id))


@step(u'I view the "{group_id}" group API "{including}" users')
def go_to_group_including_users(context, group_id, including):
    when_i_visit_url(
        context, r'/api/3/action/group_show?id={}&include_users={}'.format(
            group_id, including in ['with', 'including']))


@step(u'I view the "{organisation_id}" organisation API "{including}" users')
def go_to_organisation_including_users(context, organisation_id, including):
    when_i_visit_url(
        context, r'/api/3/action/organization_show?id={}&include_users={}'.format(
            organisation_id, including in ['with', 'including']))


# ckanext-validation


@step(u'I should see a validation timestamp')
def should_see_validation_timestamp(context):
    context.execute_steps(u"""
        Then I should see "Validation timestamp"
        And I should see an element with xpath "//th[contains(string(), 'Validation timestamp')]/../td[contains(string(), '-') and contains(string(), ':') and contains(string(), '.')]"
    """)
