from abc import ABC

from lgt.common.python.lgt_logging import log
from lgt.common.python.slack_client.slack_client import SlackClient
from lgt_data.model import UserModel
from lgt_data.mongo_repository import UserMongoRepository, DedicatedBotRepository
from pydantic import BaseModel
from ..basejobs import BaseBackgroundJobData, BaseBackgroundJob

"""
Update Slack User profile
"""


class UpdateUserSlackProfileJobData(BaseBackgroundJobData, BaseModel):
    user_id: str


class UpdateUserSlackProfileJob(BaseBackgroundJob, ABC):

    @property
    def job_data_type(self) -> type:
        return UpdateUserSlackProfileJobData

    def exec(self, data: UpdateUserSlackProfileJobData):
        user = UserMongoRepository().get(data.user_id)
        bots = DedicatedBotRepository().get_user_bots(data.user_id)
        for bot in bots:
            if bot.invalid_creds:
                log.warning(
                    f'User: {user.email} dedicated bot: {bot.name} credentials are invalid. '
                    f'Not able to update user profile')
                continue

            slack = SlackClient(bot.token, bot.cookies)
            UpdateUserSlackProfileJob.__update_profile(user, slack)

    @staticmethod
    def __update_profile(user: UserModel, slack: SlackClient):
        slack.update_profile(user.slack_profile.to_dic())
        # try to update user photo
        if user.photo_url:
            photo_resp = slack.update_profile_photo(user.photo_url)
            log.info(f"[PHOTO UPDATE] {photo_resp}")
