import pyperclip
from selenium.webdriver import Keys
from volworld_common.test.behave.BehaveUtil import BehaveUtil
from behave import *
from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, w__click_element_by_dom_id, w__assert_element_existing, \
    w__key_in_element_by_dom_id


@when('{mentor} input {title} as title and {description} as description for new chapter')
def when__input_title_description(c, mentor: str, title: str, description: str):
    w__key_in_element_by_dom_id(c, [A.Chapter, A.Title, A.Input], BehaveUtil.clear_string(title))
    w__key_in_element_by_dom_id(c, [A.Chapter, A.Description, A.Input], BehaveUtil.clear_string(description))


@when('{mentor} key in [chapter title input] as {title}')
def when__input_title(c, mentor: str, title: str):
    w__key_in_element_by_dom_id(c, [A.Chapter, A.Title, A.Input], BehaveUtil.clear_string(title))


@when('{mentor} paste in [chapter description input] as {description}')
def when__input_description(c, mentor: str, description: str):
    pyperclip.copy(BehaveUtil.clear_string(description))
    input_elm = w__get_element_by_shown_dom_id(c, [A.Chapter, A.Description, A.Input])
    input_elm.click()
    input_elm.send_keys(Keys.CONTROL, 'v')


@then('the input field of [chapter title input] is filled with "{input_text}"')
def then__the_input_field_of_chapter_title_input_is_filled_with(c, input_text: str):
    elm = w__get_element_by_shown_dom_id(c, [A.Chapter, A.Title, A.Input])
    assert elm.get_attribute('value') == input_text, f"input value = [{elm.get_attribute('value')}]\nexpect value = [{input_text}]"


@then('the input field of [chapter description input] is filled with "{input_text}"')
def then__the_input_field_of_chapter_description_input_is_filled_with(c, input_text: str):
    elm = w__get_element_by_shown_dom_id(c, [A.Chapter, A.Description, A.Input])
    assert elm.get_attribute('value') == input_text, f"input value = [{elm.get_attribute('value')}]\nexpect value = [{input_text}]"
