from typing import Any, Dict, List
from profile_reddit_restapi_imp_python_package.ProfileRedditConstants import PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID, PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME
import os
import tqdm
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
import praw
from dotenv import load_dotenv
load_dotenv()

REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME')

object_to_insert = {
    'component_id': PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'yoav.e@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)


class Reddit:

    def __init__(self):
        logger.start("__init__")
        self.reddit = self._authenticate_reddit()
        logger.end("__init__")

    def _authenticate_reddit(self) -> praw.Reddit:

        logger.start("authenticate_reddit")
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=f"random_names (by u/{REDDIT_USERNAME})"
        )

        logger.end("authenticate_reddit")
        return reddit

    def get_subreddit_and_query(self, request: dict = None) -> dict:

        logger.start("get_subreddit_and_query")
        if request:
            subreddit_name, user_count = request['subreddit_name'], request['user_count']
            logger.end("get_subreddit_and_query")
            return subreddit_name, user_count

        subreddit_name = input("Enter subreddit name: ")

        num = input("Enter number of users to fetch (defult is no cap): ")

        user_count = int(num) if len(num) > 0 else None

        logger.end("get_subreddit_and_query", object={'subreddit_name': subreddit_name, 'user_count': user_count})
        return subreddit_name, user_count

    def get_users_from_subreddit(self, subreddit, user_count: int) -> Dict[str, List[Dict[str, Any]]]:
        GET_USERS_FROM_SUBREDDIT_METHOD_NAME = "get_users_from_subreddit()"
        logger.start(GET_USERS_FROM_SUBREDDIT_METHOD_NAME, object={
                     'subreddit': subreddit.name, 'user_count': user_count})
        users = []
        N = user_count

        N = float('inf') if N is None else N

        with tqdm.tqdm(total=N, desc="Getting users") as pbar:
            for submission in subreddit.new(limit=None):
                if len(users) >= N:
                    return users
                for comment in submission.comments.list():
                    logger.info("Reddit user comment")
                    if len(users) >= N:
                        return users
                    if comment.author.name == 'AutoModerator':
                        continue

                    users.append({
                        'profile': {
                            'profile_name': str(comment.author.name),
                            'name_approved': True,
                            'lang_code': "en",
                            'visibility_id': True,
                            'is_approved': True,
                            'profile_type_id': 1,
                            'stars': 2,
                            'last_dialog_workflow_state_id': 1,
                            'comments': str(comment.author.comments),
                            'submissions': str(comment.author.submissions),
                            'created_utc': str(comment.author.created_utc),
                            'has_verified_email': str(comment.author.has_verified_email),
                            'is_employee': str(comment.author.is_employee),
                            'is_mod': str(comment.author.is_mod),
                            'is_gold': str(comment.author.is_gold),
                            'link_karma': str(comment.author.link_karma)
                        },

                        'storage': {
                            "url": str(comment.author.icon_img),
                            "filename": f'{comment.author.name}.jpg',
                                        "file_type": "Profile Image"
                        },
                        
                        'reaction': {
                            'value': str(comment.author.comment_karma),
                            'image': None,
                            'title': 'comment karma',
                            'description': None
                        }
                    }
                    )

                    pbar.update(1)
        logger.end(GET_USERS_FROM_SUBREDDIT_METHOD_NAME)
        return users
