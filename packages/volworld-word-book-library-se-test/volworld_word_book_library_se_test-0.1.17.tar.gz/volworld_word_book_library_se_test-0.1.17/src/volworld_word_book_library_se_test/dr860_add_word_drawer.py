from volworld_common.test.behave.BehaveUtil import BehaveUtil

from api.A import A
from volworld_aws_api_common.test.behave.drawer_utils import click_to_open_list_nav_drawer
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, \
    w__click_element_by_dom_id, \
    w__key_in_element_by_dom_id, click_element
from selenium.webdriver.common.by import By
from behave import *

from .nav_utils import open_more_actions_drawer_from_bottom_app_bar


@then('[860_Add-Word-Drawer] is shown')
def then__word_search_drawer_is_shown(c):
    elm = w__get_element_by_shown_dom_id(c, [A.Word, A.Search, A.Drawer])
    assert elm is not None


@when('{mentor} key in {word} in word search input')
def when__enter_search_input(c, mentor: str, word: str):
    w__key_in_element_by_dom_id(c, [A.Search, A.Word], BehaveUtil.clear_string(word))


def find_search_drawer_row_by_text(c, text: str):
    elm = w__get_element_by_shown_dom_id(c, [A.Search, A.Drawer, A.Word, A.List])
    assert elm is not None
    row_spans = elm.find_elements(By.XPATH, "./section/div/main/main/span")
    for r in row_spans:
        row_text = r.get_attribute('innerHTML').strip()
        if row_text == text:
            return r.find_element(By.XPATH, "../../..")
    return None


def find_voice_button_of_search_drawer_row(c, text: str):
    text = BehaveUtil.clear_string(text)
    row = find_search_drawer_row_by_text(c, text)
    assert row is not None
    add = row.find_element(By.XPATH, f"./main/aside/button[1]")  # [1] for voice button
    return add


@when('{mentor} click on [voice button] of word {word} in [860_Add-Word-Drawer]')
def click_add_button_of_word_row(c, mentor: str, word: str):
    btn = find_voice_button_of_search_drawer_row(c, word)
    assert btn is not None
    click_element(c, btn)


@then('Word "{word}" is in word search input')
def click_add_word(c, word: str):
    elm = w__get_element_by_shown_dom_id(c, [A.Search, A.Word])
    assert elm.get_attribute('value').lower() == BehaveUtil.clear_string(word).lower()


@when('{mentor} click on [close drawer button] of [860_Add-Word-Drawer]')
def click_on_close_drawer_button(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Close, A.Word, A.Search, A.Drawer])


@when('"{mentor}" clear word list in [32E_Chapter-Word-List-Editor-Page]')
def clear_word_list(c, mentor: str):
    open_more_actions_drawer_from_bottom_app_bar(c)
    w__click_element_by_dom_id(c, [A.MoreActions, A.Drawer, A.Clear, A.All, A.Word, A.Button])


def find_add_button_of_search_drawer_row(c, text: str):
    text = BehaveUtil.clear_string(text)
    row = find_search_drawer_row_by_text(c, text)
    assert row is not None
    add = row.find_element(By.XPATH, f"./main/aside/button[2]")  # [1] for voice button
    return add


@when('{mentor} click on [add button] of word {word} to add word to list')
def click_add_button_of_word_row(c, mentor: str, word: str):
    btn = find_add_button_of_search_drawer_row(c, word)
    assert btn is not None
    click_element(c, btn)


def load_drawer_word_list(c) -> list:
    elm = w__get_element_by_shown_dom_id(c, [A.Search, A.Drawer, A.Word, A.List])
    assert elm is not None
    rows = elm.find_elements(By.XPATH, "./section/div/main/main/span")
    row_text_list = []
    for r in rows:
        row_text_list.append(r.get_attribute('innerHTML').strip())
        # print(r.get_attribute('innerHTML').strip())
    return row_text_list


@then('the words starting with {word} is shown in [860_Add-Word-Drawer]')
def then__the_words_starting_with_word_is_shown(c, word: str):
    row_text_list = load_drawer_word_list(c)
    prefix = BehaveUtil.clear_string(word)
    for t in row_text_list:
        assert t.startswith(prefix), f"{t} is NOT starting with {prefix}"


def load_drawer_tag_info_list(c) -> list:
    elm = w__get_element_by_shown_dom_id(c, [A.Search, A.Drawer, A.Word, A.List])
    assert elm is not None
    rows = elm.find_elements(By.XPATH, "./section/div/main/nav/main/b")
    row_text_list = []
    for r in rows:
        row_text_list.append(r.get_attribute('innerHTML').strip())
        print(r.get_attribute('innerHTML').strip())
    return row_text_list


@then('the word list of [860_Add-Word-Drawer] is sort by "{sort_type}" in "{dir_type}" order')
def then__the_word_list_of_860_add_word_drawer_is_sort_by(c, sort_type: str, dir_type: str):
    dir_type = BehaveUtil.clear_string(dir_type).lower()
    sort_type = BehaveUtil.clear_string(sort_type).lower()
    row_text_list = load_drawer_word_list(c)
    sort_text = row_text_list.copy()
    row_tag_list = load_drawer_tag_info_list(c)
    row_tag_list = list(map(int, row_tag_list))
    sort_tag = row_tag_list.copy()
    assert_tag = True
    if sort_type == 'alphabetical':
        sort_text.sort()
        assert_tag = False
    if sort_type == 'focusing_learners':
        sort_text.sort()
    if dir_type == 'descending':
        sort_text.reverse()
        sort_tag.reverse()

    if assert_tag:
        for i in range(len(sort_tag)):
            assert sort_tag[i] == row_tag_list[i], f"ori = [{row_tag_list}]\nsort = [{sort_tag}]"
    else:
        for i in range(len(sort_text)):
            assert sort_text[i] == row_text_list[i], f"ori = [{row_text_list}]\nsort = [{sort_text}]"


@when('{mentor} update [sort] type of [860_Add-Word-Drawer] to {sort_type}')
def when__update_sort_type_of_860_add_word_drawer(c, mentor: str, sort_type: str):
    sort_type = BehaveUtil.clear_string(sort_type).lower()
    click_to_open_list_nav_drawer(c, A.SortBy, [A.Word, A.Search])
    if sort_type == 'focusing_learners':
        w__click_element_by_dom_id(c, [A.SortBy, A.Drawer, A.Focusing, A.Button])


@when('{mentor} update [order] type of [860_Add-Word-Drawer] to {dir_type}')
def when__update_order_type_of_860_add_word_drawer(c, mentor: str, dir_type: str):
    dir_type = BehaveUtil.clear_string(dir_type).lower()
    click_to_open_list_nav_drawer(c, A.SortDirection, [A.Word, A.Search])
    if dir_type == 'ascending':
        w__click_element_by_dom_id(c, [A.SortDirection, A.Drawer, A.Ascending, A.Button])
    if dir_type == 'descending':
        w__click_element_by_dom_id(c, [A.SortDirection, A.Drawer, A.Descending, A.Button])


@then('the input of [860_Add-Word-Drawer] is filled by word "{word}"')
def then__the_input_of_860_add_word_drawer_is_filled_by_word(c, word: str):
    elm = w__get_element_by_shown_dom_id(c, [A.Search, A.Word])
    assert elm.get_attribute('value') == BehaveUtil.clear_string(word)


@when('"{mentor}" close [860_Add-Word-Drawer]')
def close_add_word_drawer(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Close, A.Word, A.Search, A.Drawer, A.Right])

