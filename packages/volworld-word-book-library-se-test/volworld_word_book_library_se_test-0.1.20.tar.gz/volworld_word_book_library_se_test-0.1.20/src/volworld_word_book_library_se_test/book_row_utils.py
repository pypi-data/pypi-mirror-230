from behave import *
from selenium.webdriver.common.by import By
from volworld_aws_api_common.test.behave.drawer_utils import click_to_open_list_nav_drawer

from volworld_common.test.behave.BehaveUtil import BehaveUtil

from api.A import A
from volworld_aws_api_common.test.behave.row_utils import w__get_row_items, w__assert_tag_svg_class_of_all_rows
from volworld_aws_api_common.test.behave.selenium_utils import w__click_element_by_dom_id, \
    w__get_element_by_shown_dom_id, w__get_element_by_presence_dom_id, w__assert_element_not_existing, \
    get_element_by_dom_id
from behave import *


def get_book_tag_info_as_int_list(c) -> list:
    rows = w__get_row_items(c)
    tag_int_list = []
    for r in rows:
        span = r.find_element(By.XPATH, "./main/nav/main/b")
        tag_int_list.append(int(span.get_attribute('innerHTML').strip()))
    return tag_int_list


def get_book_tag_info_as_text_list(c) -> list:
    rows = w__get_row_items(c)
    tag_text_list = []
    for r in rows:
        span = r.find_element(By.XPATH, "./main/nav/main/b")
        tag_text_list.append(span.get_attribute('innerHTML').strip())
    return tag_text_list


def assert_same_list(src: list, exp: list):
    assert len(src) == len(exp)
    for i in range(len(src)):
        assert src[i] == exp[i], f"src[{i}] = [{src[i]}] != [{exp[i]}]\nsrc={src}\nexp={exp}"


def get_book_title_list(c) -> list:
    rows = w__get_row_items(c)
    row_text_list = []
    for r in rows:
        span = r.find_element(By.XPATH, "./main/main/span")
        row_text_list.append(span.get_attribute('innerHTML').strip())
    return row_text_list


def assert_sorted_book_list(c, sort_type: str, sort_dir: str):
    sort_type = BehaveUtil.clear_string(sort_type)
    sort_dir = BehaveUtil.clear_string(sort_dir)
    is_desc = sort_dir.lower() == "descending"
    if sort_type.lower() == "title":
        title_list = get_book_title_list(c)
        new_text_list = list()
        for t in title_list:
            new_text_list.append(t.replace('-', '').replace(' ', '9'))
            # @note '-' is ignored while sorting in PostgreSQL
            # @ref https://stackoverflow.com/questions/4955386/postgresql-ignores-dashes-when-ordering
        ref_list = new_text_list.copy()
        ref_list.sort()
        if is_desc:
            ref_list.reverse()
        assert_same_list(new_text_list, ref_list)
        return

    if sort_type.lower() == "words":
        word_list = get_book_tag_info_as_int_list(c)
        ref_list = word_list.copy()
        ref_list.sort()
        if is_desc:
            ref_list.reverse()
        assert_same_list(word_list, ref_list)
        return


def w__assert_tag_type_of_all_rows(c, tag_type: str, rows):
    tag_type = BehaveUtil.clear_string(tag_type)

    if tag_type.lower() == "words":
        w__assert_tag_svg_class_of_all_rows(c, rows, [A.Word, A.Count])
    if tag_type.lower() == "chapters":
        w__assert_tag_svg_class_of_all_rows(c, rows, [A.Chapter, A.Count])


@then('the tag is showing {tag_type}')
def then__the_tag_is_showing_tag_type(c, tag_type: str):
    rows = w__get_row_items(c)
    w__assert_tag_type_of_all_rows(c, tag_type, rows)


@when('{mentor} update [sort] type of list page to {sort_type}')
def update_sort_type_of_list_page(c, mentor: str, sort_type: str):
    sort_type = BehaveUtil.clear_string(sort_type).lower()
    click_to_open_list_nav_drawer(c, A.SortBy)
    if sort_type == 'importance':
        w__click_element_by_dom_id(c, [A.SortBy, A.Drawer, A.Importance, A.Button])
    if sort_type.lower() == "words":
        w__click_element_by_dom_id(c, [A.SortBy, A.Drawer, A.Word, A.Button])


def assert_book_count_and_total_page(c, book_count_str: str, total_page_count_str: str, total_book_count_str: str = ''):
    book_count = BehaveUtil.clear_int(book_count_str)
    total_page_count = BehaveUtil.clear_int(total_page_count_str)

    elm = w__get_element_by_shown_dom_id(c, [A.InfoRow, A.List])
    chDiv = elm.find_elements(by=By.XPATH, value=f"./div")
    assert len(chDiv) == book_count, f"found [{len(chDiv)}] books != [{book_count}] = expect"

    pg1_id = [A.Page, '1', A.Button]
    # assert page button
    if total_page_count > 1:
        last_pg_id = [A.Page, f"{total_page_count}", A.Button]
        no_pg_id = [A.Page, f"{total_page_count + 1}", A.Button]
        print(f'last_pg_id = [{last_pg_id}]')
        print(f'no_pg_id = [{no_pg_id}]')
        w__get_element_by_presence_dom_id(c, last_pg_id)
        w__assert_element_not_existing(c, no_pg_id)

    # assert book count
    elm = get_element_by_dom_id(c, [A.Page, A.TotalCount])
    all_book_count = int(elm.get_attribute('innerHTML').strip())
    if len(total_book_count_str) > 0:
        total_book_count = BehaveUtil.clear_int(total_book_count_str)
        assert all_book_count == total_book_count

    # not showing page button
    if total_page_count <= 1:
        w__assert_element_not_existing(c, pg1_id)
        return

    # if total_page_count <= 1:
    #     w__assert_element_not_existing(c, [A.Page, A.Info])
    #     return
    # elm = w__get_element_by_shown_dom_id(c, [A.Page, A.Info])
    # info = get_elm_text(elm)
    # all_page_count = int(info.split('/')[1].strip())
    # assert total_page_count == all_page_count


