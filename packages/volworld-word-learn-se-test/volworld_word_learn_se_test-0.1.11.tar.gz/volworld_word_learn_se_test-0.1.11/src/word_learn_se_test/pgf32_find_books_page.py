import base64

import pyperclip
from behave import *
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from volworld_aws_api_common.api.enum.ProjectModeType import ProjectModeType

from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, \
    w__click_element_by_dom_id, click_element, get_element_by_dom_id
from volworld_common.test.behave.BehaveUtil import BehaveUtil

from test.behave.CotA import CotA
from test.behave.Page import Page
from volworld_aws_api_common.test.behave.row_utils import get_info_row_button_by_svg_name, get_info_row_link_by_svg_name
from volworld_aws_api_common.api.FrontEndUrl import FrontEndUrl
from volworld_aws_api_common.test.ProjectMode import ProjectMode


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


@when('{mentor} open target page with search title keywords [{keywords}], mentor names [{mentors}], and item per page is {item_per_page_str}')
def when__open_page_with_keywords_and_item_per_page(c, mentor: str, keywords: str, mentors:str, item_per_page_str: str):
    target_page = getattr(c, CotA.TargetPage)
    ks = BehaveUtil.clear_string(keywords).split(" ")
    kwb64 = list()
    for k in ks:
        kwb64.append(base64.b64encode(bytes(k, "utf-8")).decode('utf-8'))
    ms = BehaveUtil.clear_string(mentors).split(" ")
    for m in ms:
        kwb64.append(base64.b64encode(bytes(f"mentor:{m}", "utf-8")).decode('utf-8'))
    sch = '%'.join(kwb64)
    print(f'sch = [{sch}]')

    url_base = None
    if target_page == Page.PgF32_Find_Books_Page:
        test_url_prefix = ''
        if ProjectMode.type == ProjectModeType.Combined:
            test_url_prefix = f'{A.WordLearn}/'
        url_base = f"{FrontEndUrl.Root}/#/{test_url_prefix}{A.Search}/{A.Book}"

    assert url_base is not None
    url = f"{url_base}?sch={sch}&impp={BehaveUtil.clear_int(item_per_page_str)}"

    print(f"open default [{target_page}] url={url}")
    c.browser.get(url)