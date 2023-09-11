from behave import *
from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import (
    w__click_element_by_dom_id, click_element_by_dom_id)
from volworld_aws_api_common.test.behave.drawer_utils import (
    click_to_close_list_nav_drawer, \
    waiting_for_drawer_animation)


def open_more_actions_drawer_from_bottom_app_bar(c):
    w__click_element_by_dom_id(c, [A.BottomAppBar, A.MoreActions, A.Button])
    waiting_for_drawer_animation()


def open_more_actions_drawer_from_nav(c):
    w__click_element_by_dom_id(c, [A.List, A.Navigator, A.MoreActions, A.Button])
    waiting_for_drawer_animation()


@when('{mentor} open [more actions drawer]')
def when__open_nav_more_actions_drawer(c, mentor: str):
    open_more_actions_drawer_from_bottom_app_bar(c)


@when('{mentor} click on [Show / Hide Tags] switch on [more actions drawer]')
def click_on_show_hide_tag_switch(c, mentor: str):
    open_more_actions_drawer_from_bottom_app_bar(c)
    # @note input might NOT support EC.visibility_of_element_located()?
    click_element_by_dom_id(c, [A.MoreActions, A.Drawer, A.Show, A.Tag, A.Switch])


@when('{mentor} click on [drawer close button] to hide [more actions drawer]')
def click_to_hide_more_action_drawer(c, mentor: str):
    click_to_close_list_nav_drawer(c, A.MoreActions)
    # close_nav_more_actions_drawer(c)