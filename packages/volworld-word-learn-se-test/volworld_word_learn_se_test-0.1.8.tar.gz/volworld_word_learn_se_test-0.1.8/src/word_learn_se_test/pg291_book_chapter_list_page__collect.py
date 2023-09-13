from behave import *
from selenium.webdriver.common.by import By
from volworld_aws_api_common.test.behave.row_utils import w__get_row_container
from volworld_word_book_library_se_test.nav_utils import open_more_actions_drawer_from_bottom_app_bar

from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, \
    w__assert_element_not_existing, w__click_element_by_dom_id
from volworld_aws_api_common.test.behave.drawer_utils import click_to_close_list_nav_drawer


@then('[collect book button] in [bottom app bar] is enabled')
def then__collect_book_button_in_bottom_app_bar_is_enabled(c):
    dom_id = [A.BottomAppBar, A.Collect, A.Book, A.Button]
    btn = w__get_element_by_shown_dom_id(c, dom_id)
    assert btn is not None


@then('[collect book button] in [more actions drawer] is enabled')
def then__collect_book_button_in_more_actions_drawer_is_enabled(c):
    open_more_actions_drawer_from_bottom_app_bar(c)
    dom_id = [A.MoreActions, A.Drawer, A.Collect, A.Book, A.Button]
    btn = w__get_element_by_shown_dom_id(c, dom_id)
    assert btn is not None
    click_to_close_list_nav_drawer(c, A.MoreActions)


@then('[collect book button] in [bottom app bar] is not showing')
def then__collect_book_button_in_bottom_app_bar_is_not_showing(c):
    dom_id = [A.BottomAppBar, A.Collect, A.Book, A.Button]
    w__assert_element_not_existing(c, dom_id)


@then('[collect book button] in [more actions drawer] is not showing')
def then__collect_book_button_in_more_actions_drawer_is_not_showing(c):
    open_more_actions_drawer_from_bottom_app_bar(c)
    dom_id = [A.MoreActions, A.Drawer, A.Collect, A.Book, A.Button]
    w__assert_element_not_existing(c, dom_id)
    click_to_close_list_nav_drawer(c, A.MoreActions)


@then('[focus button] on each chapter row is not showing')
def then__focus_button_on_each_chapter_row_is_not_showing(c):
    elm = w__get_row_container(c)
    assert elm is not None
    asides = elm.find_elements(By.XPATH, "./div/main/aside")
    for aside in asides:
        a = aside.find_elements(By.XPATH, "./a")
        assert len(a) == 1


@when('{learner} click [collect book button] in [bottom app bar]')
def when__click_collect_book_button_in_bottom_app_bar(c, learner: str):
    w__click_element_by_dom_id(c, [A.BottomAppBar, A.Collect, A.Book, A.Button])


@when('{learner} click [collect book button] in [more actions drawer]')
def when__click_collect_book_button_in_more_actions_drawer(c, learner: str):
    open_more_actions_drawer_from_bottom_app_bar(c)
    dom_id = [A.MoreActions, A.Drawer, A.Collect, A.Book, A.Button]
    w__click_element_by_dom_id(c, dom_id)
    click_to_close_list_nav_drawer(c, A.MoreActions)
