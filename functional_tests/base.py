from functools import wraps
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from .management.commands.create_session import create_pre_authenticated_session
from .server_tools import create_session_on_server, reset_database
from django.conf import settings
import time
import os
from datetime import datetime

MAX_WAIT = 10
SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'screendumps'
)


def wait(assertion_fn):
    @wraps(assertion_fn)
    def decorated(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return assertion_fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time >= MAX_WAIT:
                    raise e
                time.sleep(0.1)

    return decorated


class _Pages:
    def __init__(self, test):
        self.list = ListPage(test)
        self.home = HomePage(test)
        self.my_lists = MyListsPage(test)


class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.staging_server = os.environ.get('STAGING_SERVER')
        if self.staging_server:
            self.live_server_url = 'http://' + self.staging_server
            reset_database(self.staging_server)

        self.pages = _Pages(self)

    def tearDown(self):
        if self._test_has_failed():
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.browser.window_handles):
                self._windowid = ix
                self.browser.switch_to_window(handle)
                self.take_screenshot()
                self.dump_html()
        self.browser.quit()
        super().tearDown()

    def _test_has_failed(self):
        # Slightly obscure but Harry P. couldn't find a better way
        return any(error for (method, error) in self._outcome.errors)

    def take_screenshot(self):
        filename = self._get_filename() + '.png'
        print(f'Dumping screenshot to {filename}')
        self.browser.get_screenshot_as_file(filename)

    def dump_html(self):
        filename = self._get_filename() + '.html'
        print(f'Dumping HTML to {filename}')
        with open(filename, 'w') as f:
            f.write(self.browser.page_source)

    def _get_filename(self):
        timestamp = datetime.now().isoformat().replace(':', '.')[:19]
        return '{folder}/{class_name}.{method}-window{window_id}-{timestamp}'.format(
            folder=SCREEN_DUMP_LOCATION,
            class_name=self.__class__.__name__,
            method=self._testMethodName,
            window_id=self._windowid,
            timestamp=timestamp
        )

    def get_item_input_box(self):
        return self.browser.find_element_by_id('id_text')

    @wait
    def wait_for(self, assertion_fn):
        return assertion_fn()

    @wait
    def wait_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    @wait
    def wait_to_be_logged_in(self, email):
        self.browser.find_element_by_link_text('Log out')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(email, navbar.text)

    @wait
    def wait_to_be_logged_out(self, email):
        self.browser.find_element_by_name('email')
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertNotIn(email, navbar.text)

    @wait
    def wait_for_404_page(self):
        self.assertEqual(
            self.browser.find_element_by_css_selector('.jumbotron h1').text,
            'Page not found'
        )

    @wait
    def wait_for_link(self, link_text):
        self.browser.find_element_by_link_text(link_text)

    def add_list_item(self, item_text):
        num_rows = len(
            self.browser.find_elements_by_css_selector('#id_list_table tr')
        )
        self.get_item_input_box().send_keys(item_text)
        self.get_item_input_box().send_keys(Keys.ENTER)
        item_number = num_rows + 1
        self.wait_for_row_in_list_table(f'{item_number}: {item_text}')

    def get_path(self, path):
        return self.browser.get(self.live_server_url + path)

    def init_pre_authenticated_session(self, email):
        if self.staging_server:
            session_key = create_session_on_server(self.staging_server, email)
        else:
            session_key = create_pre_authenticated_session(email)

        # # To set a cookie we need to first visit the domain
        # # 404 pages load the quickest!
        self.browser.get(self.live_server_url + '/404_no_such_url/')
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/',
        ))


class BasePage:
    def __init__(self, test):
        self.test = test

    @wait
    def wait_for_h1(self, h1_text):
        self.test.assertEqual(
            self.test.browser.find_element_by_tag_name('h1').text,
            h1_text
        )

    @wait
    def wait_for_link(self, link_text):
        self.browser.find_element_by_link_text(link_text)

    def click_link(self, link_text):
        self.test.browser.find_element_by_link_text(
            link_text
        ).click()
        return self


class BaseListPage(BasePage):
    def get_item_input_box(self):
        return self.test.browser.find_element_by_id('id_text')

    def get_table_rows(self):
        return self.test.browser.find_elements_by_css_selector('#id_list_table tr')

    @wait
    def wait_for_row_in_list_table(self, item_text, item_number):
        expected_row_text = f'{item_number}: {item_text}'
        rows = self.get_table_rows()
        self.test.assertIn(expected_row_text, [row.text for row in rows])

    def add_list_item(self, item_text):
        new_item_number = len(self.get_table_rows()) + 1
        self.get_item_input_box().send_keys(item_text)
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table(item_text, new_item_number)
        return self


class HomePage(BaseListPage):
    def go(self):
        self.test.browser.get(self.test.live_server_url)
        self.wait_for_h1('Start a new To-Do list')
        return self

    def create_new_list(self, first_item_text):
        return self.add_list_item(first_item_text)


class ListPage(BaseListPage):
    def get_share_box(self):
        return self.test.browser.find_element_by_css_selector(
            'input[name="sharee"]'
        )

    def get_shared_with_list(self):
        return self.test.browser.find_elements_by_css_selector(
            '.list-sharee'
        )

    def share_list_with(self, email):
        self.get_share_box().send_keys(email)
        self.get_share_box().send_keys(Keys.ENTER)
        self.test.wait_for(lambda: self.test.assertIn(
            email,
            [item.text for item in self.get_shared_with_list()]
        ))

    def get_list_owner(self):
        return self.test.browser.find_element_by_id('id_list_owner').text


class MyListsPage(BasePage):
    def go(self):
        self.test.browser.get(self.test.live_server_url)
        self.wait_for_h1('Start a new To-Do list')
        self.click_link('My lists')
        self.wait_for_h1('My Lists')
        return self
