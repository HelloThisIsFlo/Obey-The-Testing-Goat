from .base import FunctionalTest
from django.contrib import auth
from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
User = auth.get_user_model()


class MyListsTest(FunctionalTest):
    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        # Edith is a logged-in user
        self.init_pre_authenticated_session('edith@example.com')

        # She goes to the home page and starts a list
        self.browser.get(self.live_server_url)
        self.add_list_item('Reticulate splines')
        self.add_list_item('Immanentize eschaton')
        first_list_url = self.browser.current_url

        # She notices a 'My lists' link, for the first time.
        self.browser.find_element_by_link_text('My lists').click()

        # She sees that her list is in there, named according to its
        # first list item
        self.wait_for_link('Reticulate splines')
        self.browser.find_element_by_link_text('Reticulate splines').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )

        # She decides to start anohter list, just to see
        self.browser.get(self.live_server_url)
        self.add_list_item('Click cows')
        second_list_url = self.browser.current_url

        # Under 'My lists', hew new list appears
        self.browser.find_element_by_link_text('My lists').click()
        self.wait_for_link('Click cows')
        self.browser.find_element_by_link_text('Click cows').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, second_list_url)
        )

        # She logs out. The 'My lists' option disappears
        self.browser.find_element_by_link_text('Log out').click()
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_elements_by_link_text('My lists'),
            []
        ))

    def test_only_logged_in_users_can_access_their_lists(self):
        # Edith is logged in and creates 2 lists, then logs out
        self.init_pre_authenticated_session('edith@example.com')
        self.browser.get(self.live_server_url)
        self.add_list_item('Reticulate splines')
        self.add_list_item('Immanentize eschaton')
        ediths_list_1_url = self.browser.current_url
        self.browser.get(self.live_server_url)
        self.add_list_item('Click cows')
        self.add_list_item('Align Covariance Matrices')
        self.browser.find_element_by_link_text('Log out').click()
        self.wait_to_be_logged_out(email='edit@example.com')

        # Frank is logged in and creates 2 lists, then logs out
        self.init_pre_authenticated_session('frank@example.com')
        self.browser.get(self.live_server_url)
        self.add_list_item('Normalize Power')
        self.add_list_item('Attempt to Lock Back-Buffer')
        franks_list_1_url = self.browser.current_url
        self.browser.get(self.live_server_url)
        self.add_list_item('Collect Meteor Particles')
        self.add_list_item('Model Object Components')
        self.browser.find_element_by_link_text('Log out').click()
        self.wait_to_be_logged_out(email='frank@example.com')

        # Edith, logged out for now, tries to access Edith's lists
        # She is presented with a 404 page
        self.get_path('/lists/users/edith@example.com/')
        self.wait_for_404_page()

        # Edith, logged out for now, tries to a speficic list from Edith's
        # She is presented with a 404 page
        self.browser.get(ediths_list_1_url)
        self.wait_for_404_page()

        # Edith logs in
        # She can now access her lists
        self.init_pre_authenticated_session('edith@example.com')
        self.get_path('/lists/users/edith@example.com/')
        self.wait_for_link('Reticulate splines')
        self.wait_for_link('Click cows')

        # Edith, logged in, tries to access Frank's lists
        # She is presented with a 404 page
        self.get_path('/lists/users/frank@example.com/')
        self.wait_for_404_page()

        # Edith, logged in, tries to access one of Frank's lists
        # She is presented with a 404 page
        self.browser.get(franks_list_1_url)
        self.wait_for_404_page()

        # Edith, logged in, can access her own lists
        # She is presented with a 404 page
        self.browser.get(ediths_list_1_url)
        self.wait_for_row_in_list_table('1: Reticulate splines')
