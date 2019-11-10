from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest


class LayoutAndStylingTest(FunctionalTest):
    def test_layout_and_styling(self):
        def ensure_input_box_centered():
            center_of_input_box = input_box.location['x'] + \
                input_box.size['width'] / 2
            self.assertAlmostEqual(center_of_input_box, 512, delta=10)

        # Edith goes to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centered
        input_box = self.get_item_input_box()
        ensure_input_box_centered()

        # She starts a new list and sees the input is nicely
        # centered there too
        input_box.send_keys('testing')
        input_box.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: testing')
        input_box = self.get_item_input_box()
        ensure_input_box_centered()
