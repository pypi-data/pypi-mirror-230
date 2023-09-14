from volworld_common.test.behave.BehaveUtil import BehaveUtil
from api.A import A
from behave import *
from volworld_aws_api_common.test.behave.selenium_utils import (
    w__get_element_by_shown_dom_id, w__click_element_by_dom_id,
    w__key_in_element_by_dom_id,
    get_element_by_dom_id)


def search_books_by_title(c, keywords: str):
    close_btn = get_element_by_dom_id(c, [A.Search, A.Close])
    print("close_btn = ", close_btn)
    if close_btn is None:
        print("Click  [A.Search, A.Close] button...")
        w__click_element_by_dom_id(c, [A.Search, A.Open])
    w__key_in_element_by_dom_id(c, [A.Search, A.Text], BehaveUtil.clear_string(keywords))
    w__click_element_by_dom_id(c, [A.Search, A.Search])


@when('{mentor} search books by title keyword {keywords}')
def when__search_books_by_title_keyword(c, mentor: str, keywords: str):
    search_books_by_title(c, keywords)


@when('{mentor} close search area')
def when__close_search_area(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Search, A.Close])


@when('{mentor} open search area')
def when__open_search_area(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Search, A.Open])


@then('title keyword {keywords} is shown in the input field of search area')
def then__showing_search_keyword(c, keywords: str):
    keywords = BehaveUtil.clear_string(keywords)
    elm = w__get_element_by_shown_dom_id(c, [A.Search, A.Text])
    assert keywords == elm.get_attribute('value').strip()
