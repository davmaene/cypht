#!/usr/bin/python

from base import WebTest, USER, PASS
from selenium.webdriver.common.by import By
from runner import test_runner
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

class FolderListTests(WebTest):

    def __init__(self):
        WebTest.__init__(self)
        self.login(USER, PASS)
        self.wait_with_folder_list()
        self.load()

    def reload_folder_list(self):
        main_menu = self.by_class('main')
        assert main_menu.is_displayed()
        self.by_class('update_message_list').click()
        self.safari_workaround(3)
        # update_message_list triggers site reload, so we explicitly wait for element to become stale
        WebDriverWait(self.driver, 20).until(EC.staleness_of(main_menu))
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
        # And once it is stale, we can now wait for it to become available again as the page contents are loaded again.
        main_menu = WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'main'))
        )
        main_menu = self.by_class('main')
        #and finally perform our test on the actual, refreshed element.
        assert main_menu.is_displayed()

    def expand_section(self):
        self.load()
        self.wait_with_folder_list()
        self.by_css('[data-bs-target=".settings"]').click()
        folder_list = self.by_class('folder_list')
        list_item = folder_list.find_element(By.CLASS_NAME, 'menu_save')
        link = list_item.find_element(By.TAG_NAME, 'a')
        self.driver.execute_script("""
            const container = arguments[0];
            const item = arguments[1];
            container.scrollTop = item.offsetTop - container.offsetTop;
        """, folder_list, list_item)
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(link))
        link.click()
        self.wait_with_folder_list()
        self.wait_for_navigation_to_complete()
        assert self.by_class('content_title').text == 'Save Settings'

    def collapse_section(self):
        section = self.by_css('.settings.folders.collapse')
        expanded_class = section.get_attribute('class')
        assert 'show' in expanded_class
        self.load()
        section = self.by_css('.settings.folders.collapse')
        collapsed_class = section.get_attribute('class')
        assert 'show' not in collapsed_class

    def hide_folders(self):
        self.driver.execute_script("window.scrollBy(0, 1000);")
        self.wait(By.CLASS_NAME, 'menu-toggle')
        # Use JavaScript to click the element
        hide_button = self.by_class('menu-toggle')
        self.driver.execute_script("arguments[0].click();", hide_button)
        list_item = self.by_class('menu_home')
        assert list_item.is_displayed() == False

    def show_folders(self):
        self.wait(By.CLASS_NAME, 'menu-toggle')
        folder_toggle = self.by_class('menu-toggle')
        self.driver.execute_script("arguments[0].click();", folder_toggle)
        self.load()
        if not self.element_exists('content_title') or self.by_class('content_title').text != 'Home':
            self.wait_for_navigation_to_complete()
        assert self.by_class('content_title').text == 'Home'
        self.load()


if __name__ == '__main__':

    print("FOLDER LIST TESTS")
    test_runner(FolderListTests, [
        'reload_folder_list',
        # 'expand_section',
        # 'collapse_section',
        'hide_folders',
        'show_folders',
        'logout'
    ])
