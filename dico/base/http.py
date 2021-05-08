import io
import typing
from abc import ABC, abstractmethod


class HTTPRequestBase(ABC):
    """
    This abstract class includes all API request methods.

    .. note::
        Although every GET route's name in the API Documents starts with ``Get ...``, but
        they are all changed to `request_...` to prevent confusion with cache get methods.
    """

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
                             name: str,
                             channel_type: int,
                             position: int,
                             topic: str,
                             nsfw: bool,
                             rate_limit_per_user: int,
                             bitrate: int,
                             user_limit: int,
                             permission_overwrites: typing.List[dict],
                             parent_id: str,
                             rtc_region: str,
                             video_quality_mode: int):
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
    def modify_group_dm_channel(self, channel_id, name: str, icon: bin):
        """
        Sends modify channel request, for group DM.

        :param channel_id: Channel ID to request.
        :param name: Name to change.
        :param icon: base64 encoded icon.
        """
        pass

    @abstractmethod
    def modify_thread_channel(self,
                              channel_id,
                              name: str,
                              archived: bool,
                              auto_archive_duration: int,
                              locked: bool,
                              rate_limit_per_user: int):
        """
        Sends modify channel request, for thread channel.

        :param channel_id: Channel ID to request.
        :param name: Name to change.
        :param archived: Whether to se the channel to archived.
        :param auto_archive_duration: Duration to automatically archive the channel.
        :param locked: Whether to lock the thread.
        :param rate_limit_per_user: Rate limit seconds of the thread.
        """
        pass

    @abstractmethod
    def delete_channel(self, channel_id):
        """
        Sends channel delete/close request.

        :param channel_id: Channel ID to request.
        """
        pass

    @abstractmethod
    def request_channel_messages(self, channel_id, around, before, after, limit: int):
        """
        Sends channel messages get request.

        :param channel_id: Channel ID to request.
        :param around: Channel ID to get messages around it.
        :param before: Channel ID to get messages before it.
        :param after:Channel ID to get messages after it.
        :param limit: Maximum messages to get.
        """
        pass

    @abstractmethod
    def request_channel_message(self, channel_id, message_id):
        """
        Sends single channel message get request.

        :param channel_id: Channel ID to request.
        :param message_id: Message ID to request.
        """
        pass

    @property
    def close_channel(self):
        """Alias of :meth:`.delete_channel`"""
        return self.delete_channel

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
