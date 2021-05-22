import io
import typing
from abc import ABC, abstractmethod


class HTTPRequestBase(ABC):
    """
    This abstract class includes all API request methods.

    .. note::
        - Although every GET route's name in the API Documents starts with ``Get ...``, but
          they are all changed to `request_...` to prevent confusion with cache get methods.

        - Part of interaction methods are merged to one, since those are listed as separate endpoint but only the difference is the ID.
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

    # Channel Requests

    def request_channel(self, channel_id):
        """
        Sends get channel request.

        :param channel_id: Channel ID to request.
        """
        return self.request(f"/channels/{channel_id}", "GET")

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
        body = {}
        if name is not None:
            body["name"] = name
        if channel_type is not None:
            body["channel_type"] = channel_type
        if position is not None:
            body["position"] = position
        if topic is not None:
            body["topic"] = topic
        if nsfw is not None:
            body["nsfw"] = nsfw
        if rate_limit_per_user is not None:
            body["rate_limit_per_user"] = rate_limit_per_user
        if bitrate is not None:
            body["bitrate"] = bitrate
        if user_limit is not None:
            body["user_limit"] = user_limit
        if permission_overwrites is not None:
            body["permission_overwrites"] = permission_overwrites
        if parent_id is not None:
            body["parent_id"] = parent_id
        if rtc_region is not None:
            body["rtc_region"] = rtc_region
        if video_quality_mode is not None:
            body["video_quality_mode"] = video_quality_mode
        return self.request(f"/channels/{channel_id}", "PATCH", body, is_json=True)

    def modify_group_dm_channel(self, channel_id, name: str = None, icon: bin = None):
        """
        Sends modify channel request, for group DM.

        :param channel_id: Channel ID to request.
        :param name: Name to change.
        :param icon: base64 encoded icon.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if icon is not None:
            body["icon"] = icon
        return self.request(f"/channels/{channel_id}", "PATCH", body, is_json=True)

    def modify_thread_channel(self,
                              channel_id,
                              name: str = None,
                              archived: bool = None,
                              auto_archive_duration: int = None,
                              locked: bool = None,
                              rate_limit_per_user: int = None):
        """
        Sends modify channel request, for thread channel.

        :param channel_id: Channel ID to request.
        :param name: Name to change.
        :param archived: Whether to se the channel to archived.
        :param auto_archive_duration: Duration to automatically archive the channel.
        :param locked: Whether to lock the thread.
        :param rate_limit_per_user: Rate limit seconds of the thread.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if archived is not None:
            body["archived"] = archived
        if auto_archive_duration is not None:
            body["auto_archive_duration"] = auto_archive_duration
        if locked is not None:
            body["locked"] = locked
        if rate_limit_per_user is not None:
            body["rate_limit_per_user"] = rate_limit_per_user
        return self.request(f"/channels/{channel_id}", "PATCH", body, is_json=True)

    def delete_channel(self, channel_id):
        """
        Sends channel delete/close request.

        :param channel_id: Channel ID to request.
        """
        return self.request(f"/channels/{channel_id}", "DELETE")

    def request_channel_messages(self, channel_id, around=None, before=None, after=None, limit: int=None):
        """
        Sends channel messages get request.

        :param channel_id: Channel ID to request.
        :param around: Channel ID to get messages around it.
        :param before: Channel ID to get messages before it.
        :param after:Channel ID to get messages after it.
        :param limit: Maximum messages to get.
        """
        if around and before and after:
            raise ValueError("Only around or before or after must be passed.")
        query = {}
        if around:
            query["around"] = around
        if before:
            query["before"] = before
        if after:
            query["after"] = after
        if limit:
            query["limit"] = limit
        return self.request(f"/channels/{channel_id}/messages", "GET", params=query)

    def request_channel_message(self, channel_id, message_id):
        """
        Sends single channel message get request.

        :param channel_id: Channel ID to request.
        :param message_id: Message ID to request.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}", "GET")

    def create_message(self,
                       channel_id,
                       content: str = None,
                       nonce: typing.Union[int, str] = None,
                       tts: bool = False,
                       embed: dict = None,
                       allowed_mentions: dict = None,
                       message_reference: dict = None):
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
        if not (content or embed):
            raise ValueError("either content or embed must be passed.")
        body = {}
        if content is not None:
            body["content"] = content
        if embed is not None:
            body["embed"] = embed
        if nonce is not None:
            body["nonce"] = nonce
        if tts is not None:
            body["tts"] = tts
        if allowed_mentions is not None:
            body["allowed_mentions"] = allowed_mentions
        if message_reference is not None:
            body["message_reference"] = message_reference
        return self.request(f"/channels/{channel_id}/messages", "POST", body, is_json=True)

    @abstractmethod
    def create_message_with_files(self,
                                  channel_id,
                                  content: str,
                                  files: typing.List[io.FileIO],
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

    def crosspost_message(self, channel_id, message_id):
        """
        Sends crosspost message request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to crosspost.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}/crosspost", "POST")

    def create_reaction(self, channel_id, message_id, emoji: str):
        """
        Sends create reaction request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to react.
        :param emoji: Emoji to add.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me", "PUT")

    def delete_reaction(self, channel_id, message_id, emoji: str, user_id="@me"):
        """
        Sends delete reaction request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to request.
        :param emoji: Emoji to delete.
        :param user_id: User ID to delete reaction. Pass ``@me`` to remove own.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}", "DELETE")

    def request_reactions(self, channel_id, message_id, emoji: str, after=None, limit=None):
        """
        Sends get reactions request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to request.
        :param emoji: Emoji to request.
        :param after: User ID to request after this user.
        :param limit: Maximum number to request.
        """
        params = {}
        if after is not None:
            params["after"] = after
        if limit is not None:
            params["limit"] = limit
        return self.request(f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}", "GET", params=params)

    def delete_all_reactions(self, channel_id, message_id):
        """
        Sends delete all reactions request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to request.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}/reactions", "DELETE")

    def delete_all_reactions_emoji(self, channel_id, message_id, emoji: str):
        """
        Sends delete all reactions emoji request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to request.
        :param emoji: Emoji to delete.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}", "DELETE")

    def edit_message(self,
                     channel_id,
                     message_id,
                     content: str = None,
                     embed: dict = None,
                     flags: int = None,
                     allowed_mentions: dict = None,
                     attachments: typing.List[dict] = None):
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
        body = {}
        if content is not None:
            body["content"] = content
        if embed is not None:
            body["embed"] = embed
        if flags is not None:
            body["flags"] = flags
        if allowed_mentions is not None:
            body["allowed_mentions"] = allowed_mentions
        if attachments is not None:
            body["attachments"] = attachments
        return self.request(f"/channels/{channel_id}/messages/{message_id}", "PATCH", body, is_json=True)

    def delete_message(self, channel_id, message_id):
        """
        Sends delete message request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to edit.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}", "DELETE")

    def bulk_delete_messages(self, channel_id, message_ids: typing.List[str]):
        """
        Sends bulk delete message request.

        :param channel_id: ID of the channel.
        :param message_ids: List of the message IDs to delete.
        """
        body = {"messages": list(map(str, message_ids))}
        return self.request(f"/channels/{channel_id}/messages/bulk-delete", "POST", body, is_json=True)

    def edit_channel_permissions(self, channel_id, overwrite_id, allow, deny, overwrite_type):
        """
        Sends edit channel permissions request.

        :param channel_id: ID of the channel.
        :param overwrite_id: Role or Member ID to edit permissions.
        :param allow: What permissions to allow.
        :param deny: What permissions to deny.
        :param overwrite_type: Type of the overwrite target. Set to 0 for Role, and 1 for Member.
        """
        body = {"allow": allow, "deny": deny, "type": overwrite_type}
        return self.request(f"/channels/{channel_id}/permissions/{overwrite_id}", "PUT", body, is_json=True)

    # Webhook Requests

    def create_webhook(self, channel_id, name: str, avatar: str = None):
        """
        Sends create webhook request.

        :param channel_id: ID of the channel.
        :param name: Name of the webhook.
        :param avatar: URL of the avatar image.
        """
        body = {"name": name}
        if avatar is not None:
            body["avatar"] = avatar
        return self.request(f"/channels/{channel_id}/webhooks", "POST", body, is_json=True)

    def request_channel_webhooks(self, channel_id):
        """
        Sends get channel webhooks request.

        :param channel_id: ID of the channel.
        """
        return self.request(f"/channels/{channel_id}/webhooks", "GET")

    def request_guild_webhooks(self, guild_id):
        """
        Sends get guild webhooks request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/webhooks", "GET")

    def request_webhook(self, webhook_id):
        """
        Sends get webhook request.

        :param webhook_id: ID of the webhook.
        """
        return self.request(f"/webhooks/{webhook_id}", "GET")

    def request_webhook_with_token(self, webhook_id, webhook_token):
        """
        Sends get webhook request.

        :param webhook_id: ID of the webhook.
        :param webhook_token: Token of the webhook.
        """
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}", "GET")

    def modify_webhook(self, webhook_id, name: str = None, avatar: str = None, channel_id: str = None):
        """
        Sends modify webhook request.

        :param webhook_id: ID of the webhook.
        :param name: Name of the webhook.
        :param avatar: URL of the avatar image.
        :param channel_id: ID of the channel.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if avatar is not None:
            body["avatar"] = avatar
        if channel_id is not None:
            body["channel_id"] = channel_id
        return self.request(f"/webhooks/{webhook_id}", "PATCH", body, is_json=True)

    def modify_webhook_with_token(self, webhook_id, webhook_token, name: str = None, avatar: str = None):
        """
        Sends modify webhook request.

        :param webhook_id: ID of the webhook.
        :param webhook_token: Token of the webhook.
        :param name: Name of the webhook.
        :param avatar: URL of the avatar image.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if avatar is not None:
            body["avatar"] = avatar
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}", "PATCH", body, is_json=True)

    def delete_webhook(self, webhook_id):
        """
        Sends delete webhook request.

        :param webhook_id: ID of the webhook.
        """
        return self.request(f"/webhooks/{webhook_id}", "DELETE")

    def delete_webhook_with_token(self, webhook_id, webhook_token):
        """
        Sends delete webhook request with token.

        :param webhook_id: ID of the webhook.
        :param webhook_token: Token of the webhook.
        """
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}", "DELETE")

    def execute_webhook(self,
                        webhook_id,
                        webhook_token,
                        wait: bool = None,
                        thread_id=None,
                        content: str = None,
                        username: str = None,
                        avatar_url: str = None,
                        tts: bool = False,
                        embeds: typing.List[dict] = None,
                        allowed_mentions: dict = None,
                        flags: int = None):
        """
        Sends execute webhook request.

        :param webhook_id: ID of the webhook.
        :param webhook_token: Token of the webhook.
        :param wait: Whether to wait response of the server.
        :param thread_id: ID of the thread.
        :param content: Content of the message.
        :param username: Name of the webhook.
        :param avatar_url: URL of the avatar image.
        :param tts: Whether this message is TTS.
        :param embeds: List of embeds of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :return: Message object dict.
        :param flags: Flags of the message.
        """
        if not (content or embeds):
            raise ValueError("either content or embeds must be passed.")
        body = {}
        if content is not None:
            body["content"] = content
        if username is not None:
            body["username"] = username
        if avatar_url is not None:
            body["avatar_url"] = avatar_url
        if tts is not None:
            body["tts"] = tts
        if embeds is not None:
            body["embeds"] = embeds
        if allowed_mentions is not None:
            body["allowed_mentions"] = allowed_mentions
        if flags is not None:
            body["flags"] = flags
        params = {}
        if wait is not None:
            params["wait"] = "true" if wait else "false"
        if thread_id is not None:
            params["thread_id"] = thread_id
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}", "POST", body, is_json=True, params=params)

    @abstractmethod
    def execute_webhook_with_files(self,
                                   webhook_id,
                                   webhook_token,
                                   wait: bool = None,
                                   thread_id=None,
                                   content: str = None,
                                   username: str = None,
                                   avatar_url: str = None,
                                   tts: bool = False,
                                   files: typing.List[io.FileIO] = None,
                                   embeds: typing.List[dict] = None,
                                   allowed_mentions: dict = None,
                                   flags: int = None):
        """
        Sends execute webhook request with files.

        :param webhook_id: ID of the webhook.
        :param webhook_token: Token of the webhook.
        :param wait: Whether to wait response of the server.
        :param thread_id: ID of the thread.
        :param content: Content of the message.
        :param username: Name of the webhook.
        :param avatar_url: URL of the avatar image.
        :param tts: Whether this message is TTS.
        :param files: Files of the message.
        :param embeds: List of embeds of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :param flags: Flags of the message.
        """
        pass

    def request_webhook_message(self, webhook_id, webhook_token, message_id):
        """
        Sends get webhook message request.

        :param webhook_id: ID of the webhook.
        :param webhook_token: Token of the webhook.
        :param message_id: ID of the message
        """
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}", "GET")

    @abstractmethod
    def edit_webhook_message(self,
                             webhook_id,
                             webhook_token,
                             message_id,
                             content: str = None,
                             embeds: typing.List[dict] = None,
                             files: typing.List[io.FileIO] = None,
                             allowed_mentions: dict = None,
                             attachments: typing.List[dict] = None):
        """
        Sends edit webhook message request.
        :param webhook_id: ID of the webhook.
        :param webhook_token: Token of the webhook.
        :param message_id: ID of the message to edit.
        :param content: Content of the message.
        :param embeds: List of embed of the message.
        :param files: Files of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :param attachments: Attachments to keep.
        """
        pass

    def delete_webhook_message(self, webhook_id, webhook_token, message_id):
        """
        Sends delete webhook message request.

        :param webhook_id: ID of the webhook.
        :param webhook_token: Token of the webhook.
        :param message_id: ID of the message to edit.
        """
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}", "DELETE")

    # Interaction Requests

    def request_application_commands(self, application_id, guild_id=None):
        """
        Sends get global or guild application commands request.

        :param application_id: ID of the application.
        :param guild_id: ID of the guild.
        """
        return self.request(f"/applications/{application_id}/"+(f"guilds/{guild_id}/commands" if guild_id else "commands"), "GET")

    def create_interaction_response(self, interaction_id, interaction_token, interaction_response: dict):
        """
        Sends create interaction response request.

        :param interaction_id: ID of the interaction.
        :param interaction_token: Token of the interaction.
        :param interaction_response: Interaction Response as dict.
        """
        return self.request(f"/interactions/{interaction_id}/{interaction_token}/callback", "POST", interaction_response, is_json=True)

    def request_original_interaction_response(self, application_id, interaction_token):
        """
        Sends get original interaction response request.

        :param application_id: ID of the application.
        :param interaction_token: Token of the interaction.
        """
        return self.request_webhook_message(application_id, interaction_token, "@original")

    def create_followup_message(self,
                                application_id,
                                interaction_token,
                                content: str = None,
                                username: str = None,
                                avatar_url: str = None,
                                tts: bool = False,
                                files: typing.List[io.FileIO] = None,
                                embeds: typing.List[dict] = None,
                                allowed_mentions: dict = None,
                                flags: int = None):
        """
        Sends create followup message request.

        :param application_id: ID of the application.
        :param interaction_token: Token of the interaction.
        :param content: Content of the message.
        :param username: Name of the webhook.
        :param avatar_url: URL of the avatar image.
        :param tts: Whether this message is TTS.
        :param files: Files of the message.
        :param embeds: List of embeds of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :param flags: Flags of the message.
        """
        return self.execute_webhook_with_files(application_id, interaction_token, None, None, content, username, avatar_url, tts, files, embeds, allowed_mentions, flags) if files \
            else self.execute_webhook(application_id, interaction_token, None, None, content, username, avatar_url, tts, embeds, allowed_mentions, flags)

    def edit_interaction_response(self,
                                  application_id,
                                  interaction_token,
                                  message_id="@original",
                                  content: str = None,
                                  embeds: typing.List[dict] = None,
                                  files: typing.List[io.FileIO] = None,
                                  allowed_mentions: dict = None,
                                  attachments: typing.List[dict] = None):
        """
        Sends edit interaction response request.

        :param application_id: ID of the application.
        :param interaction_token: Token of the interaction.
        :param message_id: ID of the message to edit.
        :param content: Content of the message.
        :param embeds: List of embed of the message.
        :param files: Files of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :param attachments: Attachments to keep.
        """
        return self.edit_webhook_message(application_id, interaction_token, message_id, content, embeds, files, allowed_mentions, attachments)

    @property
    def edit_followup_message(self):
        """Sends edit followup message request. Actually an alias of :meth:`.edit_interaction_response`."""
        return self.edit_interaction_response

    def delete_interaction_response(self, application_id, interaction_token, message_id="@original"):
        """
        Sends delete interaction response request.

        :param application_id: ID of the application.
        :param interaction_token: Token of the interaction.
        :param message_id: ID of the message to delete.
        """
        return self.delete_webhook_message(application_id, interaction_token, message_id)

    # Misc

    @abstractmethod
    def download(self, url):
        """
        Downloads file from passed url.

        :param url: URL to download.
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
