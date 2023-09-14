from behave import *

from features.steps.project_specific_steps import dialog_ids
from .nav_utils import open_more_actions_drawer_from_bottom_app_bar

from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, \
    click_element, scroll_to_bottom, w__assert_element_existing, w__assert_element_not_existing, \
    w__click_element_by_dom_id, click_element_by_dom_id
from selenium.webdriver.common.by import By
from volworld_common.test.behave.BehaveUtil import BehaveUtil


def check_word_count_in_32e_page(c, words):
    if BehaveUtil.clear_int(words) == 0:
        empty_list_container = w__get_element_by_shown_dom_id(c, [A.Empty, A.InfoRow, A.List])
        assert empty_list_container is not None
        return

    list_container = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    word_rows = list_container.find_elements(By.XPATH, "./div")
    assert len(word_rows) == BehaveUtil.clear_int(words)


def check_unknown_word_count_in_32e_page(c, words):
    list_container = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    btns = list_container.find_elements(By.XPATH, "./div/main/aside/button[1]")
    class_name = f"SvgIcon-{'-'.join([A.Not, A.Find])}"
    unknown_btn_count = 0
    for btn in btns:
        if btn.get_attribute('innerHTML').strip().find(class_name) > -1:
            unknown_btn_count += 1
    assert unknown_btn_count == BehaveUtil.clear_int(words)


@then('there are "{words}" words in word list')
def then__words_in_word_list(c, words: str):
    check_word_count_in_32e_page(c, words)


@then('there are "{words}" unknown words in word list')
def then__unknown_words_in_word_list(c, words: str):
    check_unknown_word_count_in_32e_page(c, words)


@then('[save button] in [bottom app bar] is "{active}"')
def then__check_save_chapter_btn(c, active: str):
    btn = w__get_element_by_shown_dom_id(c, [A.BottomAppBar, A.Save, A.Button])
    assert btn is not None
    enabled = BehaveUtil.clear_string(active).lower() == 'enabled'
    assert btn.is_enabled() == enabled


def load_word_text_list(c) -> list:
    elm = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    assert elm is not None
    rows = elm.find_elements(By.XPATH, "./div/main/main/span")
    row_text_list = []
    for r in rows:
        row_text_list.append(r.get_attribute('innerHTML').strip())
        # print(r.get_attribute('innerHTML').strip())
    return row_text_list


def load_drawer_tag_info_list(c) -> list:
    elm = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    assert elm is not None
    rows = elm.find_elements(By.XPATH, "./div/main/nav/main/b")
    row_text_list = []
    for r in rows:
        row_text_list.append(r.get_attribute('innerHTML').strip())
        print(r.get_attribute('innerHTML').strip())
    return row_text_list


@then('the word list is sort by {sort_type} in {dir_type} order')
def then__the_word_list_is_sort_by(c, sort_type: str, dir_type: str):
    dir_type = BehaveUtil.clear_string(dir_type).lower()
    sort_type = BehaveUtil.clear_string(sort_type).lower()
    row_bool_title_list = load_word_text_list(c)
    sort_text = row_bool_title_list.copy()
    row_tag_list = load_drawer_tag_info_list(c)
    row_tag_list = list(map(int, row_tag_list))
    sort_tag = row_tag_list.copy()
    assert_tag = True
    if sort_type == 'title' or sort_type == 'alphabetical':
        sort_text.sort()
        assert_tag = False
    else:
        sort_tag.sort()

    if dir_type == 'descending':
        sort_text.reverse()
        sort_tag.reverse()

    if assert_tag:
        for i in range(len(sort_tag)):
            assert sort_tag[i] == row_tag_list[i], f"ori = [{row_tag_list}]\nsort = [{sort_tag}]"
    else:
        for i in range(len(sort_text)):
            assert sort_text[i] == row_bool_title_list[i], f"ori = [{row_bool_title_list}]\nsort = [{sort_text}]"


def click_on_word_row_button(c, word: str, ind: int):
    list_container = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    spans = list_container.find_elements(By.XPATH, f'./div/main/main/span[text()=\'{BehaveUtil.clear_string(word)}\']')
    assert len(spans) == 1, f'spans = {len(spans)}'
    scroll_to_bottom(c)
    btn = spans[0].find_element(By.XPATH, f'../../aside/button[{ind}]')
    assert btn is not None
    # print(btn.get_attribute('innerHTML'))
    click_element(c, btn)


@when('"{mentor}" click on [voice icon] of word "{word}" in [32E_Chapter-Word-List-Editor-Page]')
def click_unknown_word(c, mentor: str, word: str):
    click_on_word_row_button(c, word, 1)


@then('[save chapter button] in [bottom app bar] is shown')
def check_save_chapter_btn_not_show(c):
    w__assert_element_existing(c, [A.BottomAppBar, A.Save, A.Button])


@then('[save chapter button] in [bottom app bar] is NOT shown')
def check_save_chapter_btn_not_show(c):
    w__assert_element_not_existing(c, [A.BottomAppBar, A.Save, A.Button])


def is_word_in_used_word_list(c, text: str):
    return is_word_in_used_word_list__in_32e(c, text)


