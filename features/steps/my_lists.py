from behave import given, when, then
from functional_tests.management.commands.create_session import \
    create_pre_authenticated_session
from functional_tests.base import wait
from django.conf import settings
from selenium.webdriver.common.keys import Keys


@given(u'I am a logged-in user')
def step_impl(context):
    session_key = create_pre_authenticated_session('edith@example.com')

    # # To set a cookie we need to first visit the domain
    # # 404 pages load the quickest!
    context.browser.get(context.get_url('/404_no_such_url/'))
    context.browser.add_cookie(dict(
        name=settings.SESSION_COOKIE_NAME,
        value=session_key,
        path='/',
    ))


@wait
def wait_for_list_item(context, item_text):
    context.test.assertIn(
        item_text,
        context.browser.find_element_by_css_selector('#id_list_table').text
    )


@when(u'I create a list with first item "{first_item_text}"')
def step_impl(context, first_item_text):
    context.browser.get(context.get_url('/'))
    context.browser.find_element_by_id('id_text').send_keys(first_item_text)
    context.browser.find_element_by_id('id_text').send_keys(Keys.ENTER)
    wait_for_list_item(context, first_item_text)


@when(u'I add an item "{item_text}"')
def step_impl(context, item_text):
    context.browser.find_element_by_id('id_text').send_keys(item_text)
    context.browser.find_element_by_id('id_text').send_keys(Keys.ENTER)
    wait_for_list_item(context, item_text)


@then(u'I will see a link to "{link_text}"')
@wait
def step_impl(context, link_text):
    context.browser.find_element_by_link_text(link_text)


@when(u'I click the link to "{link_text}"')
def step_impl(context, link_text):
    context.browser.find_element_by_link_text(link_text).click()

@then(u'I will be on the "{first_item_text}" list page')
@wait
def step_impl(context, first_item_text):
    first_row = context.browser.find_element_by_css_selector(
        '#id_list_table tr:first-child'
    )
    expected_row_text = '1: ' + first_item_text
    context.test.assertEqual(first_row.text, expected_row_text)
