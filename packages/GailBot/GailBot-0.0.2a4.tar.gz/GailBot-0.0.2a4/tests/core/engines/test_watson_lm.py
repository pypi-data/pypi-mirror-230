# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-06-28 18:22:18
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-06-30 14:16:41
from gailbot.core.engines.watson.lm import WatsonLMInterface
from gailbot.core.utils.logger import makelogger
from tests.test_data.setting_data import SETTING_DATA

WATSON_API_KEY = SETTING_DATA.WATSON_SETTING["apikey"]
WATSON_LANG_CUSTOM_ID = SETTING_DATA.WATSON_LANG_CUSTOM_ID
WATSON_REGION = SETTING_DATA.WATSON_SETTING["region"]
WATSON_BASE_LANG_MODEL = SETTING_DATA.WATSON_SETTING["base_model"]

logger = makelogger("watson_lm")


def test_init_lm():
    """
    test_init_lm()
    Purpose:            Test to see if Watson LM Interface is initialized properly
    Expected Output:    The intercace initialized correctly with language model
                        names printed out.
    """
    model = WatsonLMInterface(WATSON_API_KEY, WATSON_REGION)
    assert model != None
    assert model.get_base_models
    logger.info(model.get_base_model([WATSON_BASE_LANG_MODEL]))
    logger.info(model.get_base_models())
    logger.info(model.get_custom_model([WATSON_LANG_CUSTOM_ID]))
    logger.info(model.get_custom_models())


def test_create_model():
    """
    test_create_model()
    Purpose:            Test to see if creating a custom test model works with
                        Watson LM intercace. A custom model called "test" is
                        created, added, and then deleted
    Expected Output:    The custom made model is deleted and that remaining
                        models match with original list of models. Print lists
                        of models
    """
    model = WatsonLMInterface(WATSON_API_KEY, WATSON_REGION)
    original = model.get_custom_models()
    model.create_custom_model("test", WATSON_BASE_LANG_MODEL, "for testing")
    logger.info(model.get_custom_models())
    new_model_id = model.get_custom_models()["test"]
    model.delete_custom_model(new_model_id)
    logger.info(model.get_custom_models())
    assert original == model.get_custom_models()


def _failed_test_train_model():
    """error:   No input data available for training"""
    model = WatsonLMInterface(WATSON_API_KEY, WATSON_REGION)
    model.create_custom_model("test", WATSON_BASE_LANG_MODEL, "for testing")
    new_model_id = model.get_custom_models()["test"]
    assert model.train_custom_model(new_model_id)
    model.delete_custom_model(new_model_id)
    logger.info(model.get_custom_models())


def test_get_base():
    """
    test_get_base()
    Purpose:            Test the functionality of get_base_models() method
    Expected Output:    The result of get_base_model() method printed out
    """
    model = WatsonLMInterface(WATSON_API_KEY, WATSON_REGION)
    print(model.get_base_models())
