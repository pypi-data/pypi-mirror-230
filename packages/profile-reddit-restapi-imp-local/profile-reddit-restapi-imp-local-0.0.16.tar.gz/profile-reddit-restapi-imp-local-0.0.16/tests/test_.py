from dotenv import load_dotenv

load_dotenv()
import os
import sys
sys.path.append(os.getcwd())
import praw
from profile_reddit_restapi_imp_python_package.handler import RedditImporter
from profile_reddit_restapi_imp_python_package .search_reddit import Reddit
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger
from profile_reddit_restapi_imp_python_package.ProfileRedditConstants import *


object_to_insert = {
    'component_id': PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    'developer_email': 'yoav.e@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)

# Add the parent directory to the path so we can import the script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#


def test_authenticate_reddit():
    TEST_AUTHENTICATE_REDDIT_METHOD_NAME = "test_authenticate_reddit()"
    logger.start(TEST_AUTHENTICATE_REDDIT_METHOD_NAME)
    reddit = Reddit()._authenticate_reddit()

    result = isinstance(reddit, praw.Reddit)
    logger.end(TEST_AUTHENTICATE_REDDIT_METHOD_NAME, object={'result': result})
    assert result



def test_get_subreddit_and_query():
    TEST_GET_SUBREDDIT_AND_QUERY_METHOD_NAME = "test_get_subreddit_and_query()"
    FUNNY = "funny"
    USER_COUNT = 10
    logger.start(TEST_GET_SUBREDDIT_AND_QUERY_METHOD_NAME)
    request = {"subreddit_name": FUNNY, "user_count": USER_COUNT}
    subreddit_name, num = Reddit().get_subreddit_and_query(request=request)
    logger.info(f"subreddit_name {subreddit_name}")
    logger.info(f"num {num}")
    assert subreddit_name == "funny"
    assert num == 10
    logger.end(TEST_GET_SUBREDDIT_AND_QUERY_METHOD_NAME)