def is_word_in_used_word_list__in_32e(c, text: str):
    text = BehaveUtil.clear_string(text)
    container = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    assert container is not None, "Can NOT find container"
    row_spans = container.find_elements(By.XPATH, "./div/main/main/span")
    assert row_spans is not None, "Can NOT find row_spans"
    for r in row_spans:
        row_text = r.get_attribute('innerHTML').strip()
        print("row_text = ", row_text)
        if row_text == text:
            return True
    return False


@then('{word} is in word list')
def then__word_is_in_word_list(c, word: str):
    assert is_word_in_used_word_list(c, word)


def find_used_word_row_by_text(c, text: str):
    elm = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    assert elm is not None
    row_spans = elm.find_elements(By.XPATH, "./div/main/main/span")
    for r in row_spans:
        row_text = r.get_attribute('innerHTML').strip()
        if row_text == text:
            return r.find_element(By.XPATH, "../../..")
    return None


def find_remove_button_of_used_word_row(c, text: str):
    text = BehaveUtil.clear_string(text)
    row = find_used_word_row_by_text(c, text)
    assert row is not None
    add = row.find_element(By.XPATH, "./main/aside/button[2]")
    return add


@when('{mentor} click on [remove button] of word {word} to remove word from list')
def when__click_on_remove_button_of_word(c, mentor: str, word: str):
    btn = find_remove_button_of_used_word_row(c, word)
    assert btn is not None
    print("click_remove_button_of_word_row -> ", btn)
    click_element(c, btn)


@then('{word} is NOT in word list')
def check_word_not_in_used_list(c, word: str):
    assert not is_word_in_used_word_list(c, word)


@when('"{mentor}" click on [surprise icon] of word "{word}" row in [32E_Chapter-Word-List-Editor-Page]')
def when__click_on_surprise_icon_of_word(c, mentor: str, word: str):
    click_on_word_row_button(c, word, 1)


@when('"{mentor}" click on [remove icon] of word "{word}" row in [32E_Chapter-Word-List-Editor-Page]')
def when__click_on_remove_icon_of_word(c, mentor: str, word: str):
    click_on_word_row_button(c, word, 2)


@when('{mentor} click on [view as learner button] in [more actions drawer]')
def when__click_on_view_as_learner_button_in_more_actions_drawer(c, mentor: str):
    open_more_actions_drawer_from_bottom_app_bar(c)
    dom_id = [A.MoreActions, A.Drawer, A.To, A.Chapter, A.Button]
    w__click_element_by_dom_id(c, dom_id)


@when('{mentor} click on [head mentor info]')
def when__click_on_head_mentor_info(c, mentor: str):
    dom_id = [A.Title, A.Footer, A.Left]
    w__click_element_by_dom_id(c, dom_id)


@when('{mentor} click on [header book title]')
def when__click_on_header_book_title(c, mentor: str):
    dom_id = [A.Title, A.Header]
    w__click_element_by_dom_id(c, dom_id)


@when('{mentor} click on [Chapter Description] area')
def when__click_on_chapter_description_area(c, mentor: str):
    dom_id = [A.Title, A.Main, A.Description]
    w__click_element_by_dom_id(c, dom_id)


@when('{mentor} click on [close button] of dialog')
def when__click_on_close_button_of_dialog(c, mentor: str):
    dom_id = [A.Description, A.Dialog, A.Ok, A.Button]
    w__click_element_by_dom_id(c, dom_id)


@when('{mentor} click on [delete this chapter button] in more actions drawer')
def when__click_on_delete_this_chapter_button_in_more_actions_drawer(c, mentor: str):
    open_more_actions_drawer_from_bottom_app_bar(c)
    click_element_by_dom_id(c, [A.MoreActions, A.Drawer, A.Remove, A.Chapter, A.Button])


@when('{mentor} click on [cancel button] of [confirm to delete chapter dialog]')
def when__click_on_cancel_button_of_confirm_to_delete_chapter_dialog(c, mentor: str):
    click_element_by_dom_id(c, [A.Confirm, A.Remove, A.Chapter, A.Dialog, A.Cancel, A.Button])


@when('{mentor} click on [confirm button] of [confirm to delete chapter dialog]')
def when__click_on_confirm_button_of_confirm_to_delete_chapter_dialog(c, mentor: str):
    click_element_by_dom_id(c, [A.Confirm, A.Remove, A.Chapter, A.Dialog, A.Remove, A.Button])


@then('[confirm to delete chapter dialog] is closed')
def then__confirm_to_delete_chapter_dialog_is_closed(c):
    ids = [A.Confirm, A.Remove, A.Chapter, A.Dialog]
    w__assert_element_not_existing(c, ids)


@then('[confirm to delete chapter dialog] is popup with deleting {words} words')
def then__confirm_to_delete_chapter_dialog_is_popup_with_deleting_words(c, words: str):
    words = BehaveUtil.clear_string(words)
    ids = [A.Confirm, A.Remove, A.Chapter, A.Dialog]
    w__get_element_by_shown_dom_id(c, ids)
    ids = [A.Confirm, A.Remove, A.Chapter, A.Dialog, A.Word]
    w = w__get_element_by_shown_dom_id(c, ids)
    display = w.get_attribute('innerHTML').strip()
    assert f"{words} Words" in display, display