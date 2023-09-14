import base64

from selenium.webdriver.common.by import By
from volworld_aws_api_common.api.FrontEndUrl import FrontEndUrl
from volworld_common.test.behave.BehaveUtil import BehaveUtil
from api.A import A
from behave import *
from volworld_aws_api_common.test.behave.selenium_utils import (
    w__get_element_by_shown_dom_id, w__click_element_by_dom_id, w__assert_element_existing, \
    w__key_in_element_by_dom_id, w__get_element_by_presence_dom_id, w__assert_element_not_existing, assert_page_id,
    click_element)
from volworld_aws_api_common.test.behave.row_utils import w__get_row_items

from volworld_aws_api_common.test.ProjectMode import ProjectMode

from .book_row_utils import assert_sorted_book_list
from .nav_utils import open_more_actions_drawer_from_bottom_app_bar


@then('the book list is sorted by {sort_type} in {sort_dir} order')
def then__assert_sorted_book_list(c, sort_type: str, sort_dir: str):
    assert_sorted_book_list(c, sort_type, sort_dir)


@then('[empty search results message] is shown')
def then__empty_search_results_message_is_shown(c):
    elm = w__get_element_by_shown_dom_id(c, [A.Empty, A.Search, A.InfoRow, A.List])
    assert elm is not None


@then('[show all book button] is shown with {books_str} books')
def then__show_all_book_button_is_shown(c, books_str: str):
    book_count = BehaveUtil.clear_int(books_str)
    elm = w__get_element_by_shown_dom_id(c, [A.Show, A.All, A.Book, A.Button])
    assert elm is not None
    elm = w__get_element_by_shown_dom_id(c, [A.Empty, A.Search, A.InfoRow, A.List])
    book_info = elm.find_element(By.XPATH, "./header/b")
    assert int(book_info.get_attribute('innerHTML').strip()) == book_count is not None


@when('{mentor} click on [show all book button]')
def when__click_on_show_all_book_button(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Show, A.All, A.Book, A.Button])


@when('{mentor} click on [head image] in 1st row')
def when__click_on_head_image_in_1_st_row(c, mentor):
    rows = w__get_row_items(c)
    book_icon = rows[0].find_element(By.XPATH, f"./main/header/a[1]")
    assert book_icon is not None
    click_element(c, book_icon)


@when('{mentor} click on [book icon] in 1st row')
def when__click_on_book_icon_in_1_st_row(c, mentor):
    rows = w__get_row_items(c)
    book_icon = rows[0].find_element(By.XPATH, f"./main/aside/a[1]")
    assert book_icon is not None
    click_element(c, book_icon)


def to_sort_param(sort: str):
    sort = BehaveUtil.clear_string(sort).lower()
    if sort == 'word':
        return 'w'
    return 'tt'


def to_dir_param(direction: str):
    direction = BehaveUtil.clear_string(direction).lower()
    if direction == 'descending':
        return 'desc'
    return 'asc'


@when('{mentor} open [9F0_My-Book-List-Page] with {itme_per_page} items per page sort by {sort} in {direction} direction')
def open_MyBookListPage(c, mentor: str, itme_per_page: str, sort: str, direction: str):
    c.browser.get(f"{FrontEndUrl.Root}/#/{ProjectMode.testUrlPrefix}{A.Book}/{A.List}"
                  f"?impp={BehaveUtil.clear_int(itme_per_page)}"
                  f"&pg=1"
                  f"&stby={to_sort_param(sort)}"
                  f"&stdr={to_dir_param(direction)}")


@when('{mentor} click on [add book button]')
def when__click_on_add_book_button(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Add, A.Book])


@when('{mentor} click on [add book button] on the bottom app bar')
def when__click_on_add_book_button_on_the_bottom_app_bar(c, mentor: str):
    w__click_element_by_dom_id(c, [A.BottomAppBar, A.Add, A.Book, A.Button])


@when('{mentor} click on [add book button] in the [more actions]')
def click_on_add_book_button(c, mentor: str):
    open_more_actions_drawer_from_bottom_app_bar(c)
    w__click_element_by_dom_id(c, [A.MoreActions, A.Drawer, A.To, A.Add, A.Book, A.Button])


@then('information of no book is shown')
def then__no_book_information_is_showing(c):
    elm = w__get_element_by_shown_dom_id(c, [A.Empty, A.InfoRow, A.List])
    assert elm.get_attribute('innerHTML').strip().find("You have no word book.") > 0

# @then('there is no row in list page')
# def then__no_book_in_list_page(c):
#     assert_no_book_in_list_page(c)


@then('additional [add book button] is shown')
def then__additional_add_book_button_is_shown(c):
    elm = w__get_element_by_shown_dom_id(c, [A.Add, A.Book])
    assert elm is not None