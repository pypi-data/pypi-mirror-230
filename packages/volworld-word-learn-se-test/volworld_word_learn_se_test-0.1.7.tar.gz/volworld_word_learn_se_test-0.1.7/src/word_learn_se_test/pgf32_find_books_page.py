import base64

import pyperclip
from behave import *
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from volworld_aws_api_common.test.behave.row_utils import w__get_row_container
from volworld_word_book_library_se_test.nav_utils import open_more_actions_drawer_from_bottom_app_bar

from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, \
    w__assert_element_not_existing, w__click_element_by_dom_id, click_element, get_element_by_dom_id
from volworld_aws_api_common.test.behave.drawer_utils import click_to_close_list_nav_drawer
from volworld_common.test.behave.BehaveUtil import BehaveUtil

from src.word_learn_se_test.row_util import get_info_row_button_by_svg_name, get_info_row_link_by_svg_name


@when('{learner} find books by title keywords [{titles}] and mentor names [{mentors}]')
def when__find_books_by_title_keywords_and_mentor_names(c, learner: str, titles: str, mentors: str):
    search_btn = get_element_by_dom_id(c, [A.Search, A.Search])
    if search_btn is None:
        w__click_element_by_dom_id(c, [A.Search, A.Open])
    search_btn = w__get_element_by_shown_dom_id(c, [A.Search, A.Search])
    titles = BehaveUtil.clear_string(titles)
    mentors = BehaveUtil.clear_string(mentors)
    search = titles
    for m in mentors.split(' '):
        search += f" mentor:{m.strip()}"
    pyperclip.copy(search)
    input_elm = w__get_element_by_shown_dom_id(c, [A.Search, A.Text])
    input_elm.click()
    input_elm.send_keys(Keys.CONTROL, 'a')
    input_elm.send_keys(Keys.DELETE)
    input_elm.send_keys(Keys.CONTROL, 'v')

    click_element(c, search_btn)


@then('title keywords [{titles}] and mentor names [{mentors}] is shown in the input field of search area')
def then__title_keywords_titles_and_mentor_names_mentors_is_shown_in_the_input_field_of_search_area(
        c, titles: str, mentors: str):
    titles = BehaveUtil.clear_string(titles)
    mentors = BehaveUtil.clear_string(mentors)
    search = titles
    for m in mentors.split(' '):
        search += f" mentor:{m.strip()}"
    pyperclip.copy(search)
    input_elm = w__get_element_by_shown_dom_id(c, [A.Search, A.Text])
    input = input_elm.get_attribute("value")
    print(f"input value = {input}")

    assert input == search, search


@then('the url of target page shows title keywords [{titles}] and mentor names [{mentors}]')
def then__the_url_of_target_page_shows_title_keywords_titles_and_mentor_names_mentors(
        c, titles: str, mentors: str):
    titles = BehaveUtil.clear_string(titles)
    mentors = BehaveUtil.clear_string(mentors)
    search_list = []
    for t in titles.split(' '):
        search_list.append(t.strip())
    for m in mentors.split(' '):
        search_list.append(f"mentor:{m.strip()}")
    # print(f"search_list = {search_list}")

    url: str = c.browser.current_url
    # print(f"url = {url}")
    sch = url.split("sch=")[1].split("&")[0]
    elms = sch.split("%")
    for elm in elms:
        # print(f"elm = {elm}")
        elm = base64.b64decode(elm + "==").decode('utf-8')
        # print(f"decoded elm = {elm}")
        assert elm in search_list, elm


@when('{learner} click on collect button of first book row')
def when__click_on_collect_button_of_first_book_row(c, learner: str):
    svg_class_name = "SvgIcon-to-clt-b"
    btn = get_info_row_button_by_svg_name(c, 0, svg_class_name)
    assert btn is not None
    click_element(c, btn)


@then('there is no collected button in first book row')
def then__there_is_no_collected_button_in_first_book_row(c):
    svg_class_name = "SvgIcon-to-clt-b"
    btn = get_info_row_button_by_svg_name(c, 0, svg_class_name)
    assert btn is None


@then('there is an open collected book link in first book row')
def then__there_is_a_open_collected_book_button_in_first_book_row(c):
    svg_class_name = "SvgIcon-opn-cltd-b"
    btn = get_info_row_link_by_svg_name(c, 0, svg_class_name)
    assert btn is not None


@then('there is an open non-collected book link in first book row')
def then__there_is_a_open_collected_book_button_in_first_book_row(c):
    svg_class_name = "SvgIcon-opn-b"
    btn = get_info_row_link_by_svg_name(c, 0, svg_class_name)
    assert btn is not None


@when('{learner} click open non-collected book link')
def when__click_open_non_collected_book_link(c, learner: str):
    svg_class_name = "SvgIcon-opn-b"
    btn = get_info_row_link_by_svg_name(c, 0, svg_class_name)
    click_element(c, btn)


@when('{learner} click open collected book link')
def when__click_open_collected_book_link(c, learner: str):
    svg_class_name = "SvgIcon-opn-cltd-b"
    btn = get_info_row_link_by_svg_name(c, 0, svg_class_name)
    click_element(c, btn)


def get_title_image_svg_by_class_name(c, svg_class_name):
    image = w__get_element_by_shown_dom_id(c, [A.Title, A.Image])
    svg_list = image.find_elements(By.XPATH, f"./*[name()='svg' and contains(@class, '{svg_class_name}')]")
    return svg_list


@then('there is a non-collected book icon on header image')
def then__there_is_a_non_collected_book_icon_on_header_image(c):
    svg_list = get_title_image_svg_by_class_name(c, "SvgIcon-b")
    assert len(svg_list) == 1


@then('there is a collected book icon on header image')
def then__there_is_a_collected_book_icon_on_header_image(c):
    svg_list = get_title_image_svg_by_class_name(c, "SvgIcon-cltd-b")
    assert len(svg_list) == 1


@when('{user} click back button on browser')
def when__click_back_button_on_browser(c, user: str):
    c.browser.back()