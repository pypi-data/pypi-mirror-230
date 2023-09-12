# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-06-28 18:22:18
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-06-30 14:16:47
from gailbot.core.engines.watson.am import WatsonAMInterface
from gailbot.core.utils.logger import makelogger
from tests.test_data.setting_data import SETTING_DATA

WATSON_API_KEY = SETTING_DATA.WATSON_SETTING["apikey"]
WATSON_LANG_CUSTOM_ID = SETTING_DATA.WATSON_LANG_CUSTOM_ID
WATSON_REGION = SETTING_DATA.WATSON_SETTING["region"]
WATSON_BASE_LANG_MODEL = SETTING_DATA.WATSON_SETTING["base_model"]

logger = makelogger("watson_am")


def test_init_lm():
    """
    test_init_lm()
    Purpose:            Test to make sure that a Watson AM Interface is
                        initialized as "model"
    Expected Output:    "model" is not empty
    """
    model = WatsonAMInterface(WATSON_API_KEY, WATSON_REGION)
    assert model != None


def test_create_model():
    """
    test_create_model()
    Purpose:            Test to create and delete a custom Watson model
                        using a model id.
    Expected Output:    Newly created custom model is deleted in the end
    """
    model = WatsonAMInterface(WATSON_API_KEY, WATSON_REGION)
    original = model.get_custom_models()
    model.create_custom_model("test", WATSON_BASE_LANG_MODEL, "for testing")
    logger.info(model.get_custom_models())
    new_model_id = model.get_custom_models()["test"]
    model.delete_custom_model(new_model_id)
    logger.info(model.get_custom_models())
    assert original == model.get_custom_models()
