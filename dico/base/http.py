import io
import typing
import datetime
from abc import ABC, abstractmethod


class __EmptyObject:
    """An empty object. Can be used as an alternative of ``None``."""
    def __bool__(self) -> bool:
        return False

    def __len__(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "Empty"


EmptyObject: __EmptyObject = __EmptyObject()
_R = typing.Optional[typing.Union[dict, list, str, bytes]]
RESPONSE = typing.Union[_R, typing.Awaitable[_R]]


class HTTPRequestBase(ABC):
    """
    This abstract class includes all API request methods.

    .. note::
        - Although every GET route's name in the API Documents starts with ``Get ...``, but
          they are all changed to `request_...` to prevent confusion with cache get methods.

        - Part of interaction methods are merged to one, since those are listed as separate endpoint but only the difference is the ID.

    .. warning::
        This module isn't intended to be directly used. It is recommended to request via APIClient.
    """

    BASE_URL: str = "https://discord.com/api/v9"

    @abstractmethod
    def request(self, route: str, meth: str, body: typing.Any = None, *, is_json: bool = False, reason_header: str = None, retry: int = 3, **kwargs) -> RESPONSE:
        """
        This function includes requesting REST API.
        :return: Response.
        """
        pass

    # Audit Log Requests

    def request_guild_audit_log(self, guild_id, user_id: str = None, action_type: int = None, before: str = None, limit: int = None) -> RESPONSE:
        """
        Sends get guild audit log request.

        :param guild_id: ID of the guild to get audit log.
        :param user_id: ID of the user who did the action.
        :param action_type: Type of the action.
        :param before: Entry ID to get before.
        :param limit: Maximum number of the audit log to get.
        """
        params = {}
        if user_id is not None:
            params["user_id"] = user_id
        if action_type is not None:
            params["action_type"] = action_type
        if before is not None:
            params["before"] = before
        if limit is not None:
            params["limit"] = limit
        return self.request(f"/guilds/{guild_id}/audit-logs", "GET", params=params)

    # Channel Requests

    def request_channel(self, channel_id) -> RESPONSE:
        """
        Sends get channel request.

        :param channel_id: Channel ID to request.
        """
        return self.request(f"/channels/{channel_id}", "GET")

    def modify_guild_channel(self,
                             channel_id,
                             name: str = None,
                             channel_type: int = None,
                             position: int = EmptyObject,
                             topic: str = EmptyObject,
                             nsfw: bool = EmptyObject,
                             rate_limit_per_user: int = EmptyObject,
                             bitrate: int = EmptyObject,
                             user_limit: int = EmptyObject,
                             permission_overwrites: typing.List[dict] = EmptyObject,
                             parent_id: str = EmptyObject,
                             rtc_region: str = EmptyObject,
                             video_quality_mode: int = EmptyObject,
                             reason: str = None) -> RESPONSE:
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
        :param reason: Reason of the action.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if channel_type is not None:
            body["channel_type"] = channel_type
        if position is not EmptyObject:
            body["position"] = position
        if topic is not EmptyObject:
            body["topic"] = topic
        if nsfw is not EmptyObject:
            body["nsfw"] = nsfw
        if rate_limit_per_user is not EmptyObject:
            body["rate_limit_per_user"] = rate_limit_per_user
        if bitrate is not EmptyObject:
            body["bitrate"] = bitrate
        if user_limit is not EmptyObject:
            body["user_limit"] = user_limit
        if permission_overwrites is not EmptyObject:
            body["permission_overwrites"] = permission_overwrites
        if parent_id is not EmptyObject:
            body["parent_id"] = parent_id
        if rtc_region is not EmptyObject:
            body["rtc_region"] = rtc_region
        if video_quality_mode is not EmptyObject:
            body["video_quality_mode"] = video_quality_mode
        return self.request(f"/channels/{channel_id}", "PATCH", body, is_json=True, reason_header=reason)

    def modify_group_dm_channel(self, channel_id, name: str = None, icon: bin = None, reason: str = None) -> RESPONSE:
        """
        Sends modify channel request, for group DM.

        :param channel_id: Channel ID to request.
        :param name: Name to change.
        :param icon: base64 encoded icon.
        :param reason: Reason of the action.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if icon is not None:
            body["icon"] = icon
        return self.request(f"/channels/{channel_id}", "PATCH", body, is_json=True, reason_header=reason)

    def modify_thread_channel(self,
                              channel_id,
                              name: str = None,
                              archived: bool = None,
                              auto_archive_duration: int = None,
                              locked: bool = None,
                              rate_limit_per_user: int = EmptyObject,
                              reason: str = None) -> RESPONSE:
        """
        Sends modify channel request, for thread channel.

        :param channel_id: Channel ID to request.
        :param name: Name to change.
        :param archived: Whether to se the channel to archived.
        :param auto_archive_duration: Duration to automatically archive the channel.
        :param locked: Whether to lock the thread.
        :param rate_limit_per_user: Rate limit seconds of the thread.
        :param reason: Reason of the action.
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
        if rate_limit_per_user is not EmptyObject:
            body["rate_limit_per_user"] = rate_limit_per_user
        return self.request(f"/channels/{channel_id}", "PATCH", body, is_json=True, reason_header=reason)

    def delete_channel(self, channel_id, reason: str = None) -> RESPONSE:
        """
        Sends channel delete/close request.

        :param channel_id: Channel ID to request.
        :param reason: Reason of the action.
        """
        return self.request(f"/channels/{channel_id}", "DELETE", reason_header=reason)

    @property
    def close_channel(self):
        """Alias of :meth:`.delete_channel`."""
        return self.delete_channel

    def request_channel_messages(self, channel_id, around=None, before=None, after=None, limit: int = None) -> RESPONSE:
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

    def request_channel_message(self, channel_id, message_id) -> RESPONSE:
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
                       embeds: typing.List[dict] = None,
                       allowed_mentions: dict = None,
                       message_reference: dict = None,
                       components: typing.List[dict] = None,
                       sticker_ids: typing.List[str] = None) -> RESPONSE:
        """
        Sends create message request.

        :param channel_id: ID of the channel.
        :param content: Content of the message.
        :param nonce:
        :param tts: Whether this message is TTS.
        :param embeds: List of embeds of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :param message_reference: Message to reference.
        :param components: Components of the message.
        :param sticker_ids: List of ID of the stickers.
        """
        if not (content or embeds or sticker_ids):
            raise ValueError("either content or embed or sticker_ids must be passed.")
        body = {}
        if content is not None:
            body["content"] = content
        if embeds is not None:
            body["embeds"] = embeds
        if nonce is not None:
            body["nonce"] = nonce
        if tts is not None:
            body["tts"] = tts
        if allowed_mentions is not None:
            body["allowed_mentions"] = allowed_mentions
        if message_reference is not None:
            body["message_reference"] = message_reference
        if components is not None:
            body["components"] = components
        if sticker_ids is not None:
            body["sticker_ids"] = sticker_ids
        return self.request(f"/channels/{channel_id}/messages", "POST", body, is_json=True)

    @abstractmethod
    def create_message_with_files(self,
                                  channel_id,
                                  content: str = None,
                                  files: typing.List[io.FileIO] = None,
                                  nonce: typing.Union[int, str] = None,
                                  tts: bool = None,
                                  embeds: typing.List[dict] = None,
                                  allowed_mentions: dict = None,
                                  message_reference: dict = None,
                                  components: typing.List[dict] = None,
                                  sticker_ids: typing.List[str] = None,
                                  attachments: typing.List[dict] = None) -> RESPONSE:
        """
        Sends create message request with files.

        :param channel_id: ID of the channel.
        :param content: Content of the message.
        :param files: Files of the message.
        :param nonce:
        :param tts: Whether this message is TTS.
        :param embeds: List of embeds of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :param message_reference: Message to reference.
        :param components: Components of the message.
        :param sticker_ids: List of ID of the stickers.
        :param attachments: List of attachment objects.
        """
        pass

    def crosspost_message(self, channel_id, message_id) -> RESPONSE:
        """
        Sends crosspost message request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to crosspost.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}/crosspost", "POST")

    def create_reaction(self, channel_id, message_id, emoji: str) -> RESPONSE:
        """
        Sends create reaction request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to react.
        :param emoji: Emoji to add.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me", "PUT")

    def delete_reaction(self, channel_id, message_id, emoji: str, user_id="@me") -> RESPONSE:
        """
        Sends delete reaction request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to request.
        :param emoji: Emoji to delete.
        :param user_id: User ID to delete reaction. Pass ``@me`` to remove own.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}", "DELETE")

    def request_reactions(self, channel_id, message_id, emoji: str, after=None, limit=None) -> RESPONSE:
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

    def delete_all_reactions(self, channel_id, message_id) -> RESPONSE:
        """
        Sends delete all reactions request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to request.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}/reactions", "DELETE")

    def delete_all_reactions_emoji(self, channel_id, message_id, emoji: str) -> RESPONSE:
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
                     content: str = EmptyObject,
                     embeds: typing.List[dict] = EmptyObject,
                     flags: int = EmptyObject,
                     allowed_mentions: dict = EmptyObject,
                     attachments: typing.List[dict] = EmptyObject,
                     components: typing.List[dict] = EmptyObject) -> RESPONSE:
        """
        Sends edit message request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to edit.
        :param content: Content of the message.
        :param embeds: List of embeds of the message.
        :param flags: Flags of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :param attachments: Attachments to keep.
        :param components: Components of the message.
        :return: Message object dict.
        """
        body = {}
        if content is not EmptyObject:
            body["content"] = content
        if embeds is not EmptyObject:
            body["embeds"] = embeds
        if flags is not EmptyObject:
            body["flags"] = flags
        if allowed_mentions is not EmptyObject:
            body["allowed_mentions"] = allowed_mentions
        if attachments is not EmptyObject:
            body["attachments"] = attachments
        if components is not EmptyObject:
            body["components"] = components
        return self.request(f"/channels/{channel_id}/messages/{message_id}", "PATCH", body, is_json=True)

    @abstractmethod
    def edit_message_with_files(self,
                                channel_id,
                                message_id,
                                content: str = EmptyObject,
                                embeds: typing.List[dict] = EmptyObject,
                                flags: int = EmptyObject,
                                files: typing.List[io.FileIO] = EmptyObject,
                                allowed_mentions: dict = EmptyObject,
                                attachments: typing.List[dict] = EmptyObject,
                                components: typing.List[dict] = EmptyObject) -> RESPONSE:
        """
        Sends edit message request with files.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to edit.
        :param content: Content of the message.
        :param embeds: List of embeds of the message.
        :param flags: Flags of the message.
        :param files: Files of the message.
        :param allowed_mentions: Allowed mentions of the message.
        :param attachments: Attachments to keep.
        :param components: Components of the message.
        :return: Message object dict.
        """
        pass

    def delete_message(self, channel_id, message_id, reason: str = None) -> RESPONSE:
        """
        Sends delete message request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to edit.
        :param reason: Reason of the action.
        """
        return self.request(f"/channels/{channel_id}/messages/{message_id}", "DELETE", reason_header=reason)

    def bulk_delete_messages(self, channel_id, message_ids: typing.List[typing.Union[int, str]], reason: str = None) -> RESPONSE:
        """
        Sends bulk delete message request.

        :param channel_id: ID of the channel.
        :param message_ids: List of the message IDs to delete.
        :param reason: Reason of the action.
        """
        body = {"messages": list(map(str, message_ids))}
        return self.request(f"/channels/{channel_id}/messages/bulk-delete", "POST", body, is_json=True, reason_header=reason)

    def edit_channel_permissions(self, channel_id, overwrite_id, allow: str, deny: str, overwrite_type: int, reason: str = None) -> RESPONSE:
        """
        Sends edit channel permissions request.

        :param channel_id: ID of the channel.
        :param overwrite_id: Role or Member ID to edit permissions.
        :param allow: What permissions to allow.
        :param deny: What permissions to deny.
        :param overwrite_type: Type of the overwrite target. Set to 0 for Role, and 1 for Member.
        :param reason: Reason of the action.
        """
        body = {"allow": allow, "deny": deny, "type": overwrite_type}
        return self.request(f"/channels/{channel_id}/permissions/{overwrite_id}", "PUT", body, is_json=True, reason_header=reason)

    def request_channel_invites(self, channel_id) -> RESPONSE:
        """
        Sends get channel invites request.

        :param channel_id: ID of the channel.
        """
        return self.request(f"/channels/{channel_id}/invites", "GET")

    def create_channel_invite(self,
                              channel_id,
                              max_age: int = None,
                              max_uses: int = None,
                              temporary: bool = None,
                              unique: bool = None,
                              target_type: int = None,
                              target_user_id: str = None,
                              target_application_id: str = None,
                              reason: str = None) -> RESPONSE:
        """
        Sends create channel invite request.

        :param channel_id: ID of the channel.
        :param max_age: Maximum age in seconds.
        :param max_uses: Maximum uses.
        :param temporary: Whether the invite only grants temporary membership.
        :param unique: Whether the invite is unique.
        :param target_type: Type of the invite.
        :param target_user_id: User ID to target to.
        :param target_application_id: Application ID to target to.
        :param reason: Reason of the action.
        """
        body = {}
        if max_age is not None:
            body["max_ages"] = max_age
        if max_uses is not None:
            body["max_uses"] = max_uses
        if temporary is not None:
            body["temporary"] = temporary
        if unique is not None:
            body["unique"] = unique
        if target_type is not None:
            body["target_type"] = target_type
        if target_user_id is not None:
            body["target_user_id"] = target_user_id
        if target_application_id is not None:
            body["target_application_id"] = target_application_id
        return self.request(f"/channels/{channel_id}/invites", "POST", body, is_json=True, reason_header=reason)

    def delete_channel_permission(self, channel_id, overwrite_id, reason: str = None) -> RESPONSE:
        """
        Sends delete channel permissions request.

        :param channel_id: ID of the channel.
        :param overwrite_id: ID of the target user/role.
        :param reason: Reason of the action.
        """
        return self.request(f"/channels/{channel_id}/permissions/{overwrite_id}", "DELETE", reason_header=reason)

    def follow_news_channel(self, channel_id, webhook_channel_id) -> RESPONSE:
        """
        Sends follow news channel request.

        :param channel_id: ID of the channel to follow.
        :param webhook_channel_id: Target channel ID.
        """
        return self.request(f"/channels/{channel_id}/followers", "POST", {"webhook_channel_id": webhook_channel_id}, is_json=True)

    def trigger_typing_indicator(self, channel_id) -> RESPONSE:
        """
        Sends trigger typing indicator request.

        :param channel_id: ID of the channel.
        """
        return self.request(f"/channels/{channel_id}/typing", "POST")

    def request_pinned_messages(self, channel_id) -> RESPONSE:
        """
        Sends get pinned messages request.

        :param channel_id: ID of the channel.
        """
        return self.request(f"/channels/{channel_id}/pins", "GET")

    def pin_message(self, channel_id, message_id, reason: str = None) -> RESPONSE:
        """
        Sends pin message request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to pin.
        :param reason: Reason of the action.
        """
        return self.request(f"/channels/{channel_id}/pins/{message_id}", "PUT", reason_header=reason)

    def unpin_message(self, channel_id, message_id, reason: str = None) -> RESPONSE:
        """
        Sends unpin message request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to unpin.
        :param reason: Reason of the action.
        """
        return self.request(f"/channels/{channel_id}/pins/{message_id}", "DELETE", reason_header=reason)

    def group_dm_add_recipient(self, channel_id, user_id, access_token: str, nick: str) -> RESPONSE:
        """
        Sends group dm add recipient request.

        :param channel_id: ID of the group dm channel.
        :param user_id: ID of the user to add.
        :param access_token: Access token.
        :param nick: Nickname of the user.
        """
        body = {"access_token": access_token, "nick": nick}
        return self.request(f"/channels/{channel_id}/recipients/{user_id}", "PUT", body, is_json=True)

    def group_dm_remove_recipient(self, channel_id, user_id) -> RESPONSE:
        """
        Sends group dm remove recipient request.

        :param channel_id: ID of the group dm channel.
        :param user_id: ID of the user to remove.
        """
        return self.request(f"/channels/{channel_id}/recipients/{user_id}", "DELETE")

    def start_thread_with_message(self, channel_id, message_id, name: str, auto_archive_duration: int, reason: str = None) -> RESPONSE:
        """
        Sends start thread with message request.

        :param channel_id: ID of the channel.
        :param message_id: ID of the message to create thread.
        :param name: Name of the thread channel.
        :param auto_archive_duration: Duration in minute to automatically close after recent activity.
        :param reason: Reason of the action.
        """
        body = {"name": name, "auto_archive_duration": auto_archive_duration}
        return self.request(f"/channels/{channel_id}/messages/{message_id}/threads", "POST", body, is_json=True, reason_header=reason)

    def start_thread_without_message(self, channel_id, name: str, auto_archive_duration: int, thread_type: int = None, invitable: bool = None, reason: str = None) -> RESPONSE:
        """
        Sends start thread without message request.

        :param channel_id: ID of the channel to create thread.
        :param name: Name of the thread channel.
        :param auto_archive_duration: Duration in minute to automatically close after recent activity.
        :param thread_type: Type of the thread.
        :param invitable: Whether this thread is invitable.
        :param reason: Reason of the action.
        """
        body = {"name": name, "auto_archive_duration": auto_archive_duration}
        if thread_type is not None:
            body["type"] = thread_type
        if invitable is not None:
            body["invitable"] = invitable
        return self.request(f"/channels/{channel_id}/threads", "POST", body, is_json=True, reason_header=reason)

    def join_thread(self, channel_id) -> RESPONSE:
        """
        Sends join thread request.

        :param channel_id: ID of the thread channel to join.
        """
        return self.request(f"/channels/{channel_id}/thread-members/@me", "PUT")

    def add_thread_member(self, channel_id, user_id) -> RESPONSE:
        """
        Sends add thread member request.

        :param channel_id: ID of the thread channel.
        :param user_id: ID of the user to add.
        """
        return self.request(f"/channels/{channel_id}/thread-members/{user_id}", "PUT")

    def leave_thread(self, channel_id) -> RESPONSE:
        """
        Sends leave thread request.

        :param channel_id: ID of the thread channel to leave.
        """
        return self.request(f"/channels/{channel_id}/thread-members/@me", "DELETE")

    def remove_thread_member(self, channel_id, user_id) -> RESPONSE:
        """
        Sends remove thread member request.

        :param channel_id: ID of the thread channel.
        :param user_id: ID of the user to remove.
        """
        return self.request(f"/channels/{channel_id}/thread-members/{user_id}", "DELETE")

    def list_thread_members(self, channel_id) -> RESPONSE:
        """
        Sends list thread members request.

        :param channel_id: ID of the thread channel.
        """
        return self.request(f"/channels/{channel_id}/thread-members", "GET")

    def list_active_threads(self, channel_id) -> RESPONSE:
        """
        Sends list active threads request.

        :param channel_id: ID of the channel.
        """
        return self.request(f"/channels/{channel_id}/threads/active", "GET")

    def list_public_archived_threads(self, channel_id, before: typing.Union[str, datetime.datetime] = None, limit: int = None) -> RESPONSE:
        """
        Sends list public archived threads request.

        :param channel_id: ID of the channel.
        :param before: ISO8601 timestamp to get threads before this.
        :param limit: Limit to return.
        """
        params = {}
        if before is not None:
            params["before"] = str(before)
        if limit is not None:
            params["limit"] = limit
        return self.request(f"/channels/{channel_id}/threads/archived/public", "GET", params=params)

    def list_private_archived_threads(self, channel_id, before: typing.Union[str, datetime.datetime] = None, limit: int = None) -> RESPONSE:
        """
        Sends list private archived threads request.

        :param channel_id: ID of the channel.
        :param before: ISO8601 timestamp to get threads before this.
        :param limit: Limit to return.
        """
        params = {}
        if before is not None:
            params["before"] = str(before)
        if limit is not None:
            params["limit"] = limit
        return self.request(f"/channels/{channel_id}/threads/archived/private", "GET", params=params)

    def list_joined_private_archived_threads(self, channel_id, before: typing.Union[str, datetime.datetime] = None, limit: int = None) -> RESPONSE:
        """
        Sends list joined private archived threads request.

        :param channel_id: ID of the channel.
        :param before: ISO8601 timestamp to get threads before this.
        :param limit: Limit to return.
        """
        params = {}
        if before is not None:
            params["before"] = str(before)
        if limit is not None:
            params["limit"] = limit
        return self.request(f"/channels/{channel_id}/users/@me/threads/archived/private", "GET", params=params)

    # Emoji Requests

    def list_guild_emojis(self, guild_id) -> RESPONSE:
        """
        Sends list guild emojis request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/emojis", "GET")

    def request_guild_emoji(self, guild_id, emoji_id) -> RESPONSE:
        """
        Sends get guild emoji request.

        :param guild_id: ID of the guild.
        :param emoji_id: ID of the emoji to request.
        """
        return self.request(f"/guilds/{guild_id}/emojis/{emoji_id}", "GET")

    def create_guild_emoji(self, guild_id, name: str, image: str, roles: typing.List[str], reason: str = None) -> RESPONSE:
        """
        Sends create guild emoji request.

        :param guild_id: ID of the guild.
        :param name: Name of the emoji.
        :param image: Image data of the emoji.
        :param roles: Roles that are allowed to use this emoji.
        :param reason: Reason of the action.
        """
        body = {"name": name, "image": image, "roles": roles}
        return self.request(f"/guilds/{guild_id}/emojis", "POST", body, is_json=True, reason_header=reason)

    def modify_guild_emoji(self, guild_id, emoji_id, name: str = EmptyObject, roles: typing.List[str] = EmptyObject, reason: str = None) -> RESPONSE:
        """
        Sends modify guild emoji request.

        :param guild_id: ID of the guild.
        :param emoji_id: ID of the emoji.
        :param name: Name of the emoji to change.
        :param roles: Roles to change.
        :param reason: Reason of the action.
        """
        body = {}
        if name is not EmptyObject:
            body["name"] = name
        if roles is not EmptyObject:
            body["roles"] = roles
        return self.request(f"/guilds/{guild_id}/emojis/{emoji_id}", "PATCH", body, is_json=True, reason_header=reason)

    def delete_guild_emoji(self, guild_id, emoji_id, reason: str = None) -> RESPONSE:
        """
        Sends delete guild emoji request.

        :param guild_id: ID of the guild.
        :param emoji_id: ID of the emoji to delete.
        :param reason: Reason of the action.
        """
        return self.request(f"/guilds/{guild_id}/emojis/{emoji_id}", "DELETE", reason_header=reason)

    # Guild Requests

    def create_guild(self,
                     name: str,
                     icon: str = None,
                     verification_level: int = None,
                     default_message_notifications: int = None,
                     explicit_content_filter: int = None,
                     roles: typing.List[dict] = None,
                     channels: typing.List[dict] = None,
                     afk_channel_id: str = None,
                     afk_timeout: int = None,
                     system_channel_id: str = None,
                     system_channel_flags: int = None) -> RESPONSE:
        """
        Sends create guild request.

        .. note::
            Param ``region`` is not supported since it is deprecated.

        :param name: Name of the guild.
        :param icon: Icon data of the guild to create.
        :param verification_level: Verification level of the guild to create.
        :param default_message_notifications: Default message notification level of the guild to create.
        :param explicit_content_filter: Explicit content filter level of the guild to create.
        :param roles: Roles of the guild to create.
        :param channels: Channels of the guild to create.
        :param afk_channel_id: AFK channel ID of the guild to create.
        :param afk_timeout: AFK timeout of the guild to create.
        :param system_channel_id: System channel ID of the guild to create.
        :param system_channel_flags: System channel flags of the guild to create.
        """
        body = {"name": name}
        if icon is not None:
            body["icon"] = icon
        if verification_level is not None:
            body["verification_level"] = verification_level
        if default_message_notifications is not None:
            body["default_message_notifications"] = default_message_notifications
        if explicit_content_filter is not None:
            body["explicit_content_filter"] = explicit_content_filter
        if roles is not None:
            body["roles"] = roles
        if channels is not None:
            body["channels"] = channels
        if afk_channel_id is not None:
            body["afk_channel_id"] = afk_channel_id
        if afk_timeout is not None:
            body["afk_timeout"] = afk_timeout
        if system_channel_id is not None:
            body["system_channel_id"] = system_channel_id
        if system_channel_flags is not None:
            body["system_channel_flags"] = system_channel_flags
        return self.request("/guilds", "POST", body, is_json=True)

    def request_guild(self, guild_id, with_counts: bool = False) -> RESPONSE:
        """
        Sends get guild request.

        :param guild_id: ID of the guild to request.
        :param with_counts: Whether to return member and presence count.
        """
        return self.request(f"/guilds/{guild_id}", "GET", params={"with_counts": "true" if with_counts else "false"})

    def request_guild_preview(self, guild_id) -> RESPONSE:
        """
        Sends get guild request.

        :param guild_id: ID of the guild to request.
        """
        return self.request(f"/guilds/{guild_id}/preview", "GET")

    def modify_guild(self,
                     guild_id,
                     name: str = None,
                     verification_level: int = EmptyObject,
                     default_message_notifications: int = EmptyObject,
                     explicit_content_filter: int = EmptyObject,
                     afk_channel_id: str = EmptyObject,
                     afk_timeout: int = None,
                     icon: str = EmptyObject,
                     owner_id: str = None,
                     splash: str = EmptyObject,
                     discovery_splash: str = EmptyObject,
                     banner: str = EmptyObject,
                     system_channel_id: str = EmptyObject,
                     system_channel_flags: int = None,
                     rules_channel_id: str = EmptyObject,
                     public_updates_channel_id: str = EmptyObject,
                     preferred_locale: str = EmptyObject,
                     features: typing.List[str] = None,
                     description: str = EmptyObject,
                     reason: str = None) -> RESPONSE:
        """
        Sends create guild request.

        .. note::
            Param ``region`` is not supported since it is deprecated.

        :param guild_id: ID of the guild to modify.
        :param name: Name of the guild.
        :param verification_level: Verification level.
        :param default_message_notifications: Default message notification level.
        :param explicit_content_filter: Explicit content filter level.
        :param afk_channel_id: AFK channel ID.
        :param afk_timeout: AFK timeout.
        :param icon: Icon image data.
        :param owner_id: ID of the owner. Bot must be owner of the guild.
        :param splash: Splash image data.
        :param discovery_splash: Discovery splash image data.
        :param banner: Banner image data.
        :param system_channel_id: System channel ID.
        :param system_channel_flags: System channel flags.
        :param rules_channel_id: Rules channel ID.
        :param public_updates_channel_id: Discord community notes receive channel ID.
        :param preferred_locale: Preferred locale of the guild.
        :param features: Enabled guild features list.
        :param description: Description of the guild.
        :param reason: Reason of the action.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if verification_level is not None:
            body["verification_level"] = verification_level
        if default_message_notifications is not None:
            body["default_message_notifications"] = default_message_notifications
        if explicit_content_filter is not None:
            body["explicit_content_filter"] = explicit_content_filter
        if afk_channel_id is not None:
            body["afk_channel_id"] = afk_channel_id
        if afk_timeout is not None:
            body["afk_timeout"] = afk_timeout
        if icon is not None:
            body["icon"] = icon
        if owner_id is not None:
            body["owner_id"] = owner_id
        if splash is not None:
            body["splash"] = splash
        if discovery_splash is not None:
            body["discovery_splash"] = discovery_splash
        if banner is not None:
            body["banner"] = banner
        if system_channel_id is not None:
            body["system_channel_id"] = system_channel_id
        if system_channel_flags is not None:
            body["system_channel_flags"] = system_channel_flags
        if rules_channel_id is not None:
            body["rules_channel_id"] = rules_channel_id
        if public_updates_channel_id is not None:
            body["public_updates_channel_id"] = public_updates_channel_id
        if preferred_locale is not None:
            body["preferred_locale"] = preferred_locale
        if features is not None:
            body["features"] = features
        if description is not None:
            body["description"] = description
        return self.request(f"/guilds/{guild_id}", "PATCH", body, is_json=True, reason_header=reason)

    def delete_guild(self, guild_id) -> RESPONSE:
        """
        Sends delete guild request. Bot must be owner of the guild.

        :param guild_id: ID of the guild to delete.
        """
        return self.request(f"/guilds/{guild_id}", "DELETE")

    def request_guild_channels(self, guild_id) -> RESPONSE:
        """
        Sends get guild channels request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/channels", "GET")

    def create_guild_channel(self,
                             guild_id,
                             name: str,
                             channel_type: int = None,
                             topic: str = None,
                             bitrate: int = None,
                             user_limit: int = None,
                             rate_limit_per_user: int = None,
                             position: int = None,
                             permission_overwrites: typing.List[dict] = None,
                             parent_id: str = None,
                             nsfw: bool = None,
                             reason: str = None) -> RESPONSE:
        """
        Sends create guild channel request.

        :param guild_id: ID of the guild.
        :param name: Name of the channel to create.
        :param channel_type: Type of the channel.
        :param topic: Topic of the channel.
        :param bitrate: Bitrate of the channel.
        :param user_limit: User limit of the channel.
        :param rate_limit_per_user: Rate limit per user of the channel.
        :param position: Position of the channel.
        :param permission_overwrites: Permission overwrites of the channel.
        :param parent_id: Parent ID of the channel.
        :param nsfw: Whether this channel is NSFW.
        :param reason: Reason of the action.
        """
        body = {"name": name}
        if channel_type is not None:
            body["channel_type"] = channel_type
        if topic is not None:
            body["topic"] = topic
        if bitrate is not None:
            body["bitrate"] = bitrate
        if user_limit is not None:
            body["user_limit"] = user_limit
        if rate_limit_per_user is not None:
            body["rate_limit_per_user"] = rate_limit_per_user
        if position is not None:
            body["position"] = position
        if permission_overwrites is not None:
            body["permission_overwrites"] = permission_overwrites
        if parent_id is not None:
            body["parent_id"] = parent_id
        if nsfw is not None:
            body["nsfw"] = nsfw
        return self.request(f"/guilds/{guild_id}/channels", "POST", body, is_json=True, reason_header=reason)

    def modify_guild_channel_positions(self, guild_id, params: typing.List[dict], reason: str = None) -> RESPONSE:
        """
        Sends modify guild channel positions request.

        :param guild_id: ID of the guild.
        :param params: List of channel params to modify.
        :param reason: Reason of the action.
        """
        return self.request(f"/guilds/{guild_id}/channels", "PATCH", params, is_json=True, reason_header=reason)

    def list_active_threads_as_guild(self, guild_id) -> RESPONSE:
        """
        Sends list active threads request but with guild id.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/threads/active", "GET")

    def request_guild_member(self, guild_id, user_id) -> RESPONSE:
        """
        Sends get guild member request.

        :param guild_id: ID of the guild.
        :param user_id: ID of the user to request.
        """
        return self.request(f"/guilds/{guild_id}/members/{user_id}", "GET")

    def list_guild_members(self, guild_id, limit: int = None, after: str = None) -> RESPONSE:
        """
        Sends list guild members request.

        :param guild_id: ID of the guild.
        :param limit: Limit of the member count to get.
        :param after: The highest user ID in the previous page.
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if after is not None:
            params["after"] = after
        return self.request(f"/guilds/{guild_id}/members", "GET", params=params)

    def search_guild_members(self, guild_id, query: str, limit: int = None) -> RESPONSE:
        """
        Sends search guild members request.

        :param guild_id: ID of the guild.
        :param query: Query matching to usernames or nicknames to search.
        :param limit: Limit of the member count to get.
        """
        params = {"query": query}
        if limit is not None:
            params["limit"] = limit
        return self.request(f"/guilds/{guild_id}/members/search", "GET", params=params)

    def add_guild_member(self, guild_id, user_id, access_token: str, nick: str = None, roles: typing.List[str] = None, mute: bool = None, deaf: bool = None) -> RESPONSE:
        """
        Sends add guild member request.

        .. note::
            This requires OAuth2 access token with ``guilds.join`` scope.

        :param guild_id: ID of the guild.
        :param user_id: ID of the user to add.
        :param access_token: OAuth2 access token with ``guilds.join`` scope.
        :param nick: Nickname to set.
        :param roles: Roles to add. Using this will bypass membership screening.
        :param mute: Whether to mute this user in voice channel.
        :param deaf: Whether to deaf this user in voice channel.
        """
        body = {"access_token": access_token}
        if nick is not None:
            body["nick"] = nick
        if roles is not None:
            body["roles"] = roles
        if mute is not None:
            body["mute"] = mute
        if deaf is not None:
            body["deaf"] = deaf
        return self.request(f"/guilds/{guild_id}/members/{user_id}", "PUT", body, is_json=True)

    def modify_guild_member(self,
                            guild_id,
                            user_id,
                            nick: str = EmptyObject,
                            roles: typing.List[str] = EmptyObject,
                            mute: bool = EmptyObject,
                            deaf: bool = EmptyObject,
                            channel_id: str = EmptyObject,
                            reason: str = None) -> RESPONSE:
        """
        Sends modify guild member request.

        .. note::
           ``None`` can be used for all params.

        :param guild_id: ID of the guild.
        :param user_id: ID of the user to edit.
        :param nick: Nickname to change.
        :param roles: Roles to assign.
        :param mute: Whether to mute this user in voice channel.
        :param deaf: Whether to deaf this user in voice channel.
        :param channel_id: Voice channel to move.
        :param reason: Reason of the action.
        """
        body = {}
        if nick is not EmptyObject:
            body["nick"] = nick
        if roles is not EmptyObject:
            body["roles"] = roles
        if mute is not EmptyObject:
            body["mute"] = mute
        if deaf is not EmptyObject:
            body["deaf"] = deaf
        if channel_id is not EmptyObject:
            body["channel_id"] = channel_id
        return self.request(f"/guilds/{guild_id}/members/{user_id}", "PATCH", body, is_json=True, reason_header=reason)

    def modify_current_user_nick(self, guild_id, nick: typing.Union[str, None] = EmptyObject, reason: str = None) -> RESPONSE:
        """
        Sends modify current user nick request.

        :param guild_id: ID of the guild.
        :param nick: Nickname to change.
        :param reason: Reason of the action.
        """
        body = {}
        if nick is not EmptyObject:
            body["nick"] = nick
        return self.request(f"/guilds/{guild_id}/members/@me/nick", "PATCH", body, is_json=True, reason_header=reason)

    def add_guild_member_role(self, guild_id, user_id, role_id, reason: str = None) -> RESPONSE:
        """
        Sends add guild member role request.

        :param guild_id: ID of the guild.
        :param user_id: ID of the user.
        :param role_id: ID of the role to add.
        :param reason: Reason of the action.
        """
        return self.request(f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}", "PUT", reason_header=reason)

    def remove_guild_member_role(self, guild_id, user_id, role_id, reason: str = None) -> RESPONSE:
        """
        Sends remove guild member role request.

        :param guild_id: ID of the guild.
        :param user_id: ID of the user.
        :param role_id: ID of the role to remove.
        :param reason: Reason of the action.
        """
        return self.request(f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}", "DELETE", reason_header=reason)

    def remove_guild_member(self, guild_id, user_id) -> RESPONSE:
        """
        Sends remove guild member request.

        :param guild_id: ID of the guild.
        :param user_id: ID of the user to remove.
        """
        return self.request(f"/guilds/{guild_id}/members/{user_id}", "DELETE")

    def request_guild_bans(self, guild_id) -> RESPONSE:
        """
        Sends get guild bans request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/bans", "GET")

    def request_guild_ban(self, guild_id, user_id) -> RESPONSE:
        """
        Sends get guild ban request.

        :param guild_id: ID of the guild.
        :param user_id: ID of the user.
        """
        return self.request(f"/guilds/{guild_id}/bans/{user_id}", "GET")

    def create_guild_ban(self, guild_id, user_id, delete_message_days: int = None, reason: str = None) -> RESPONSE:
        """
        Sends create guild ban request.

        :param guild_id: ID of the guild.
        :param user_id: ID of the user to ban.
        :param delete_message_days: Days of message sent by banned user to delete.
        :param reason: Reason of the action.
        """
        body = {}
        if delete_message_days is not None:
            body["delete_message_days"] = delete_message_days
        return self.request(f"/guilds/{guild_id}/bans/{user_id}", "PUT", body, is_json=True, reason_header=reason)

    def remove_guild_ban(self, guild_id, user_id, reason: str = None) -> RESPONSE:
        """
        Sends remove guild ban request.

        :param guild_id: ID of the guild.
        :param user_id: ID of the user tom remove ban.
        :param reason: Reason of the action.
        """
        return self.request(f"/guilds/{guild_id}/bans/{user_id}", "DELETE", reason_header=reason)

    def request_guild_roles(self, guild_id) -> RESPONSE:
        """
        Sends get guild roles request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/roles", "GET")

    def create_guild_role(self, guild_id, name: str = None, permissions: str = None, color: int = None, hoist: bool = None, mentionable: bool = None, reason: str = None) -> RESPONSE:
        """
        Sends create guild role request.

        :param guild_id: ID of the guild.
        :param name: Name of the role.
        :param permissions: Permissions of the role.
        :param color: Color of the role.
        :param hoist: Whether role should be displayed separately.
        :param mentionable: Whether the role is mentionable.
        :param reason: Reason of the action.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if permissions is not None:
            body["permissions"] = permissions
        if color is not None:
            body["color"] = color
        if hoist is not None:
            body["hoist"] = hoist
        if mentionable is not None:
            body["mentionable"] = mentionable
        return self.request(f"/guilds/{guild_id}/roles", "POST", body, is_json=True, reason_header=reason)

    def modify_guild_role_positions(self, guild_id, params: typing.List[dict], reason: str = None) -> RESPONSE:
        """
        Sends modify guild role positions request.

        :param guild_id: ID of the guild.
        :param params: List of ``{"id": role ID, "position": position}``.
        :param reason: Reason of the action.
        """
        return self.request(f"/guilds/{guild_id}/roles", "PATCH", params, is_json=True, reason_header=reason)

    def modify_guild_role(self,
                          guild_id,
                          role_id,
                          name: str = EmptyObject,
                          permissions: str = EmptyObject,
                          color: int = EmptyObject,
                          hoist: bool = EmptyObject,
                          mentionable: bool = EmptyObject,
                          reason: str = None) -> RESPONSE:
        """
        Sends modify guild role request.

        :param guild_id: ID of the guild.
        :param role_id: ID of the role to modify.
        :param name: Name of the role.
        :param permissions: Permissions of the role.
        :param color: Color of the role.
        :param hoist: Whether role should be displayed separately.
        :param mentionable: Whether the role is mentionable.
        :param reason: Reason of the action.
        """
        body = {}
        if name is not EmptyObject:
            body["name"] = name
        if permissions is not EmptyObject:
            body["permissions"] = permissions
        if color is not EmptyObject:
            body["color"] = color
        if hoist is not EmptyObject:
            body["hoist"] = hoist
        if mentionable is not EmptyObject:
            body["mentionable"] = mentionable
        return self.request(f"/guilds/{guild_id}/roles/{role_id}", "PATCH", body, is_json=True, reason_header=reason)

    def delete_guild_role(self, guild_id, role_id, reason: str = None) -> RESPONSE:
        """
        Sends delete guild role request.

        :param guild_id: ID of the guild.
        :param role_id: ID of the role to delete.
        :param reason: Reason of the action.
        """
        return self.request(f"/guilds/{guild_id}/roles/{role_id}", "DELETE", reason_header=reason)

    def request_guild_prune_count(self, guild_id, days: int = None, include_roles: typing.List[str] = None) -> RESPONSE:
        """
        Sends get guild prune count request.

        :param guild_id: ID of the guild.
        :param days: Days to count prune.
        :param include_roles: Roles to include.
        :return:
        """
        params = {}
        if days is not None:
            params["days"] = days
        if include_roles is not None:
            params["include_roles"] = ','.join(include_roles)
        return self.request(f"/guilds/{guild_id}/prune", "GET", params=params)

    def begin_guild_prune(self, guild_id, days: int = None, compute_prune_count: bool = None, include_roles: typing.List[str] = None, reason: str = None) -> RESPONSE:
        """
        Sends begin guild prune request.

        :param guild_id: ID of the guild.
        :param days: Days to prune.
        :param compute_prune_count: Whether to return ``pruned``.
        :param include_roles: Roles to include.
        :param reason: Reason of the action.
        """
        body = {}
        if days is not None:
            body["days"] = days
        if compute_prune_count is not None:
            body["compute_prune_count"] = compute_prune_count
        if include_roles is not None:
            body["include_roles"] = include_roles
        return self.request(f"/guilds/{guild_id}/prune", "POST", body, reason_header=reason)

    def request_guild_voice_regions(self, guild_id) -> RESPONSE:
        """
        Sends get guild voice regions request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/regions", "GET")

    def request_guild_invites(self, guild_id) -> RESPONSE:
        """
        Sends get guild invites request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/invites", "GET")

    def request_guild_integrations(self, guild_id) -> RESPONSE:
        """
        Sends get guild integrations request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/integrations", "GET")

    def delete_guild_integration(self, guild_id, integration_id, reason: str = None) -> RESPONSE:
        """
        Sends delete guild integration request.

        :param guild_id: ID of the guild.
        :param integration_id: ID of the integration to delete.
        :param reason: Reason of the action.
        """
        return self.request(f"/guilds/{guild_id}/integrations/{integration_id}", "DELETE", reason_header=reason)

    def request_guild_widget_settings(self, guild_id) -> RESPONSE:
        """
        Sends get guild widget settings request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/widget", "GET")

    def modify_guild_widget(self, guild_id, enabled: bool = None, channel_id: str = EmptyObject, reason: str = None) -> RESPONSE:
        """
        Sends modify guild widget request.

        :param guild_id: ID of the guild.
        :param enabled: Whether the widget is enabled.
        :param channel_id: ID of the channel for the widget.
        :param reason: Reason of the action.
        """
        body = {}
        if enabled is not None:
            body["enabled"] = enabled
        if channel_id is not EmptyObject:
            body["channel_id"] = channel_id
        return self.request(f"/guilds/{guild_id}/widget", "PATCH", body, is_json=True, reason_header=reason)

    def request_guild_widget(self, guild_id) -> RESPONSE:
        """
        Sends get guild widget request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/widget.json", "GET")

    def request_guild_vanity_url(self, guild_id) -> RESPONSE:
        """
        Sends get guild vanity URL request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/vanity-url", "GET")

    def request_guild_widget_image(self, guild_id, style: str = None) -> RESPONSE:
        """
        Sends get guild widget image request.

        :param guild_id: ID of the guild.
        :param style: Style to use. Can be one of ``shield``, ``banner1``, ``banner2``, ``banner3``, or ``banner4``.
        """
        params = f"?style={style}" if style is not None else ""
        return self.download(f"{self.BASE_URL}/guilds/{guild_id}/widget.png{params}")

    def request_guild_welcome_screen(self, guild_id) -> RESPONSE:
        """
        Sends get guild welcome screen request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/welcome-screen", "GET")

    def modify_guild_welcome_screen(self,
                                    guild_id, enabled: bool = EmptyObject,
                                    welcome_channels: typing.List[dict] = EmptyObject,
                                    description: str = EmptyObject,
                                    reason: str = None) -> RESPONSE:
        """
        Sends modify guild welcome screen request.

        :param guild_id: ID of the guild.
        :param enabled: Whether it is enabled.
        :param welcome_channels: Welcome channels to link.
        :param description: Description to show in welcome screen.
        :param reason: Reason of the action.
        """
        body = {}
        if enabled is not EmptyObject:
            body["enabled"] = enabled
        if welcome_channels is not EmptyObject:
            body["welcome_channels"] = welcome_channels
        if description is not EmptyObject:
            body["description"] = description
        return self.request(f"/guilds/{guild_id}/welcome-screen", "PATCH", body, is_json=True, reason_header=reason)

    def modify_user_voice_state(self, guild_id, channel_id: str, user_id="@me", suppress: bool = None, request_to_speak_timestamp: str = None) -> RESPONSE:
        """
        Sends modify curren user or user voice state requset.

        :param guild_id: ID of the guild.
        :param channel_id: ID of the stage channel.
        :param user_id: ID of the user to modify. Set to ``@me`` for current user.
        :param suppress: Whether suppress is enabled.
        :param request_to_speak_timestamp: When to set the user to request to speak. Exclusive to current user(``@me``).
        """
        if user_id != "@me" and request_to_speak_timestamp is not None:
            raise TypeError("request_to_speak_timestamp is exclusive to @me.")
        body = {"channel_id": channel_id}
        if suppress is not None:
            body["suppress"] = suppress
        if request_to_speak_timestamp is not None:
            body["request_to_speak_timestamp"] = request_to_speak_timestamp
        return self.request(f"/guilds/{guild_id}/voice-states/{user_id}", "PATCH", body, is_json=True)

    # Guild Scheduled Event Requests

    def list_scheduled_events_for_guild(self, guild_id, with_user_count: bool = None) -> RESPONSE:
        """
        Sends list scheduled events for guild.

        :param guild_id: ID of the guild to list scheduled events.
        :param with_user_count: Whether to include number of users subscribed to each event.
        """
        params = {}
        if with_user_count is not None:
            params["with_user_count"] = "true" if with_user_count else "false"
        return self.request(f"/guilds/{guild_id}/scheduled-events", "GET", params=params)

    def create_guild_scheduled_event(self,
                                     guild_id,
                                     *,
                                     channel_id: str = None,
                                     entity_metadata: dict = None,
                                     name: str,
                                     privacy_level: int,
                                     scheduled_start_time: str,
                                     scheduled_end_time: str = None,
                                     description: str = None,
                                     entity_type: int) -> RESPONSE:
        """
        Sends create guild scheduled event request.

        :param guild_id: ID of the guild to create.
        :param channel_id: ID of the channel to schedule event. Optional if entity_type is EXTERNAL.
        :param entity_metadata: Entity metadata of the event.
        :param name: Name of the event.
        :param privacy_level: Privacy level of the event.
        :param scheduled_start_time: Scheduled start time of the event.
        :param scheduled_end_time: Scheduled end time of the event.
        :param description: Description of the event.
        :param entity_type: Type of the entity of the event.
        """
        body = {"name": name, "privacy_level": privacy_level, "scheduled_start_time": scheduled_start_time, "entity_type": entity_type}
        if channel_id is not None:
            body["channel_id"] = channel_id
        if entity_metadata is not None:
            body["entity_metadata"] = entity_metadata
        if scheduled_end_time is not None:
            body["scheduled_end_time"] = scheduled_end_time
        if description is not None:
            body["description"] = description
        return self.request(f"/guilds/{guild_id}/scheduled-events", "POST", body, is_json=True)

    def request_guild_scheduled_event(self, guild_id, guild_scheduled_event_id, with_user_count: bool = None):
        """
        Sends get guild scheduled event request.

        :param guild_id: ID of the guild to get scheduled event.
        :param guild_scheduled_event_id: ID of the scheduled event to get.
        :param with_user_count: Whether to include number of users subscribed to this event.
        """
        params = {}
        if with_user_count is not None:
            params["with_user_count"] = "true" if with_user_count else "false"
        return self.request(f"/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}", "GET", params=params)

    def modify_guild_scheduled_event(self,
                                     guild_id,
                                     guild_scheduled_event_id,
                                     channel_id: str = EmptyObject,
                                     entity_metadata: dict = None,
                                     name: str = None,
                                     privacy_level: int = None,
                                     scheduled_start_time: str = None,
                                     scheduled_end_time: str = None,
                                     description: str = None,
                                     entity_type: int = None,
                                     status: int = None):
        """
        Sends modify guild scheduled event request.

        :param guild_id: ID of the guild to modify scheduled events.
        :param guild_scheduled_event_id: ID of the event to modify.
        :param channel_id: ID of the channel of the event. Set to ``None`` if you are changing event to EXTERNAL.
        :param entity_metadata: Entity metadata of the event.
        :param name: Name of the event.
        :param privacy_level: Privacy level of the event.
        :param scheduled_start_time: Scheduled start time of the event.
        :param scheduled_end_time: Scheduled end time of the event.
        :param description: Description of the event.
        :param entity_type: Type of the entity of the event.
        :param status: Status of the event.
        """
        body = {}
        if channel_id is not EmptyObject:
            body["channel_id"] = channel_id
        if entity_metadata is not None:
            body["entity_metadata"] = entity_metadata
        if name is not None:
            body["name"] = name
        if privacy_level is not None:
            body["privacy_level"] = privacy_level
        if scheduled_start_time is not None:
            body["scheduled_start_time"] = scheduled_start_time
        if scheduled_end_time is not None:
            body["scheduled_end_time"] = scheduled_end_time
        if description is not None:
            body["description"] = description
        if entity_type is not None:
            body["entity_type"] = entity_type
        if status is not None:
            body["status"] = status
        return self.request(f"/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}", "PATCH", body, is_json=True)

    def delete_guild_scheduled_event(self, guild_id, guild_scheduled_event_id):
        """
        Sends delete guild scheduled event request.

        :param guild_id: ID of the guild to delete scheduled event.
        :param guild_scheduled_event_id: ID of the scheduled event to delete.
        """
        return self.request(f"/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}", "DELETE")

    def request_guild_scheduled_event_users(self,
                                            guild_id,
                                            guild_scheduled_event_id,
                                            limit: int = None,
                                            with_member: bool = None,
                                            before: str = None,
                                            after: str = None):
        """
        Sends get guild scheduled event users request.

        :param guild_id: ID of the guild to get scheduled event users.
        :param guild_scheduled_event_id: ID of the scheduled event to get users.
        :param limit: Maximum number of users to return.
        :param with_member: Whether to include member data.
        :param before: ID of the user to get users before.
        :param after: ID of the user to get users after.
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if with_member is not None:
            params["with_member"] = "true" if with_member else "false"
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after
        return self.request(f"/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}/users", "GET", params=params)

    # Guild Template Requests

    def request_guild_template(self, template_code) -> RESPONSE:
        """
        Sends get guild template request.

        :param template_code: Code of the template.
        """
        return self.request(f"/guilds/templates/{template_code}", "GET")

    def create_guild_from_template(self, template_code, name: str, icon: str = None) -> RESPONSE:
        """
        Sends create guild from template request.

        :param template_code: Code of the template.
        :param name: Name of the guild.
        :param icon: Icon of the guild.
        """
        body = {"name": name}
        if icon is not None:
            body["icon"] = icon
        return self.request(f"/guilds/templates/{template_code}", "POST", body, is_json=True)

    def request_guild_templates(self, guild_id) -> RESPONSE:
        """
        Sends get guild templates request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/templates", "GET")

    def create_guild_template(self, guild_id, name: str, description: str = EmptyObject) -> RESPONSE:
        """
        Sends create guild template request.

        :param guild_id: ID of the guild.
        :param name: Name of the template to create.
        :param description: Description of the template
        """
        body = {"name": name}
        if description is not EmptyObject:
            body["description"] = description
        return self.request(f"/guilds/{guild_id}/templates", "POST", body, is_json=True)

    def sync_guild_template(self, guild_id, template_code) -> RESPONSE:
        """
        Sends sync guild template request.

        :param guild_id: ID of the guild.
        :param template_code: Code of the template to sync.
        """
        return self.request(f"/guilds/{guild_id}/templates/{template_code}", "PUT")

    def modify_guild_template(self, guild_id, template_code, name: str = None, description: str = EmptyObject) -> RESPONSE:
        """
        Sends modify guild template request.

        :param guild_id: ID of the guild.
        :param template_code: Code of the template.
        :param name: Name to change.
        :param description: Description to change.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if description is not EmptyObject:
            body["description"] = description
        return self.request(f"/guilds/{guild_id}/templates/{template_code}", "PATCH", body, is_json=True)

    def delete_guild_template(self, guild_id, template_code) -> RESPONSE:
        """
        Sends delete guild template request.

        :param guild_id: ID of the guild.
        :param template_code: Code of the template.
        """
        return self.request(f"/guilds/{guild_id}/templates/{template_code}", "DELETE")

    # Invite Requests

    def request_invite(self, invite_code, with_counts: bool = None, with_expiration: bool = None) -> RESPONSE:
        """
        Sends get invite request.

        :param invite_code: Code of the invite.
        :param with_counts: Whether to include counts.
        :param with_expiration: Whether to include expiration info.
        """
        params = {}
        if with_counts is not None:
            params["with_counts"] = "true" if with_counts else "false"
        if with_expiration is not None:
            params["with_expiration"] = "true" if with_expiration else "false"
        return self.request(f"/invites/{invite_code}", "GET", params=params)

    def delete_invite(self, invite_code, reason: str = None) -> RESPONSE:
        """
        Sends delete invite request.

        :param invite_code: Code of the invite.
        :param reason: Reason of the action.
        """
        return self.request(f"/invites/{invite_code}", "DELETE", reason_header=reason)

    # Stage Instance requests

    def create_stage_instance(self, channel_id: str, topic: str, privacy_level: int = None, reason: str = None) -> RESPONSE:
        """
        Sends create stage instance request.

        :param channel_id: ID of the stage channel.
        :param topic: Topic of the stage instance.
        :param privacy_level: Privacy level of the stage.
        :param reason: Reason of the action.
        """
        body = {"channel_id": channel_id, "topic": topic}
        if privacy_level is not None:
            body["privacy_level"] = privacy_level
        return self.request("/stage-instances", "POST", body, is_json=True, reason_header=reason)

    def request_stage_instance(self, channel_id) -> RESPONSE:
        """
        Sends get stage instance request.

        :param channel_id: ID of the channel.
        """
        return self.request(f"/stage-instances/{channel_id}", "GET")

    def modify_stage_instance(self, channel_id, topic: str = None, privacy_level: int = None, reason: str = None) -> RESPONSE:
        """
        Sends modify stage instance request.

        :param channel_id: ID of the stage channel.
        :param topic: Topic to change.
        :param privacy_level: Privacy level to change.
        :param reason: Reason of the action.
        """
        body = {}
        if topic is not None:
            body["topic"] = topic
        if privacy_level is not None:
            body["privacy_level"] = privacy_level
        return self.request(f"/stage-instances/{channel_id}", "PATCH", body, is_json=True, reason_header=reason)

    def delete_stage_instance(self, channel_id, reason: str = None) -> RESPONSE:
        """
        Sends delete stage instance request.

        :param channel_id: ID of the stage channel.
        :param reason: Reason of the action.
        """
        return self.request(f"/stage-instances/{channel_id}", "DELETE", reason_header=reason)

    # Sticker Requests

    def request_sticker(self, sticker_id) -> RESPONSE:
        """
        Sends get sticker request.

        :param sticker_id: ID of the sticker.
        """
        return self.request(f"/stickers/{sticker_id}", "GET")

    def list_nitro_sticker_packs(self) -> RESPONSE:
        """
        Sends list nitro sticker packs request.
        """
        return self.request("/sticker-packs", "GET")

    def list_guild_stickers(self, guild_id) -> RESPONSE:
        """
        Sends list guild stickers request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/stickers", "GET")

    def request_guild_sticker(self, guild_id, sticker_id) -> RESPONSE:
        """
        Sends get guild sticker request.

        :param guild_id: ID of the guild.
        :param sticker_id: ID of the sticker to request.
        """
        return self.request(f"/guilds/{guild_id}/stickers/{sticker_id}", "GET")

    @abstractmethod
    def create_guild_sticker(self, guild_id, name: str, description: str, tags: str, file: io.FileIO, reason: str = None) -> RESPONSE:
        """
        Sends create guild sticker request.

        :param guild_id: ID of the guild.
        :param name: Name of the sticker.
        :param description: Description of the sticker.
        :param tags: Autocomplete text.
        :param file: Sticker file to upload. Max 500 KB.
        :param reason: Reason of the action.
        """
        pass

    def modify_guild_sticker(self, guild_id, sticker_id, name: str = None, description: str = EmptyObject, tags: str = None, reason: str = None) -> RESPONSE:
        """
        Sends modify guild sticker request.

        :param guild_id: ID of the guild.
        :param sticker_id: ID of the sticker to modify.
        :param name: Name to modify.
        :param description: Description to modify. Can be None.
        :param tags: Tags to edit.
        :param reason: Reason of the action.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if description is not EmptyObject:
            body["description"] = description
        if tags is not None:
            body["tags"] = tags
        return self.request(f"/guilds/{guild_id}/stickers/{sticker_id}", "PATCH", body, is_json=True, reason_header=reason)

    def delete_guild_sticker(self, guild_id, sticker_id, reason: str = None):
        """
        Sends delete guild sticker request.

        :param guild_id: ID of the guild.
        :param sticker_id: ID of sticker to delete.
        :param reason: Reason of the action.
        """
        return self.request(f"/guilds/{guild_id}/stickers/{sticker_id}", "DELETE", reason_header=reason)

    # User Requests

    def request_user(self, user_id="@me") -> RESPONSE:
        """
        Sends get user request.

        :param user_id: ID of the user to get.
        """
        return self.request(f"/users/{user_id}", "GET")

    def modify_current_user(self, username: str = None, avatar: str = EmptyObject) -> RESPONSE:
        """
        Sends modify current user request. You can create avatar using ``to_image_data`` of utils.

        :param username: Name to modify.
        :param avatar: Image data to modify.
        """
        body = {}
        if username is not None:
            body["username"] = username
        if avatar is not EmptyObject:
            body["avatar"] = avatar
        return self.request("/users/@me", "PATCH", body, is_json=True)

    def request_current_user_guilds(self) -> RESPONSE:
        """
        Sends get current user guilds request.
        """
        return self.request(f"/users/@me/guilds", "GET")

    def leave_guild(self, guild_id) -> RESPONSE:
        """
        Sends leave guild request.

        :param guild_id: ID of the guild to leave.
        """
        return self.request(f"/users/@me/guilds/{guild_id}", "DELETE")

    def create_dm(self, recipient_id: str) -> RESPONSE:
        """
        Sends create dm request.

        :param recipient_id: ID of the recipient to add.
        """
        return self.request(f"/users/@me/channels", "POST", {"recipient_id": recipient_id}, is_json=True)

    def create_group_dm(self, access_tokens: typing.List[str], nicks: typing.Dict[str, str]) -> RESPONSE:
        """
        Sends create group dm request.

        :param access_tokens: OAuth2 access tokens of the participants to add.
        :param nicks: Dict of ID-nick to set.
        """
        return self.request(f"/users/@me/channels", "POST", {"access_tokens": access_tokens, "nicks": nicks}, is_json=True)

    # Voice Requests

    def list_voice_regions(self) -> RESPONSE:
        """
        Sends list voice regions request.
        """
        return self.request("/voice/regions", "GET")

    # Webhook Requests

    def create_webhook(self, channel_id, name: str, avatar: str = None) -> RESPONSE:
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

    def request_channel_webhooks(self, channel_id) -> RESPONSE:
        """
        Sends get channel webhooks request.

        :param channel_id: ID of the channel.
        """
        return self.request(f"/channels/{channel_id}/webhooks", "GET")

    def request_guild_webhooks(self, guild_id) -> RESPONSE:
        """
        Sends get guild webhooks request.

        :param guild_id: ID of the guild.
        """
        return self.request(f"/guilds/{guild_id}/webhooks", "GET")

    def request_webhook(self, webhook_id) -> RESPONSE:
        """
        Sends get webhook request.

        :param webhook_id: ID of the webhook.
        """
        return self.request(f"/webhooks/{webhook_id}", "GET")

    def request_webhook_with_token(self, webhook_id, webhook_token) -> RESPONSE:
        """
        Sends get webhook request.

        :param webhook_id: ID of the webhook.
        :param webhook_token: Token of the webhook.
        """
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}", "GET")

    def modify_webhook(self, webhook_id, name: str = None, avatar: str = None, channel_id: str = None) -> RESPONSE:
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

    def modify_webhook_with_token(self, webhook_id, webhook_token, name: str = None, avatar: str = None) -> RESPONSE:
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

    def delete_webhook(self, webhook_id) -> RESPONSE:
        """
        Sends delete webhook request.

        :param webhook_id: ID of the webhook.
        """
        return self.request(f"/webhooks/{webhook_id}", "DELETE")

    def delete_webhook_with_token(self, webhook_id, webhook_token) -> RESPONSE:
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
                        components: typing.List[dict] = None,
                        flags: int = None) -> RESPONSE:
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
        :param components: Components of the message.
        :param flags: Flags of the message.
        :return: Message object dict.
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
        if components is not None:
            body["components"] = components
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
                                   components: typing.List[dict] = None,
                                   attachments: typing.List[dict] = None,
                                   flags: int = None) -> RESPONSE:
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
        :param components: Components of the message.
        :param attachments: List of attachment objects.
        :param flags: Flags of the message.
        """
        pass

    def request_webhook_message(self, webhook_id, webhook_token, message_id) -> RESPONSE:
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
                             content: str = EmptyObject,
                             embeds: typing.List[dict] = EmptyObject,
                             files: typing.List[io.FileIO] = EmptyObject,
                             allowed_mentions: dict = EmptyObject,
                             attachments: typing.List[dict] = EmptyObject,
                             components: typing.List[dict] = EmptyObject) -> RESPONSE:
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
        :param components: Components of the message.
        """
        pass

    def delete_webhook_message(self, webhook_id, webhook_token, message_id) -> RESPONSE:
        """
        Sends delete webhook message request.

        :param webhook_id: ID of the webhook.
        :param webhook_token: Token of the webhook.
        :param message_id: ID of the message to edit.
        """
        return self.request(f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}", "DELETE")

    # Interaction Requests

    def request_application_commands(self, application_id, guild_id=None) -> RESPONSE:
        """
        Sends get global or guild application commands request.

        :param application_id: ID of the application.
        :param guild_id: ID of the guild. Set to None for global.
        """
        return self.request(f"/applications/{application_id}/"+(f"guilds/{guild_id}/commands" if guild_id else "commands"), "GET")

    def create_application_command(self,
                                   application_id,
                                   name: str,
                                   description: str = None,
                                   options: typing.List[dict] = None,
                                   default_permission: bool = None,
                                   command_type: int = None,
                                   guild_id=None) -> RESPONSE:
        """
        Sends create global or guild application command request.

        :param application_id: ID of the application.
        :param name: Name of the command.
        :param description: Description of the command.
        :param options: Options of the command.
        :param default_permission: Whether the command is enabled as a default.
        :param command_type: Type of the command.
        :param guild_id: ID of the guild. Set to None for global.
        """
        body = {"name": name}
        if description is not None:
            body["description"] = description
        if options:
            body["options"] = options
        if default_permission is not None:
            body["default_permission"] = default_permission
        if command_type is not None:
            body["type"] = command_type
        return self.request(f"/applications/{application_id}/"+(f"guilds/{guild_id}/commands" if guild_id else "commands"), "POST", body, is_json=True)

    def request_application_command(self, application_id, command_id, guild_id=None) -> RESPONSE:
        """
        Sends get global or guild application command request.

        :param application_id: ID of the application.
        :param command_id: ID of the command to request.
        :param guild_id: ID of the guild. Set to None for global.
        """
        return self.request(f"/applications/{application_id}/"+(f"guilds/{guild_id}/commands" if guild_id else "commands")+f"/{command_id}", "GET")

    def edit_application_command(self, application_id, command_id, name: str = None, description: str = None, options: typing.List[dict] = None, default_permission: bool = None, guild_id=None) -> RESPONSE:
        """
        Sends edit global or guild application command request.

        :param application_id: ID of the application.
        :param command_id: ID of the command to edit.
        :param name: Name of the command.
        :param description: Description of the command.
        :param options: Options of the command.
        :param default_permission: Whether the command is enabled as a default.
        :param guild_id: ID of the guild. Set to None for global.
        """
        body = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if options is not None:
            body["options"] = options
        if default_permission is not None:
            body["default_permission"] = default_permission
        return self.request(f"/applications/{application_id}/"+(f"guilds/{guild_id}/commands" if guild_id else "commands")+f"/{command_id}", "PATCH", body, is_json=True)

    def delete_application_command(self, application_id, command_id, guild_id=None) -> RESPONSE:
        """
        Sends delete global or guild application command request.

        :param application_id: ID of the application.
        :param command_id: ID of the command to request.
        :param guild_id: ID of the guild. Set to None for global.
        """
        return self.request(f"/applications/{application_id}/"+(f"guilds/{guild_id}/commands" if guild_id else "commands")+f"/{command_id}", "DELETE")

    def bulk_overwrite_application_commands(self, application_id, commands: typing.List[dict], guild_id=None) -> RESPONSE:
        """
        Sends delete global or guild application command request.

        :param application_id: ID of the application.
        :param commands: List of commands to overwrite.
        :param guild_id: ID of the guild. Set to None for global.
        """
        return self.request(f"/applications/{application_id}/"+(f"guilds/{guild_id}/commands" if guild_id else "commands"), "PUT", commands, is_json=True)

    def create_interaction_response(self, interaction_id, interaction_token, interaction_response: dict) -> RESPONSE:
        """
        Sends create interaction response request.

        :param interaction_id: ID of the interaction.
        :param interaction_token: Token of the interaction.
        :param interaction_response: Interaction Response as dict.
        """
        return self.request(f"/interactions/{interaction_id}/{interaction_token}/callback", "POST", interaction_response, is_json=True)

    def request_interaction_response(self, application_id, interaction_token, message_id="@original") -> RESPONSE:
        """
        Sends get original interaction response request.

        :param application_id: ID of the application.
        :param interaction_token: Token of the interaction.
        :param message_id: ID of the message to request.
        """
        return self.request_webhook_message(application_id, interaction_token, message_id)

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
                                components: typing.List[dict] = None,
                                attachments: typing.List[dict] = None,
                                flags: int = None) -> RESPONSE:
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
        :param components: Components of the message.
        :param attachments: List of attachment objects.
        :param flags: Flags of the message.
        """
        return self.execute_webhook_with_files(application_id, interaction_token, None, None, content, username, avatar_url,
                                               tts, files, embeds, allowed_mentions, components, attachments, flags) if files \
            else self.execute_webhook(application_id, interaction_token, None, None, content, username, avatar_url, tts, embeds, allowed_mentions, components, flags)

    def edit_interaction_response(self,
                                  application_id,
                                  interaction_token,
                                  message_id="@original",
                                  content: str = EmptyObject,
                                  embeds: typing.List[dict] = EmptyObject,
                                  files: typing.List[io.FileIO] = EmptyObject,
                                  allowed_mentions: dict = EmptyObject,
                                  attachments: typing.List[dict] = EmptyObject,
                                  components: typing.List[dict] = EmptyObject) -> RESPONSE:
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
        :param components: Components of the message.
        """
        return self.edit_webhook_message(application_id, interaction_token, message_id, content, embeds, files, allowed_mentions, attachments, components)

    @property
    def edit_followup_message(self):
        """Sends edit followup message request. Actually an alias of :meth:`.edit_interaction_response`."""
        return self.edit_interaction_response

    def delete_interaction_response(self, application_id, interaction_token, message_id="@original") -> RESPONSE:
        """
        Sends delete interaction response request.

        :param application_id: ID of the application.
        :param interaction_token: Token of the interaction.
        :param message_id: ID of the message to delete.
        """
        return self.delete_webhook_message(application_id, interaction_token, message_id)

    def request_guild_application_command_permissions(self, application_id, guild_id) -> RESPONSE:
        """
        Sends get guild application command permissions request.

        :param application_id: ID of the application.
        :param guild_id: ID of the guild.
        """
        return self.request(f"/applications/{application_id}/guilds/{guild_id}/commands/permissions", "GET")

    def request_application_command_permissions(self, application_id, guild_id, command_id) -> RESPONSE:
        """
        Sends get application command permissions request.

        :param application_id: ID of the application.
        :param guild_id: ID of the guild.
        :param command_id: ID of the command to get.
        """
        return self.request(f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions", "GET")

    def edit_application_command_permissions(self, application_id, guild_id, command_id, permissions: typing.List[dict]) -> RESPONSE:
        """
        Sends edit application command permissions request.

        :param application_id: ID of the application.
        :param guild_id: ID of the guild.
        :param command_id: ID of the command to edit.
        :param permissions: List of permissions to edit
        :return:
        """
        body = {"permissions": permissions}
        return self.request(f"/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions", "PUT", body, is_json=True)

    def batch_edit_application_command_permissions(self, application_id, guild_id, permissions: typing.List[dict]) -> RESPONSE:
        """
        Sends batch edit application command permissions request.

        :param application_id: ID of the application.
        :param guild_id: ID of the guild.
        :param permissions: List of dict of command ID and permissions to edit
        :return:
        """
        return self.request(f"/applications/{application_id}/guilds/{guild_id}/commands/permissions", "PUT", permissions, is_json=True)

    # OAuth2 Requests

    def request_current_bot_application_information(self) -> RESPONSE:
        """
        Sends get current bot application information request.
        """
        return self.request("/oauth2/applications/@me", "GET")

    # Gateway Requests

    def request_gateway(self, bot: bool = True) -> RESPONSE:
        """
        Sends get gateway request.

        :param bot: Whether it should be bot.
        """
        extra = "/bot" if bot else ""
        return self.request("/gateway"+extra, "GET")

    # Misc

    @abstractmethod
    def download(self, url) -> RESPONSE:
        """
        Downloads file from passed url.

        :param url: URL to download.
        """
        pass

    @classmethod
    @abstractmethod
    def create(cls, token, *args, **kwargs) -> "HTTPRequestBase":
        """
        Creates new HTTP request client.

        :param token: Token of the bot.
        :param args: Extra optional args.
        :param kwargs: Extra optional keyword args.
        :return: Initialized object.
        """
        pass
