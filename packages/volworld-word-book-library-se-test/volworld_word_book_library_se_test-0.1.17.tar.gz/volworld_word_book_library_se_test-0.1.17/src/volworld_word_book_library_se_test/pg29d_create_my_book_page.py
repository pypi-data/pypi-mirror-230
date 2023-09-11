import pyperclip
from behave import *
from selenium.webdriver import Keys
from volworld_common.test.behave.BehaveUtil import BehaveUtil
from volworld_aws_api_common.test.behave.selenium_utils import (
    w__get_element_by_shown_dom_id, w__click_element_by_dom_id, \
    w__key_in_element_by_dom_id, w__get_element_by_presence_dom_id, w__assert_element_not_existing)
from api.A import A


@then('[public book checkbox] is shown')
def then__public_book_checkbox_is_shown(c):
    elm = w__get_element_by_presence_dom_id(c, [A.Public, A.CheckBox])
    assert elm is not None


@when('{mentor} key in [book title input] as {title}')
def when__key_in_book_title(c, mentor: str, title: str):
    w__key_in_element_by_dom_id(c, [A.Book, A.Title, A.Input], BehaveUtil.clear_string(title))


@when('{mentor} paste in [book description input] as "{description}"')
def when__key_in_book_description(c, mentor: str, description: str):
    pyperclip.copy(description)
    input_elm = w__get_element_by_shown_dom_id(c, [A.Book, A.Description, A.Input])
    input_elm.click()
    input_elm.send_keys(Keys.CONTROL, 'v')


@then('[excess character limit of title warning dialog] is shown')
def then__excess_character_limit_of_title_warning_dialog_is_shown(c):
    elm = w__get_element_by_shown_dom_id(c, [A.Title, A.Character, A.Limit, A.Warning, A.Dialog])
    assert elm is not None


@when('"{mentor}" click on [ok button] of [excess character limit of title warning dialog]')
def when__click_on_ok_button_of_excess_character_limit_of_title_warning_dialog(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Title, A.Character, A.Limit, A.Warning, A.Dialog, A.Ok, A.Button])


@then('[excess character limit of title warning dialog] is closed')
def then__excess_character_limit_of_title_warning_dialog_is_closed(c):
    w__assert_element_not_existing(c, [A.Title, A.Character, A.Limit, A.Warning, A.Dialog])


@then('the input field of [book title input] is filled with "{input_text}"')
def then__the_input_field_of_book_title_input_is_filled_with(c, input_text: str):
    elm = w__get_element_by_shown_dom_id(c, [A.Book, A.Title, A.Input])
    assert elm.get_attribute('value') == input_text, f"input value = [{elm.get_attribute('value')}]\nexpect value = [{input_text}]"


@then('the input field of [book description input] is filled with "{input_text}"')
def then__the_input_field_of_book_description_input_is_filled_with(c, input_text: str):
    elm = w__get_element_by_shown_dom_id(c, [A.Book, A.Description, A.Input])
    assert elm.get_attribute('value') == input_text, f"input value = [{elm.get_attribute('value')}]\nexpect value = [{input_text}]"


@when('{mentor} input {title} as title and {description} as description for new book')
def when__input_title_description_for_new_book(c, mentor: str, title: str, description: str):
    w__key_in_element_by_dom_id(c, [A.Book, A.Title, A.Input], BehaveUtil.clear_string(title))
    w__key_in_element_by_dom_id(c, [A.Book, A.Description, A.Input], BehaveUtil.clear_string(description))