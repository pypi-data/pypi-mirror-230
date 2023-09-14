
import pyperclip
from selenium.webdriver import Keys
from behave import *
from api.A import A
from volworld_aws_api_common.test.behave.selenium_utils import w__get_element_by_shown_dom_id
from volworld_common.test.behave.BehaveUtil import BehaveUtil


@when('"{mentor}" paste in word list of [add word list dialog] as "{word_list}"')
def clear_word_list(c, mentor: str, word_list: str):
    pyperclip.copy(BehaveUtil.clear_string(word_list))
    input_elm = w__get_element_by_shown_dom_id(c, [A.Word, A.List, A.Dialog, A.Input])
    input_elm.click()
    input_elm.send_keys(Keys.CONTROL, 'v')


@then('[save button] of [add word list dialog] is "{active}"')
def check_add_word_list_dialog_btn(c, active: str):
    btn = w__get_element_by_shown_dom_id(c, [A.Word, A.List, A.Dialog, A.Save, A.Button])
    assert btn is not None
    enabled = BehaveUtil.clear_string(active).lower() == 'enabled'
    assert btn.is_enabled() == enabled