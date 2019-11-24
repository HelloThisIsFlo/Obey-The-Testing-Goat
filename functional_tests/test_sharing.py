from selenium import webdriver
from .base import FunctionalTest


def quit_if_possible(browser):
    try:
        browser.quit()
    except:
        pass


class SharingTest(FunctionalTest):
    def test_can_share_a_list_with_another_user(self):
        # Edith is a logged-in user
        self.init_pre_authenticated_session('edith@example.com')
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))

        # Her friend Oniciferous is also hanging out on the lists site
        oni_browser = webdriver.Firefox()
        self.addCleanup(lambda: quit_if_possible(oni_browser))
        self.browser = oni_browser
        self.init_pre_authenticated_session('oniciferous@example.com')

        # Edith goes to the home page and starts a list
        self.browser = edith_browser
        self.pages.home\
            .go()\
            .add_list_item('Get help')

        # She notices a 'Share this list' option
        share_box = self.pages.list.get_share_box()
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your-friend@example.com'
        )

        # She shares her list
        # The page updates to say that it's shared with Oniciferous
        self.pages.list.share_list_with('oniciferous@example.com')

        # Oniciferous now goes to the lists pag with his browser
        # He sees Edith's list in there!
        self.browser = oni_browser
        self.pages.my_lists\
            .go()\
            .wait_for_link('Get help')\
            .click_link('Get help')

        # On the list page, Oniciferous can see it says it's Edith's list
        self.wait_for(lambda: self.assertEqual(
            self.pages.list.get_list_owner(),
            'edith@example.com'
        ))

        # He adds an item to the list
        self.pages.list.add_list_item('Hi Edith!')

        # When Edith refreshes the page, she sees Oniciferous's addition
        self.browser = edith_browser
        self.browser.refresh()
        self.pages.list.wait_for_row_in_list_table('Hi Edith!', 2)
