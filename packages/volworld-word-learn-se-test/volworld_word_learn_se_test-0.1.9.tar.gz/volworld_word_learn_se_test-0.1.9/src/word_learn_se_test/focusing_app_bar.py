
from behave import *
from selenium.webdriver.common.by import By
from volworld_common.test.behave.BehaveUtil import BehaveUtil

from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import (get_element_by_dom_id, click_element,
                                                                waiting_for_animation,
                                                                w__get_element_by_shown_dom_id, check_have_svg_icon)

from test.behave.PageGroup import PageGroup


def check_focusing_circles_and_slots_on_focusing_bar(c, focusing_circles: str, empty_slots: str):
    f_ch = int(BehaveUtil.clear_string(focusing_circles))
    slot = int(BehaveUtil.clear_string(empty_slots))
    app_bar = w__get_element_by_shown_dom_id(c, [A.AppBar, A.Focusing, A.Count])
    svg_list = app_bar.find_elements(by=By.CSS_SELECTOR, value=f"svg")
    # print('svg_list size = ', len(svg_list))
    focusing_count = 0
    empty_slot = 0
    for svg in svg_list:
        # print('svg size = ', svg.get_attribute('class'))
        if check_have_svg_icon(svg, [A.Filled, A.Circle]):
            focusing_count += 1
        if check_have_svg_icon(svg, [A.Empty, A.Circle]):
            empty_slot += 1
    assert focusing_count == f_ch, f"Expect focusing chapters = [{f_ch}] != [{focusing_count}]"
    assert empty_slot == slot, f"Expect empty slots = [{slot}] != [{empty_slot}]"


def remove_focusing_row_by_text(c, row_text: str):
    app_bar = get_element_by_dom_id(c, [A.AppBar, A.Focusing])
    click_element(c, app_bar)
    waiting_for_animation()
    drawer_main = w__get_element_by_shown_dom_id(c, [A.AppBar, A.Focusing, A.Drawer, A.Main])
    row_text = BehaveUtil.clear_string(row_text)
    row = drawer_main.find_element(by=By.XPATH, value=f".//*[text()='{row_text}']")
    assert row is not None
    remove_btn = row.find_element(by=By.XPATH, value=f"../../aside/button")
    # print("focus_btn innerHTML = ", focus_btn.get_attribute('innerHTML').strip())
    click_element(c, remove_btn)


# def get_list_root(c):
#     group = PageGroup.get_group(c)
#     ids = []
#     if group == PageGroup.Pg291_Book_Chapter_List_Page:
#         ids = [A.Chapter, A.List]
#     elif group == PageGroup.Pg154_Chapter_Word_List_Page:
#         ids = [A.Word, A.List]
#     assert len(ids) > 0, "Unknown Group"
#     return w__get_element_by_shown_dom_id(c, ids)


def click_row_to_add_focusing_item(c, row_text: str):
    list_root = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    row_text = BehaveUtil.clear_string(row_text)
    row = list_root.find_element(by=By.XPATH, value=f".//*[text()='{row_text}']")
    assert row is not None
    btns = row.find_elements(by=By.XPATH, value=f"../../aside/button")
    if len(btns) == 1:
        focus_btn = btns[0]  # for chapter ->  <a><button>
    else:
        focus_btn = btns[1]  # for word ->  <button><button>
    click_element(c, focus_btn)