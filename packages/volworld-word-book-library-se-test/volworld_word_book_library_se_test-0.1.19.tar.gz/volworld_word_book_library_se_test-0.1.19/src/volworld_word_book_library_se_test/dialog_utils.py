from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__click_element_by_dom_id
from volworld_common.test.behave.BehaveUtil import BehaveUtil
from behave import *


@when('"{mentor}" click on ["{button}"] of dialog')
def click_on_button(c, mentor: str, button: str):
    button = BehaveUtil.clear_string(button)
    ids = []
    if button == 'Cancel-Button]':
        ids = [A.Dialog, A.Cancel, A.Button]
    if button == 'Save-Button':
        ids = [A.Dialog, A.Save, A.Button]
    # if button == 'add word list button':
    #     ids = [A.Add, A.Word, A.List]

    w__click_element_by_dom_id(c, ids)