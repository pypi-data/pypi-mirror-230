from behave import *
from selenium.webdriver.common.by import By
from volworld_aws_api_common.test.behave.row_utils import w__get_row_container
from volworld_word_book_library_se_test.nav_utils import open_more_actions_drawer_from_bottom_app_bar

from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, \
    w__assert_element_not_existing, w__click_element_by_dom_id, click_element, get_element_by_dom_id
from volworld_aws_api_common.test.behave.drawer_utils import click_to_close_list_nav_drawer


@when('{learner} disable [show tag] switch in [more actions drawer]')
def when__disable_show_tag_switch_in_more_actions_drawer(c, learner: str):
    open_more_actions_drawer_from_bottom_app_bar(c)
    # @note input might NOT support EC.visibility_of_element_located()?
    elm = get_element_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Tag, A.Switch])
    assert elm.get_attribute("checked") is not None
    click_element(c, elm)


@when('{learner} enable [show tag] switch in [more actions drawer]')
def when__enable_show_tag_switch_in_more_actions_drawer(c, learner: str):
    open_more_actions_drawer_from_bottom_app_bar(c)
    # @note input might NOT support EC.visibility_of_element_located()?
    elm = get_element_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Tag, A.Switch])
    assert elm.get_attribute("checked") is None
    click_element(c, elm)


@then('the tags of list items is not showing')
def then__the_tags_of_list_items_is_not_showing(c):
    list_root = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    items = list_root.find_elements(By.XPATH, "./div/main/nav")
    assert len(items) == 0


@then('the tags of list items is showing')
def then__the_tags_of_list_items_is_showing(c):
    list_root = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    items = list_root.find_elements(By.XPATH, "./div/main/nav")
    assert len(items) > 0