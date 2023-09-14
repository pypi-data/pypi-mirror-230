from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, w__click_element_by_dom_id, \
    w__assert_element_not_existing
from behave import *


@then('[excess limit of create empty book warning dialog] is shown')
def check_showing_excess_create_warning(c):
    elm = w__get_element_by_shown_dom_id(c, [A.Create, A.Limit, A.Warning, A.Dialog])
    assert elm is not None


@when('"{mentor}" click on [ok button] of [excess limit of create empty book warning dialog]')
def click_ok_of_showing_excess_create_warning(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Create, A.Limit, A.Warning, A.Dialog, A.Ok, A.Button])


@then('[excess limit of create empty book warning dialog] is closed')
def check_closed_excess_create_warning(c):
    w__assert_element_not_existing(c, [A.Create, A.Limit, A.Warning, A.Dialog])


@then('[excess character limit of description warning dialog] is shown')
def then__excess_character_limit_of_description_warning_is_shown(c):
    elm = w__get_element_by_shown_dom_id(c, [A.Description, A.Character, A.Limit, A.Warning, A.Dialog])
    assert elm is not None


@when('"{mentor}" click on [ok button] of [excess character limit of description warning dialog]')
def when__click_on_ok_button_of_excess_character_limit_of_description_warning_dialog(c, mentor: str):
    w__click_element_by_dom_id(c, [A.Description, A.Character, A.Limit, A.Warning, A.Dialog, A.Ok, A.Button])


@then('[excess character limit of description warning dialog] is closed')
def then__excess_character_limit_of_description_warning_dialog_is_closed(c):
    w__assert_element_not_existing(c, [A.Description, A.Character, A.Limit, A.Warning, A.Dialog])
