from behave import *
from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, \
    w__click_element_by_dom_id, w__assert_element_not_existing, waiting_for_animation


@then('[can not edit non-head version book dialog] will show')
def then__open_can_not_edit_non_head_ver_book_dialog(c):
    elm = w__get_element_by_shown_dom_id(c, [A.Book, A.Not, A.HeadVersion, A.Dialog])
    assert elm is not None


@when('{mentor} click on [warning circle button] in [bottom app bar]')
def when__click_on_warning_on_bottom_app_bar(c, mentor: str):
    w__click_element_by_dom_id(c, [A.BottomAppBar, A.Warning, A.Button])


@then('[can not edit non-head version book dialog] will close')
def then__close_can_not_edit_non_head_ver_book_dialog(c):
    waiting_for_animation()
    w__assert_element_not_existing(c, [A.Book, A.Not, A.HeadVersion, A.Dialog])


@when('{mentor} click on [head version button] of [can not edit non-head version book dialog]')
def click_hv_of_can_not_edit_non_head_ver_book_dialog(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Book, A.Not, A.HeadVersion, A.Dialog, A.HeadVersion])


@when('{mentor} click on [cancel button] of [can not edit non-head version book dialog]')
def click_cancel_of_can_not_edit_non_head_ver_book_dialog(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Book, A.Not, A.HeadVersion, A.Dialog, A.Cancel])


@then('head version of [PgD6F_Book-Chapter-List-Editor-Page] will show')
def check_show_head_version_book_chapters_page(c):
    w__assert_element_not_existing(c, [A.Book, A.Not, A.HeadVersion, A.Dialog])
    elm = w__get_element_by_shown_dom_id(c, [A.BottomAppBar, A.Add, A.Chapter, A.Button])
    assert elm is not None