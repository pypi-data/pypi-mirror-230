from api.A import A

from volworld_aws_api_common.test.behave.row_utils import assert_tag_icon_class_of_list, load_row_text_list, load_row_tag_info_list
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, w__click_element_by_dom_id, \
    waiting_for_animation, w__assert_element_not_existing, click_element, assert_page_id, \
    w__get_element_by_shown_xpath
from volworld_common.test.behave.BehaveUtil import BehaveUtil
from behave import *


@then('the chapter list is sorted by {sort_type} in {sort_dir} order')
def then__assert_sorted_chapter_list(c, sort_type: str, sort_dir: str):
    # target_page = getattr(c, CotA.TargetPage)
    # print(f"target_page = {target_page}")
    # print(f"TargetPage.NGSL__PgD6F_Book_Chapter_List_Editor_Page = {Page.NGSL__PgD6F_Book_Chapter_List_Editor_Page}")

    assert_sort_chapter_list(c, sort_type, sort_dir)


def assert_sort_chapter_list(c, sort_type: str, dir_type: str):
    dir_type = BehaveUtil.clear_string(dir_type).lower()
    sort_type = BehaveUtil.clear_string(sort_type).lower()
    row_bool_title_list = load_row_text_list(c)
    sort_text = row_bool_title_list.copy()
    row_tag_list = load_row_tag_info_list(c)
    row_tag_list = list(map(int, row_tag_list))
    sort_tag = row_tag_list.copy()
    assert_tag = True
    if sort_type == 'title':
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


@then('the tag of chapter list is showing {tag_type}')
def then__the_tag_of_chapter_list(c, tag_type: str):
    tag_type = BehaveUtil.clear_string(tag_type).lower()
    if tag_type == 'words':
        assert_tag_icon_class_of_list(c, f"SvgIcon-{'-'.join([A.Word, A.Count])}")
    if tag_type == 'focusing_learners':
        assert_tag_icon_class_of_list(c, f"SvgIcon-{'-'.join([A.Focusing, A.Learner, A.Count])}")


@then('[full book description dialog] is closed')
def then__full_book_description_dialog_is_closed(c):
    waiting_for_animation()
    w__assert_element_not_existing(c, [A.Description, A.Dialog])


@when('{mentor} click on [close button] of [full book description dialog]')
def when__click_on_dialog_ok_button(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Description, A.Dialog, A.Ok, A.Button])


@then('[full book description dialog] is shown')
def then__full_book_description_dialog_is_shown(c):
    elm = w__get_element_by_shown_dom_id(c, [A.Description, A.Dialog])
    assert elm is not None


@when('{mentor} click on chapter icon link of row {row_name}')
def when__click_on_chapter_icon_link_of_row(c, mentor: str, row_name: str):
    link = w__get_element_by_shown_xpath(c, f"//text()[. = 'Chapter 01']/../../../aside/a")
    # link = c.browser.find_element(By.XPATH, xpath)
    assert link is not None
    click_element(c, link)


@when('{mentor} click on [book chapter list button] in [bottom app bar]')
def when__click_on_chapter_icon_of_row(c, mentor: str):
    w__click_element_by_dom_id(c, [A.BottomAppBar, A.To, A.Book, A.Button])


@when('{mentor} click on [add chapter button]')
def when__click_on_add_chapter_button(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Add, A.Chapter])


@when('{mentor} click on [Book Description] area')
def when__click_on_book_description_area(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Title, A.Main, A.Description])


@then('[Already has a emtpy chapter dialog] is shown')
def then__already_has_a_emtpy_chapter_dialog_is_shown(c):
    w__get_element_by_shown_dom_id(c, [A.Empty, A.Chapter, A.Existing, A.Dialog])


@then('[Already has a emtpy chapter dialog] is closed')
def then__already_has_a_emtpy_chapter_dialog_is_closed(c):
    w__assert_element_not_existing(c, [A.Empty, A.Chapter, A.Existing, A.Dialog])


@when('{mentor} click on [add chapter button] in [bottom app bar]')
def when__click_on_add_chapter_button_in_bottom_app_bar(c, mentor: str):
    w__click_element_by_dom_id(c, [A.BottomAppBar, A.Add, A.Chapter, A.Button])



@when('{mentor} click on [cancel button] of [Already has a emtpy chapter dialog]')
def when__click_on_cancel_button_of_already_has_a_emtpy_chapter_dialog(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Empty, A.Chapter, A.Existing, A.Dialog, A.Cancel])


@when('{mentor} click on [edit empty chapter] of [Already has a emtpy chapter dialog]')
def when__click_on_edit_empty_chapter_of_already_has_a_emtpy_chapter_dialog(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Empty, A.Chapter, A.Existing, A.Dialog, A.Edit, A.Empty, A.Chapter])