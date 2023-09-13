from behave import *

from .focusing_app_bar import check_focusing_circles_and_slots_on_focusing_bar


@then('{focusing_ch} focusing Chapters and {empty_slots} empty slots shown on focusing bar')
def then__focusing_chapters_and_empty_slots_empty_slots_shown_on_focusing_bar(c, focusing_ch: str, empty_slots: str):
    check_focusing_circles_and_slots_on_focusing_bar(c, focusing_ch, empty_slots)

