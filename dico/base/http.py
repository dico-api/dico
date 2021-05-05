import io
import typing
from abc import ABC, abstractmethod


class HTTPRequestBase(ABC):
    BASE_URL = "https://discord.com/api/v8"

    @abstractmethod
    def request(self, route: str, meth: str, body: dict = None, is_json: bool = False, *, retry: int = 3, **kwargs):
        """
        This function should wrap :meth:`._request` with rate limit handling.
        :return:
        """
        pass

    @abstractmethod
    def _request(self, route: str, meth: str, body: dict = None, is_json: bool = False, **kwargs) -> typing.Tuple[int, dict]:
        """
        HTTP Requesting part.
        :return: Tuple[int, dict]
        """
        pass

    @abstractmethod
    def request_channel(self, channel_id):
        """
        Sends get channel request.

        :param channel_id: Channel ID to request.
        """
        pass

    @abstractmethod
    def modify_guild_channel(self,
                             channel_id,
                             name: str = None,
                             channel_type: int = None,
                             position: int = None,
                             topic: str = None,
                             nsfw: bool = None,
                             rate_limit_per_user: int = None,
                             bitrate: int = None,
                             user_limit: int = None,
                             permission_overwrites: typing.List[dict] = None,
                             parent_id: str = None,
                             rtc_region: str = None,
                             video_quality_mode: int = None):
        """
        Sends modify channel request, for guild channel.

        :param channel_id: Channel ID to request.
        :param name: Name to change.
        :param channel_type: Type of the channel.
        :param position: Channel position.
        :param topic: Channel topic to change.
        :param nsfw: Whether the channel is NSFW.
        :param rate_limit_per_user: Rate limit seconds of the channel.
        :param bitrate: Bitrate of the channel.
        :param user_limit: Limitation of the user count.
        :param permission_overwrites: Specific permissions for user of role.
        :param parent_id: Parent category ID.
        :param rtc_region: Voice region ID.
        :param video_quality_mode: Video quality of the channel.
        """
        pass

    @abstractmethod
    def modify_group_dm_channel(self, channel_id, name: str = None, icon: bin = None):
        """
        Sends modify channel request, for guild channel.

        :param channel_id: Channel ID to request.
        :param name: Name to change.
        :param icon: base64 encoded icon.
        """
        pass

    @abstractmethod
    def create_message(self,
                       channel_id,
                       content: str,
                       nonce: typing.Union[int, str],
                       tts: bool,
                       embed: dict,
                       allowed_mentions: dict,
                       message_reference: dict):
        """
        Sends create message request.

        :param channel_id: ID of the channel.
        :param content: Content of the message.
        :param nonce:
        :param tts: Whether this message is TTS.
        :param embed: Embed of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :param message_reference: Message to reference.
        :return: Message object dict.
        """
        pass

    @abstractmethod
    def create_message_with_files(self,
                                  channel_id,
                                  content: str,
                                  files: typing.List[typing.Union[io.FileIO]],
                                  nonce: typing.Union[int, str],
                                  tts: bool,
                                  embed: dict,
                                  allowed_mentions: dict,
                                  message_reference: dict):
        """
        Sends create message request with files.

        :param channel_id: ID of the channel.
        :param content: Content of the message.
        :param files: Files of the message.
        :param nonce:
        :param tts: Whether this message is TTS.
        :param embed: Embed of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :param message_reference: Message to reference.
        :return: Message object dict.
        """
        pass

    @abstractmethod
    def edit_message(self,
                     channel_id,
                     message_id,
                     content: str,
                     embed: dict,
                     flags: int,
                     allowed_mentions: dict,
                     attachments: typing.List[dict]):
        """
        Sends edit message request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to edit.
        :param content: Content of the message.
        :param embed: Embed of the message.
        :param flags:
        :param allowed_mentions: Allowed mentions of the message.
        :param attachments: Attachments to keep.
        :return: Message object dict.
        """
        pass

    @abstractmethod
    def delete_message(self, channel_id, message_id):
        """
        Sends delete message request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to edit.
        """
        pass

    @classmethod
    @abstractmethod
    def create(cls, token, *args, **kwargs):
        """
        Creates new HTTP request client.

        :param token: Token of the bot.
        :param args: Extra optional args.
        :param kwargs: Extra optional keyword args.
        :return: Initialized object.
        """
        pass
