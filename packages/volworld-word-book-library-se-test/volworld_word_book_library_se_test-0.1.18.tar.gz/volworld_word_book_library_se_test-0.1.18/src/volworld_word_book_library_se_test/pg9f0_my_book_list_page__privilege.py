from volworld_common.test.behave.BehaveUtil import BehaveUtil
from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id, w__click_element_by_dom_id, \
    get_element_by_dom_id, click_element_by_dom_id
from volworld_aws_api_common.test.behave.input_utils import assert_input_elm_enabled_by_dom_id, assert_input_elm_selected_by_dom_id, \
    assert_input_elm_not_selected_by_dom_id
from behave import *


@then('{mentor} find [show public] switch on [more actions drawer] is NOT [enabled]')
def then__show_public_switch_in_more_actions_is_not_enabled(c, mentor: str):
    assert_input_elm_enabled_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Public, A.Switch], False)


@then('{mentor} find [show private] switch on [more actions drawer] is NOT [enabled]')
def then__show_private_switch_in_more_actions_is_not_enabled(c, mentor: str):
    assert_input_elm_enabled_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Private, A.Switch], False)


@then('{mentor} find [show public] switch on [more actions drawer] is [enabled]')
def then__show_public_switch_in_more_actions_is_enabled(c, mentor: str):
    assert_input_elm_enabled_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Public, A.Switch], True)


@then('{mentor} find [show private] switch on [more actions drawer] is [enabled]')
def then__show_private_switch_in_more_actions_is_enabled(c, mentor: str):
    assert_input_elm_enabled_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Private, A.Switch], True)


@then('{mentor} find [show private] switch on [more actions drawer] is [checked]')
def then__show_private_switch_in_more_actions_is_checked(c, mentor: str):
    assert_input_elm_selected_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Private, A.Switch])


@then('{mentor} find [show private] switch on [more actions drawer] is NOT [checked]')
def then__show_private_switch_in_more_actions_is_not_checked(c, mentor: str):
    assert_input_elm_not_selected_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Private, A.Switch])


@then('{mentor} find [show public] switch on [more actions drawer] is [checked]')
def then__show_public_switch_in_more_actions_is_checked(c, mentor: str):
    assert_input_elm_selected_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Public, A.Switch])


@then('{mentor} find [show public] switch on [more actions drawer] is NOT [checked]')
def then__show_public_switch_in_more_actions_is_not_checked(c, mentor: str):
    assert_input_elm_not_selected_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Public, A.Switch])


@when('{mentor} click on [show private] switch on [more actions drawer]')
def when__click_on_show_private_switch_in_more_actions(c, mentor: str):
    # @note can not wait for input?
    click_element_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Private, A.Switch])


@when('{mentor} click on [show public] switch on [more actions drawer]')
def when__click_on_show_public_switch_in_more_actions(c, mentor: str):
    # @note can not wait for input?
    click_element_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Public, A.Switch])

