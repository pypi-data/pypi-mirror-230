from selenium.webdriver.common.by import By
from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id


def get_info_row_element_by_svg_name(c, row_index: int, elm_tag: str, svg_class_name: str):
    row_container = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    assert row_container is not None
    rows = row_container.find_elements(By.XPATH, "./div/main/aside")
    collect_btn_lst = rows[row_index].find_elements(By.XPATH, f"./{elm_tag}")
    print(f"found [{len(collect_btn_lst)}] {row_container}")
    for btn in collect_btn_lst:
        svg_lst = btn.find_elements(By.XPATH, f"./*[name()='svg' and contains(@class, '{svg_class_name}')]")
        if len(svg_lst) > 0:
            assert len(svg_lst) == 1
            return btn
    return None


def get_info_row_button_by_svg_name(c, row_index: int, svg_class_name: str):
    return get_info_row_element_by_svg_name(c, row_index, 'button', svg_class_name)
    # elm = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    # assert elm is not None
    # rows = elm.find_elements(By.XPATH, "./div/main/aside")
    # collect_btn_lst = rows[row_index].find_elements(By.XPATH, "./button")
    # print(f"found [{len(collect_btn_lst)}] buttons")
    # for btn in collect_btn_lst:
    #     svg_lst = btn.find_elements(By.XPATH, f"./*[name()='svg' and contains(@class, '{svg_class_name}')]")
    #     if len(svg_lst) > 0:
    #         assert len(svg_lst) == 1
    #         return btn
    # return None

def get_info_row_link_by_svg_name(c, row_index: int, svg_class_name: str):
    return get_info_row_element_by_svg_name(c, row_index, 'a', svg_class_name)