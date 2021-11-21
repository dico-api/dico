import io
import datetime
from typing import TYPE_CHECKING, Optional, Union, Type, List, Dict, Awaitable
from .base.http import HTTPRequestBase, EmptyObject
from .model import Channel, Message, MessageReference, AllowedMentions, Snowflake, Embed, Attachment, Overwrite, \
    Emoji, User, Interaction, InteractionResponse, Webhook, Guild, ApplicationCommand, Invite, Application, FollowedChannel, \
    ThreadMember, ListThreadsResponse, Component, Role, ApplicationCommandOption, GuildApplicationCommandPermissions, \
    ApplicationCommandPermissions, VerificationLevel, DefaultMessageNotificationLevel, ExplicitContentFilterLevel, \
    SystemChannelFlags, GuildPreview, ChannelTypes, GuildMember, Ban, PermissionFlags, GuildWidget, FILE_TYPE, \
    VoiceRegion, Integration, ApplicationCommandTypes, WelcomeScreen, WelcomeScreenChannel, PrivacyLevel, StageInstance, \
    AuditLog, AuditLogEvents, GuildTemplate, BYTES_RESPONSE, Sticker, GetGateway, VideoQualityModes, InviteTargetTypes, WidgetStyle, \
    GuildScheduledEvent, GuildScheduledEventEntityMetadata, GuildScheduledEventPrivacyLevel, GuildScheduledEventEntityTypes, GuildScheduledEventStatus, \
    GuildScheduledEventUser
from .utils import from_emoji, wrap_to_async, to_image_data

if TYPE_CHECKING:
    from .base.model import AbstractObject, DiscordObjectBase


class APIClient:
    """
    REST API handling client.

    Example:

    .. code-block:: python

        import dico

        # For request-based:
        api = dico.APIClient("TOKEN", base=dico.HTTPRequest)

        # For aiohttp-based:
        api = dico.APIClient("TOKEN", base=dico.AsyncHTTPRequest)

        ...

    .. note::
        Most of the object parameters accept Snowflake or int or str. For example, you may pass ``832488750034190378`` in Message type.

    :param str token: Token of the client.
    :param Type[HTTPRequestBase] base: HTTP request handler to use. Must inherit :class:`~.HTTPRequestBase`.
    :param Optional[AllowedMentions] default_allowed_mentions: Default allowed mentions object to use. Default None.
    :param Optional[Snowflake] application_id: ID of the application. Required if you use interactions.
    :param http_options: Options of HTTP request handler.

    :ivar HTTPRequestBase ~.http: HTTP request client.
    :ivar Optional[AllowedMentions] ~.default_allowed_mentions: Default allowed mentions object of the API client.
    :ivar Optional[Application] ~.application: Application object of the client.
    :ivar Optional[Snowflake] ~.application_id: ID of the application. Can be ``None``, and if it is, you must pass parameter application_id for all methods that requires it.
    """

    def __init__(self,
                 token: str,
                 *,
                 base: Type[HTTPRequestBase],
                 default_allowed_mentions: Optional[AllowedMentions] = None,
                 application_id: Optional[Snowflake.TYPING] = None,
                 **http_options):
        self.http: HTTPRequestBase = base.create(token, **http_options)
        self.default_allowed_mentions: Optional[AllowedMentions] = default_allowed_mentions
        self.application: Optional[Application] = None
        self.application_id: Optional[Snowflake] = Snowflake.ensure_snowflake(application_id)

    # Audit Log

    def request_guild_audit_log(self,
                                guild: Guild.TYPING,
                                *,
                                user: Optional[User.TYPING] = None,
                                action_type: Optional[Union[int, AuditLogEvents]] = None,
                                before: Optional["DiscordObjectBase.TYPING"] = None,
                                limit: Optional[int] = None) -> AuditLog.RESPONSE:
        """
        Requests guild audit log.

        :param guild: Guild to request audit log.
        :param user: Moderator who did the action. Default all.
        :param Optional[AuditLogEvents] action_type: Type of the audit log to get.
        :param before: Entry object to get before. Can be any object which includes ID.
        :param Optional[int] limit: Limit of the number of the audit logs to get.
        :return: :class:`~.AuditLog`
        """
        if user is not None:
            user = str(int(user))
        if action_type is not None:
            action_type = int(action_type)
        if before is not None:
            before = str(int(before))
        resp = self.http.request_guild_audit_log(int(guild), user, action_type, before, limit)
        if isinstance(resp, dict):
            return AuditLog(self, resp)
        return wrap_to_async(AuditLog, self, resp, as_create=False)

    # Channel

    def request_channel(self, channel: Channel.TYPING) -> Channel.RESPONSE:
        """
        Requests channel object.

        :param channel: Channel to get.
        :return: :class:`~.Channel`
        """
        channel = self.http.request_channel(int(channel))
        if isinstance(channel, dict):
            return Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def modify_guild_channel(self,
                             channel: Channel.TYPING,
                             *,
                             name: Optional[str] = None,
                             channel_type: Optional[Union[int, ChannelTypes]] = None,
                             position: Optional[int] = EmptyObject,
                             topic: Optional[str] = EmptyObject,
                             nsfw: Optional[bool] = EmptyObject,
                             rate_limit_per_user: Optional[int] = EmptyObject,
                             bitrate: Optional[int] = EmptyObject,
                             user_limit: Optional[int] = EmptyObject,
                             permission_overwrites: Optional[List[Overwrite]] = EmptyObject,
                             parent: Optional[Channel.TYPING] = EmptyObject,
                             rtc_region: Optional[str] = EmptyObject,
                             video_quality_mode: Optional[Union[int, VideoQualityModes]] = EmptyObject,
                             reason: Optional[str] = None) -> Channel.RESPONSE:
        """
        Modifies guild channel.

        .. note::
            All keyword-only arguments except name, channel_type, and reason accept None.

        :param channel: Channel to edit.
        :param Optional[str] name: Name of the channel to change.
        :param Optional[ChannelTypes] channel_type: Type of the channel to change.
        :param Optional[int] position: Position of the channel to change.
        :param Optional[str] topic: Topic of the channel to change.
        :param Optional[bool] nsfw: Whether this channel is NSFW.
        :param Optional[int] rate_limit_per_user: Slowmode of the channel to change.
        :param Optional[int] bitrate: Bitrate of the channel to change.
        :param Optional[int] user_limit: User limit of the channel to change.
        :param Optional[List[Overwrite]] permission_overwrites: List of permission overwrites to change.
        :param parent: Parent category of the channel to change.
        :param Optional[str] rtc_region: RTC region of the channel to change. Pass None to set to automatic.
        :param Optional[VideoQualityModes] video_quality_mode: Video quality mode of the camera to change.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        if permission_overwrites:
            permission_overwrites = [x.to_dict() for x in permission_overwrites]
        if parent:
            parent = int(parent)  # noqa
        channel = self.http.modify_guild_channel(int(channel), name, int(channel_type), position, topic, nsfw, rate_limit_per_user,
                                                 bitrate, user_limit, permission_overwrites, parent, rtc_region, int(video_quality_mode), reason=reason)
        if isinstance(channel, dict):
            return Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def modify_group_dm_channel(self, channel: Channel.TYPING, *, name: Optional[str] = None, icon: Optional[bytes] = None, reason: Optional[str] = None) -> Channel.RESPONSE:
        """
        Modifies group DM channel.

        :param channel: DM Channel to modify.
        :param Optional[str] name: Name to change.
        :param Optional[bin] icon: Icon as bytes to change.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        channel = self.http.modify_group_dm_channel(int(channel), name, icon, reason=reason)
        if isinstance(channel, dict):
            return Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def modify_thread_channel(self,
                              channel: Channel.TYPING,
                              *,
                              name: Optional[str] = None,
                              archived: Optional[bool] = None,
                              auto_archive_duration: Optional[int] = None,
                              locked: Optional[bool] = None,
                              rate_limit_per_user: Optional[int] = EmptyObject,
                              reason: Optional[str] = None) -> Channel.RESPONSE:
        """
        Modifies thread channel.

        :param channel: Thread channel to modify.
        :param Optional[str] name: Name to change.
        :param archived: Whether this thread is archived.
        :param Optional[int] auto_archive_duration: Auto archive duration to set.
        :param Optional[bool] locked: Whether this thread is locked.
        :param Optional[int] rate_limit_per_user: Slowmode time to change. Set to None to remove.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        channel = self.http.modify_thread_channel(int(channel), name, archived, auto_archive_duration, locked, rate_limit_per_user, reason=reason)
        if isinstance(channel, dict):
            return Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def delete_channel(self, channel: Channel.TYPING, *, reason: Optional[str] = None) -> Channel.RESPONSE:
        """
        Deletes channel.

        :param channel: Channel to delete.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        resp = self.http.delete_channel(int(channel), reason=reason)
        if isinstance(resp, dict):
            return Channel.create(self, resp, prevent_caching=True)
        return wrap_to_async(Channel, self, resp, prevent_caching=True)

    def request_channel_messages(self,
                                 channel: Channel.TYPING,
                                 *,
                                 around: Optional[Message.TYPING] = None,
                                 before: Optional[Message.TYPING] = None,
                                 after: Optional[Message.TYPING] = None,
                                 limit: Optional[int] = None) -> Message.RESPONSE_AS_LIST:
        """
        Requests list of messages in the channel.

        :param channel: Channel to request messages.
        :param around: Target message to get around.
        :param before: Target message to get before.
        :param after: Target message to get after.
        :param Optional[int] limit: Limit of numbers of messages to request. Default 50.
        :return: List[ :class:`~.Message` ]
        """
        messages = self.http.request_channel_messages(int(channel), around and str(int(around)), before and str(int(before)), after and str(int(after)), limit)
        # This looks unnecessary, but this is to ensure they are all numbers.
        if isinstance(messages, list):
            return [Message.create(self, x) for x in messages]
        return wrap_to_async(Message, self, messages)

    def request_channel_message(self, channel: Channel.TYPING, message: Message.TYPING) -> Message.RESPONSE:
        """
        Requests message from channel.

        :param channel: Channel to request message.
        :param message: Message to request.
        :return: :class:`~.Message`
        """
        message = self.http.request_channel_message(int(channel), int(message))
        if isinstance(message, dict):
            return Message.create(self, message)
        return wrap_to_async(Message, self, message)

    def create_message(self,
                       channel: Channel.TYPING,
                       content: Optional[str] = None,
                       *,
                       embed: Optional[Union[Embed, dict]] = None,
                       embeds: Optional[List[Union[Embed, dict]]] = None,
                       file: Optional[FILE_TYPE] = None,
                       files: Optional[List[FILE_TYPE]] = None,
                       tts: Optional[bool] = False,
                       allowed_mentions: Optional[Union[AllowedMentions, dict]] = None,
                       message_reference: Optional[Union[Message, MessageReference, dict]] = None,
                       component: Optional[Union[dict, Component]] = None,
                       components: Optional[List[Union[dict, Component]]] = None,
                       sticker: Optional[Sticker.TYPING] = None,
                       stickers: Optional[List[Sticker.TYPING]] = None) -> Message.RESPONSE:
        """
        Creates message to channel.

        .. note::
            - FileIO object passed to ``file`` or ``files`` parameter will be automatically closed when requesting,
              therefore it is recommended to pass file path.

        .. warning::
            - You must pass at least one of ``content`` or ``embed`` or ``file`` or ``files`` parameter.
            - You can't use ``file`` and ``files`` at the same time.

        :param channel: Channel to create message.
        :param Optional[str] content: Content of the message.
        :param embed: Embed of the message.
        :type embed: Optional[Union[Embed, dict]]
        :param embeds: List of embeds of the message.
        :type embeds: Optional[List[Union[Embed, dict]]]
        :param file: File of the message.
        :type file: Optional[Union[io.FileIO, pathlib.Path, str]]
        :param files: Files of the message.
        :type files: Optional[List[Union[io.FileIO, pathlib.Path, str]]]
        :param Optional[bool] tts: Whether to speak message.
        :param allowed_mentions: :class:`~.AllowedMentions` to use for this request.
        :type allowed_mentions: Optional[Union[AllowedMentions, dict]]
        :param message_reference: Message to reply.
        :type message_reference: Optional[Union[Message, MessageReference, dict]]
        :param component: Component of the message.
        :type component: Optional[Union[dict, Component]]
        :param components: List of  components of the message.
        :type components: Optional[List[Union[dict, Component]]]
        :param Optional[Sticker] sticker: Sticker of the message.
        :param Optional[List[Sticker]] stickers: Stickers of the message. Up to 3.
        :return: :class:`~.Message`
        """
        if files and file:
            raise TypeError("you can't pass both file and files.")
        if file:
            files = [file]
        if files:
            for x in range(len(files)):
                sel = files[x]
                if isinstance(sel, str):
                    files[x] = open(sel, "rb")
        if isinstance(message_reference, Message):
            message_reference = MessageReference.from_message(message_reference)
        if embed and embeds:
            raise TypeError("you can't pass both embed and embeds.")
        if embed:
            embeds = [embed]
        if embeds:
            embeds = [x if isinstance(x, dict) else x.to_dict() for x in embeds]
        if message_reference and not isinstance(message_reference, dict):
            message_reference = message_reference.to_dict()
        if component and components:
            raise TypeError("you can't pass both component and components.")
        if component:
            components = [component]
        if components:
            components = [*map(lambda n: n if isinstance(n, dict) else n.to_dict(), components)]
        if sticker and stickers:
            raise TypeError("you can't pass both sticker and stickers.")
        if sticker:
            stickers = [sticker]
        if stickers:
            stickers = [*map(int, stickers)]
        params = {"channel_id": int(channel),
                  "content": content,
                  "embeds": embeds,
                  "nonce": None,  # What does this do tho?
                  "message_reference": message_reference,
                  "tts": tts,
                  "allowed_mentions": self.get_allowed_mentions(allowed_mentions),
                  "components": components,
                  "sticker_ids": stickers}
        if files:
            params["files"] = files
        try:
            msg = self.http.create_message_with_files(**params) if files else self.http.create_message(**params)
            if isinstance(msg, dict):
                return Message.create(self, msg)
            return wrap_to_async(Message, self, msg)
        finally:
            if files:
                [x.close() for x in files if not x.closed]

    def crosspost_message(self,
                          channel: Channel.TYPING,
                          message: Message.TYPING) -> Message.RESPONSE:
        """
        Crossposts message.

        :param channel: Channel of the message to crosspost.
        :param message: Message to crosspost.
        :return: :class:`~..Message`
        """
        msg = self.http.crosspost_message(int(channel), int(message))
        if isinstance(msg, dict):
            return Message.create(self, msg)
        return wrap_to_async(Message, self, msg)

    def create_reaction(self,
                        channel: Channel.TYPING,
                        message: Message.TYPING,
                        emoji: Union[str, Emoji]):
        """
        Creates reaction to the message.

        :param channel: Channel of the message to create reaction.
        :param message: Message to create reaction.
        :param emoji: Emoji for creating reaction.
        :type emoji: Union[str, Emoji]
        """
        return self.http.create_reaction(int(channel), int(message), from_emoji(emoji))

    def delete_reaction(self,
                        channel: Channel.TYPING,
                        message: Message.TYPING,
                        emoji: Union[str, Emoji],
                        user: User.TYPING = "@me"):
        """
        Deletes reaction of the message.

        :param channel: Channel of the message to delete reaction.
        :param message: Message to delete reaction.
        :param emoji: Emoji of the reaction to delete.
        :type emoji: Union[str, Emoji]
        :param user: User to delete reaction of. Default "@me" which is the bot itself.
        """
        return self.http.delete_reaction(int(channel), int(message), from_emoji(emoji), int(user) if user != "@me" else user)

    def request_reactions(self,
                          channel: Channel.TYPING,
                          message: Message.TYPING,
                          emoji: Union[str, Emoji],
                          after: Optional[User.TYPING] = None,
                          limit: Optional[int] = None) -> User.RESPONSE_AS_LIST:
        """
        Requests list of users reacted to the message.

        :param channel: Channel of the message to get reacted users.
        :param message: Message to get reacted users.
        :param emoji: Emoji of the reaction to get.
        :type emoji: Union[str, Emoji]
        :param after: The target user to get after.
        :param Optional[int] limit: Limit of the number of the reactions.
        :return: :class:`~.User`
        """
        users = self.http.request_reactions(int(channel), int(message), from_emoji(emoji), int(after), limit)
        if isinstance(users, list):
            return [User.create(self, x) for x in users]
        return wrap_to_async(User, self, users)

    def delete_all_reactions(self, channel: Channel.TYPING, message: Message.TYPING):
        """
        Deletes all reactions of the message.

        :param channel: Channel of the message to delete all reactions.
        :param message: Message to delete all reactions.
        """
        return self.http.delete_all_reactions(int(channel), int(message))

    def delete_all_reactions_emoji(self,
                                   channel: Channel.TYPING,
                                   message: Message.TYPING,
                                   emoji: Union[str, Emoji]):
        """
        Deletes all reactions of the selected emoji.

        :param channel: Channel of the message to remove all reactions.
        :param message: Message to remove all reactions.
        :param emoji: Emoji to remove all reactions.
        :type emoji: Union[str, Emoji]
        """
        return self.http.delete_all_reactions_emoji(int(channel), int(message), from_emoji(emoji))

    def edit_message(self,
                     channel: Channel.TYPING,
                     message: Message.TYPING,
                     *,
                     content: Optional[str] = EmptyObject,
                     embed: Optional[Union[Embed, dict]] = EmptyObject,
                     embeds: Optional[List[Union[Embed, dict]]] = EmptyObject,
                     file: Optional[FILE_TYPE] = EmptyObject,
                     files: Optional[List[FILE_TYPE]] = EmptyObject,
                     allowed_mentions: Optional[Union[AllowedMentions, dict]] = EmptyObject,
                     attachments: Optional[List[Union[Attachment, dict]]] = EmptyObject,
                     component: Optional[Union[dict, Component]] = EmptyObject,
                     components: Optional[List[Union[dict, Component]]] = EmptyObject) -> Message.RESPONSE:
        """
        Edits message.

        .. note::
            All keyword arguments are can be both optional and ``None``. Passing ``None`` will remove the related item, and not passing will keep it as original state.

        :param channel: Channel of the message to edit.
        :param message: Message to edit.
        :param Optional[str] content: Content to edit.
        :param embed: Embed to edit.
        :type embed: Optional[Union[Embed, dict]]
        :param embeds: Embeds to edit.
        :type embeds: Optional[List[Union[Embed, dict]]]
        :param Optional[FILE_TYPE] file: File to add.
        :param Optional[List[FILE_TYPE]] files: Files to add.
        :param allowed_mentions: Allowed mentions of the message.
        :type allowed_mentions: Optional[Union[AllowedMentions, dict]]
        :param attachments: Attachments to keep.
        :type attachments: Optional[List[Union[Attachment, dict]]]
        :param component: Component of the message to edit.
        :type component: Optional[Union[dict, Component]]
        :param components: Components of the message to edit.
        :type components: Optional[List[Union[dict, Component]]]
        :return: :class:`~.Message`
        """
        if files and file:
            raise TypeError("you can't pass both file and files.")
        if file is None or files is None:
            files = None
        else:
            if file:
                files = [file]
            if files:
                for x in range(len(files)):
                    sel = files[x]
                    if isinstance(sel, str):
                        files[x] = open(sel, "rb")
        if embed and embeds:
            raise TypeError("you can't pass both embed and embeds.")
        if embed is None or embeds is None:
            embeds = None
        else:
            if embed:
                embeds = [embed]
            if embeds:
                embeds = [x if isinstance(x, dict) else x.to_dict() for x in embeds]
        _att = []
        if attachments:
            for x in attachments:
                if not isinstance(x, dict):
                    x = x.to_dict()
                _att.append(x)
        if component and components:
            raise TypeError("you can't pass both component and components.")
        if component is None or components is None:
            components = None
        else:
            if component:
                components = [component]
            if components:
                components = [*map(lambda n: n if isinstance(n, dict) else n.to_dict(), components)]
        params = {"channel_id": int(channel),
                  "message_id": int(message),
                  "content": content,
                  "embeds": embeds,
                  "flags": EmptyObject,
                  "allowed_mentions": self.get_allowed_mentions(allowed_mentions),
                  "attachments": _att,
                  "components": components}
        if files:
            params["files"] = files
        try:
            msg = self.http.edit_message(**params) if not files else self.http.edit_message_with_files(**params)
            if isinstance(msg, dict):
                msg = Message.create(self, msg)
            return wrap_to_async(Message, self, msg)
        finally:
            if files:
                [x.close() for x in files]

    def delete_message(self,
                       channel: Channel.TYPING,
                       message: Message.TYPING,
                       *,
                       reason: Optional[str] = None):
        """
        Deletes message.

        :param channel: Channel of the message to delete.
        :param message: Message to delete.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.delete_message(int(channel), int(message), reason=reason)

    def bulk_delete_messages(self, channel: Channel.TYPING, *messages: Message.TYPING, reason: Optional[str] = None):
        """
        Bulk deletes messages.

        :param channel: Channel of the messages to delete.
        :param messages: Messages to delete.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.bulk_delete_messages(int(channel), list(map(int, messages)), reason=reason)

    def edit_channel_permissions(self, channel: Channel.TYPING, overwrite: Overwrite, *, reason: Optional[str] = None):
        """
        Edits channel permissions.

        :param channel: Chanel to edit response.
        :param Overwrite overwrite: Permission overwrite to edit.
        :param Optional[str] reason: Reason of the action.
        """
        ow_dict = overwrite.to_dict()
        return self.http.edit_channel_permissions(int(channel), ow_dict["id"], ow_dict["allow"], ow_dict["deny"], ow_dict["type"], reason=reason)

    def request_channel_invites(self, channel: Channel.TYPING) -> Invite.RESPONSE_AS_LIST:
        """
        Requests channel invites.

        :param channel: Channel to request invites.
        :return: :class:`~.Invite`
        """
        invites = self.http.request_channel_invites(int(channel))
        if isinstance(invites, list):
            return [Invite(self, x) for x in invites]
        return wrap_to_async(Invite, self, invites, as_create=False)

    def create_channel_invite(self,
                              channel: Channel.TYPING,
                              *,
                              max_age: Optional[int] = None,
                              max_uses: Optional[int] = None,
                              temporary: Optional[bool] = None,
                              unique: Optional[bool] = None,
                              target_type: Optional[Union[int, InviteTargetTypes]] = None,
                              target_user: Optional[User.TYPING] = None,
                              target_application: Optional[Application.TYPING] = None,
                              reason: Optional[str] = None) -> Invite.RESPONSE:
        """
        Creates channel invite.

        :param channel: Channel to request invite.
        :param Optional[int] max_age: Maximum age of the invite.
        :param Optional[int] max_uses: Maximum use count of the invite.
        :param Optional[bool] temporary: Whether this invite is temporary, meaning user will be kicked if role is not added.
        :param Optional[bool] unique: Whether this invite is unique, meaning new code will be generated even if there is invite with same options.
        :param target_type: Target type of the voice channel invite.
        :type target_type: Optional[Union[int, InviteTargetTypes]]
        :param target_user: Target user of the invite.
        :param target_application: Target application of the invite.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Invite`
        """
        invite = self.http.create_channel_invite(int(channel), max_age, max_uses, temporary, unique, int(target_type),
                                                 int(target_user) if target_user is not None else target_user,
                                                 int(target_application) if target_application is not None else target_application, reason=reason)
        if isinstance(invite, dict):
            return Invite(self, invite)
        return wrap_to_async(Invite, self, invite, as_create=False)

    def delete_channel_permission(self, channel: Channel.TYPING, overwrite: Union[Overwrite.TYPING, User, Role], *, reason: Optional[str] = None):
        """
        Deletes channel permission.

        :param channel: Channel to delete permission.
        :param overwrite: Target overwrite to delete. Accepts ID of the user or role.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.delete_channel_permission(int(channel), int(overwrite), reason=reason)

    def follow_news_channel(self, channel: Channel.TYPING, target_channel: Channel.TYPING) -> FollowedChannel.RESPONSE:
        """
        Follows news channel to target channel.

        :param channel: Channel to follow.
        :param target_channel: Channel to receive published messages.
        :return: :class:`~.FollowedChannel`
        """
        fc = self.http.follow_news_channel(int(channel), str(target_channel))
        if isinstance(fc, dict):
            return FollowedChannel(self, fc)
        return wrap_to_async(FollowedChannel, self, fc, as_create=False)

    def trigger_typing_indicator(self, channel: Channel.TYPING):
        """
        Triggers ``<client> is typing...`` on channel.

        :param channel: Channel to trigger typing.
        """
        return self.http.trigger_typing_indicator(int(channel))

    def request_pinned_messages(self, channel: Channel.TYPING) -> Message.RESPONSE_AS_LIST:
        """
        Requests pinned messages of the channel.

        :param channel: Channel to request pinned messages.
        :return: List[:class:`~.Message`]
        """
        msgs = self.http.request_pinned_messages(int(channel))
        if isinstance(msgs, list):
            return [Message.create(self, x) for x in msgs]
        return wrap_to_async(Message, self, msgs)

    def pin_message(self, channel: Channel.TYPING, message: Message.TYPING, *, reason: Optional[str] = None):
        """
        Pins message to the channel.

        :param channel: Channel to pin message.
        :param message: Message to pin.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.pin_message(int(channel), int(message), reason=reason)

    def unpin_message(self, channel: Channel.TYPING, message: Message.TYPING, *, reason: Optional[str] = None):
        """
        Unpins message from the channel.

        :param channel: Channel to unpin the message.
        :param message: Message to unpin.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.unpin_message(int(channel), int(message), reason=reason)

    def group_dm_add_recipient(self,
                               channel: Channel.TYPING,
                               user: User.TYPING,
                               access_token: str,
                               nick: str):
        """
        Adds recipient to the group DM.

        :param channel: Group DM channel to add recipient.
        :param user: Recipient to add.
        :param str access_token: OAuth2 access token to use.
        :param str nick: Nickname to assign.
        """
        return self.http.group_dm_add_recipient(int(channel), int(user), access_token, nick)

    def group_dm_remove_recipient(self,
                                  channel: Channel.TYPING,
                                  user: User.TYPING):
        """
        Removes recipient to the group DM.

        :param channel: Group DM channel to remove recipient.
        :param user: Recipient to remove.
        """
        return self.http.group_dm_remove_recipient(int(channel), int(user))

    def start_thread(self,
                     channel: Channel.TYPING,
                     message: Optional[Message.TYPING] = None,
                     *,
                     name: str,
                     auto_archive_duration: int,
                     thread_type: Union[ChannelTypes, int] = None,
                     invitable: bool = None,
                     reason: Optional[str] = None) -> Channel.RESPONSE:
        """
        Starts new thread.

        .. note::
            If ``message`` param is passed, type of thread will be always public regardless of what you've set to.

        :param channel: Channel to create thread.
        :param message: Message to create thread from.
        :param str name: Name of the thread.
        :param int auto_archive_duration: When to archive thread in minutes.
        :param thread_type: Type of thread.
        :type thread_type: Union[ChannelTypes, int]
        :param bool invitable: Whether this thread can be invitable.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        channel = self.http.start_thread_with_message(int(channel), int(message), name, auto_archive_duration, reason=reason) if message else \
            self.http.start_thread_without_message(int(channel), name, auto_archive_duration, int(thread_type), invitable, reason=reason)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def join_thread(self, channel: Channel.TYPING):
        """
        Joins to thread.

        :param channel: Thread to join.
        """
        return self.http.join_thread(int(channel))

    def add_thread_member(self, channel: Channel.TYPING, user: User.TYPING):
        """
        Adds member to thread.

        :param channel: Thread to add member.
        :param user: User to add.
        """
        return self.http.add_thread_member(int(channel), int(user))

    def leave_thread(self, channel: Channel.TYPING):
        """
        Leaves thread.

        :param channel: Thread to leave.
        """
        return self.http.leave_thread(int(channel))

    def remove_thread_member(self, channel: Channel.TYPING, user: User.TYPING):
        """
        Removes member from thread.

        :param channel: Thread to remove member.
        :param user: User to remove.
        """
        return self.http.remove_thread_member(int(channel), int(user))

    def list_thread_members(self, channel: Channel.TYPING) -> ThreadMember.RESPONSE_AS_LIST:
        """
        Lists members of thread.

        :param channel: Thread to list members.
        :return: List[:class:`~.ThreadMember`]
        """
        members = self.http.list_thread_members(int(channel))
        if isinstance(members, list):
            return [ThreadMember(self, x) for x in members]
        return wrap_to_async(ThreadMember, self, members, as_create=False)

    def list_active_threads(self, channel: Channel.TYPING) -> ListThreadsResponse.RESPONSE:
        """
        Lists threads in channel that is active.

        :param channel: Channel to list threads.
        :return: :class:`~.ListThreadsResponse`
        """
        resp = self.http.list_active_threads(int(channel))
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def list_public_archived_threads(self,
                                     channel: Channel.TYPING,
                                     *,
                                     before: Optional[Union[str, datetime.datetime]] = None,
                                     limit: Optional[int] = None) -> ListThreadsResponse.RESPONSE:
        """
        Lists threads in channel that is archived and public.

        :param channel: Channel to list threads.
        :param before: Timestamp to show threads before.
        :type before: Optional[Union[str, datetime.datetime]]
        :param Optional[int] limit: Limit of the number of the threads.
        :return: :class:`~.ListThreadsResponse`
        """
        resp = self.http.list_public_archived_threads(int(channel), before, limit)
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def list_private_archived_threads(self,
                                      channel: Channel.TYPING,
                                      *,
                                      before: Optional[Union[str, datetime.datetime]] = None,
                                      limit: Optional[int] = None) -> ListThreadsResponse.RESPONSE:
        """
        Lists threads in channel that is archived and private.

        :param channel: Channel to list threads.
        :param before: Timestamp to show threads before.
        :type before: Optional[Union[str, datetime.datetime]]
        :param Optional[int] limit: Limit of the number of the threads.
        :return: :class:`~.ListThreadsResponse`
        """
        resp = self.http.list_private_archived_threads(int(channel), before, limit)
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def list_joined_private_archived_threads(self,
                                             channel: Channel.TYPING,
                                             *,
                                             before: Union[str, datetime.datetime] = None,
                                             limit: int = None) -> ListThreadsResponse.RESPONSE:
        """
        Lists threads in channel that is archived and private and joined.

        :param channel: Channel to list threads.
        :param before: Timestamp to show threads before.
        :type before: Optional[Union[str, datetime.datetime]]
        :param Optional[int] limit: Limit of the number of the threads.
        :return: :class:`~.ListThreadsResponse`
        """
        resp = self.http.list_joined_private_archived_threads(int(channel), before, limit)
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    # Emoji

    def list_guild_emojis(self, guild: Guild.TYPING) -> Emoji.RESPONSE_AS_LIST:
        """
        Lists emojis of the guild.

        :param guild: Guild to list emojis.
        :return: List[:class:`~.Emoji`]
        """
        resp = self.http.list_guild_emojis(int(guild))
        if isinstance(resp, list):
            return [Emoji(self, x) for x in resp]
        return wrap_to_async(Emoji, self, resp, as_create=False)

    def request_guild_emoji(self, guild: Guild.TYPING, emoji: Emoji.TYPING) -> Emoji.RESPONSE:
        """
        Requests emoji from guild.

        :param guild: Guild to request emoji.
        :param emoji: Emoji to request.
        :return: :class:`~.Emoji`
        """
        resp = self.http.request_guild_emoji(int(guild), int(emoji))
        if isinstance(resp, dict):
            return Emoji(self, resp)
        return wrap_to_async(Emoji, self, resp, as_create=False)

    def create_guild_emoji(self,
                           guild: Guild.TYPING,
                           *,
                           name: str,
                           image: str,
                           roles: Optional[List[Role.TYPING]] = None,
                           reason: Optional[str] = None) -> Emoji.RESPONSE:
        """
        Creates emoji from guild.

        :param guild: Guild to create emoji.
        :param str name: Name of the emoji.
        :param str image: Image of the emoji.
        :param roles: Roles that are allowed to use this emoji.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Emoji`
        """
        resp = self.http.create_guild_emoji(int(guild), name, image, [str(int(x)) for x in roles or []], reason=reason)
        if isinstance(resp, dict):
            return Emoji(self, resp)
        return wrap_to_async(Emoji, self, resp, as_create=False)

    def modify_guild_emoji(self,
                           guild: Guild.TYPING,
                           emoji: Emoji.TYPING,
                           *,
                           name: Optional[str] = EmptyObject,
                           roles: Optional[List[Role.TYPING]] = EmptyObject,
                           reason: Optional[str] = None) -> Emoji.RESPONSE:
        """
        Modifies emoji of the guild.

        :param guild: Guild to edit emoji.
        :param emoji: Emoji to edit.
        :param Optional[str] name: Name to edit.
        :param roles: Roles to edit.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Emoji`
        """
        resp = self.http.modify_guild_emoji(int(guild), int(emoji), name, [str(int(x)) for x in roles] if roles else roles, reason=reason)
        if isinstance(resp, dict):
            return Emoji(self, resp)
        return wrap_to_async(Emoji, self, resp, as_create=False)

    def delete_guild_emoji(self, guild: Guild.TYPING, emoji: Emoji.TYPING, reason: Optional[str] = None):
        """
        Deletes emoji of the guild.

        :param guild: Guild to delete emoji.
        :param emoji: Emoji to delete.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.delete_guild_emoji(int(guild), int(emoji), reason=reason)

    # Guild

    def create_guild(self,
                     name: str,
                     *,
                     icon: Optional[str] = None,
                     verification_level: Optional[Union[int, VerificationLevel]] = None,
                     default_message_notifications: Optional[Union[int, DefaultMessageNotificationLevel]] = None,
                     explicit_content_filter: Optional[Union[int, ExplicitContentFilterLevel]] = None,
                     roles: Optional[List[dict]] = None,  # TODO: role and channel generator
                     channels: Optional[List[dict]] = None,
                     afk_channel_id: Optional[Snowflake.TYPING] = None,
                     afk_timeout: Optional[int] = None,
                     system_channel_id: Optional[Snowflake.TYPING] = None,
                     system_channel_flags: Optional[Union[int, SystemChannelFlags]] = None) -> Guild.RESPONSE:
        """
        Creates guild.

        .. note::
            You can create image data for ``icon`` using :func:`.utils.to_image_data`.

        :param str name: Name of the guild.
        :param Optional[str] icon: Icon of the guild.
        :param verification_level: Verification level of the guild.
        :type verification_level: Optional[Union[int, VerificationLevel]]
        :param default_message_notifications: Default notifications level of the guild.
        :type default_message_notifications: Optional[Union[int, DefaultMessageNotificationLevel]]
        :param explicit_content_filter: Default explicit content filter level of the guild.
        :type explicit_content_filter: Optional[Union[int, ExplicitContentFilterLevel]]
        :param Optional[List[dict]] roles: Roles of the guild.
        :param Optional[List[dict]] channels: Channels of the guild.
        :param afk_channel_id: Temporary ID of the afk channel.
        :param Optional[int] afk_timeout: Timeout of the afk channel.
        :param system_channel_id: Temporary ID of the system channel.
        :param system_channel_flags: Flags of the system channel.
        :type system_channel_flags: Optional[Union[int, SystemChannelFlags]]
        :return: :class:`~.Guild`
        """
        kwargs = {"name": name}
        if icon is not None:
            kwargs["icon"] = icon
        if verification_level is not None:
            kwargs["verification_level"] = int(verification_level)
        if default_message_notifications is not None:
            kwargs["default_message_notifications"] = int(default_message_notifications)
        if explicit_content_filter is not None:
            kwargs["explicit_content_filter"] = int(explicit_content_filter)
        if roles is not None:
            kwargs["roles"] = roles
        if channels is not None:
            kwargs["channels"] = channels
        if afk_channel_id is not None:
            kwargs["afk_channel_id"] = str(int(afk_channel_id))
        if afk_timeout is not None:
            kwargs["afk_timeout"] = afk_timeout
        if system_channel_id is not None:
            kwargs["system_channel_id"] = str(int(system_channel_id))
        if system_channel_flags is not None:
            kwargs["system_channel_flags"] = int(system_channel_flags)
        resp = self.http.create_guild(**kwargs)
        if isinstance(resp, dict):
            return Guild.create(self, resp, ensure_cache_type="guild")
        return wrap_to_async(Guild, self, resp, ensure_cache_type="guild")

    def request_guild(self, guild: Guild.TYPING, with_counts: bool = False) -> Guild.RESPONSE:
        """
        Requests guild.

        :param guild: Guild to request.
        :param with_counts: Whether to include member count and presence count.
        :return: :class:`~.Guild`
        """
        resp = self.http.request_guild(int(guild), with_counts)
        if isinstance(resp, dict):
            return Guild.create(self, resp, ensure_cache_type="guild")
        return wrap_to_async(Guild, self, resp, ensure_cache_type="guild")

    def request_guild_preview(self, guild: Guild.TYPING) -> GuildPreview.RESPONSE:
        """
        Requests guild preview.

        :param guild: Guild to request preview.
        :return: :class:`~.GuildPreview`
        """
        resp = self.http.request_guild_preview(int(guild))
        if isinstance(resp, dict):
            return GuildPreview(self, resp)
        return wrap_to_async(GuildPreview, self, resp)

    def modify_guild(self,
                     guild: Guild.TYPING,
                     *,
                     name: Optional[str] = None,
                     verification_level: Optional[Union[int, VerificationLevel]] = EmptyObject,
                     default_message_notifications: Optional[Union[int, DefaultMessageNotificationLevel]] = EmptyObject,
                     explicit_content_filter: Optional[Union[int, ExplicitContentFilterLevel]] = EmptyObject,
                     afk_channel: Optional[Channel.TYPING] = EmptyObject,
                     afk_timeout: Optional[int] = None,
                     icon: Optional[str] = EmptyObject,
                     owner: Optional[User.TYPING] = None,
                     splash: Optional[str] = EmptyObject,
                     discovery_splash: Optional[str] = EmptyObject,
                     banner: Optional[str] = EmptyObject,
                     system_channel: Optional[Channel.TYPING] = EmptyObject,
                     system_channel_flags: Optional[Union[int, SystemChannelFlags]] = None,
                     rules_channel: Optional[Channel.TYPING] = EmptyObject,
                     public_updates_channel: Optional[Channel.TYPING] = EmptyObject,
                     preferred_locale: Optional[str] = EmptyObject,
                     features: Optional[List[str]] = None,
                     description: Optional[str] = EmptyObject,
                     reason: Optional[str] = None) -> Guild.RESPONSE:
        """
        Modifies guild.

        .. note::
            You can create image data for ``icon``, ``splash``, ``discovery_splash``, and ``banner`` using :func:`.utils.to_image_data`.

        :param guild: Guild to modify.
        :param Optional[str] name: Name of the guild.
        :param verification_level: Verification level of the guild.
        :type verification_level: Optional[Union[int, VerificationLevel]]
        :param default_message_notifications: Default notifications level of the guild.
        :type default_message_notifications: Optional[Union[int, DefaultMessageNotificationLevel]]
        :param explicit_content_filter: Default explicit content filter level of the guild.
        :type explicit_content_filter: Optional[Union[int, ExplicitContentFilterLevel]]
        :param afk_channel: AFK channel of the guild.
        :param Optional[int] afk_timeout: Timeout of the AFK channel.
        :param Optional[str] icon: Icon of the guild.
        :param owner: Owner of the guild.
        :param Optional[str] splash: Splash image of the guild.
        :param Optional[str] discovery_splash: Discovery splash image of the guild.
        :param Optional[str] banner: Banner of the guild.
        :param system_channel: System channel of the guild.
        :param system_channel_flags: Flags of the system channel.
        :type system_channel_flags: Optional[Union[int, SystemChannelFlags]]
        :param rules_channel: Rules channel of the guild.
        :param public_updates_channel: Public update channel of the guild.
        :param Optional[str] preferred_locale: Preferred locale of the guild.
        :param Optional[List[str]] features: Features of the guild.
        :param Optional[str] description: Description of the guild.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Guild`
        """
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if verification_level is not EmptyObject:
            kwargs["verification_level"] = int(verification_level)
        if default_message_notifications is not EmptyObject:
            kwargs["default_message_notifications"] = int(default_message_notifications) if default_message_notifications is not None else default_message_notifications
        if explicit_content_filter is not EmptyObject:
            kwargs["explicit_content_filter"] = int(explicit_content_filter)
        if afk_channel is not EmptyObject:
            kwargs["afk_channel_id"] = str(int(afk_channel)) if afk_channel is not None else afk_channel
        if afk_timeout is not None:
            kwargs["afk_timeout"] = afk_timeout
        if icon is not EmptyObject:
            kwargs["icon"] = icon
        if owner is not None:
            kwargs["owner_id"] = str(int(owner))
        if splash is not EmptyObject:
            kwargs["splash"] = splash
        if discovery_splash is not EmptyObject:
            kwargs["discovery_splash"] = discovery_splash
        if banner is not EmptyObject:
            kwargs["banner"] = banner
        if system_channel is not EmptyObject:
            kwargs["system_channel_id"] = str(int(system_channel)) if system_channel is not None else system_channel
        if system_channel_flags is not None:
            kwargs["system_channel_flags"] = int(system_channel_flags)
        if rules_channel is not EmptyObject:
            kwargs["rules_channel_id"] = str(int(rules_channel)) if rules_channel is not None else rules_channel
        if public_updates_channel is not EmptyObject:
            kwargs["public_updates_channel_id"] = str(int(public_updates_channel)) if public_updates_channel is not None else public_updates_channel
        if preferred_locale is not EmptyObject:
            kwargs["preferred_locale"] = preferred_locale
        if features is not None:
            kwargs["features"] = features
        if description is not EmptyObject:
            kwargs["description"] = description
        resp = self.http.modify_guild(int(guild), **kwargs, reason=reason)
        if isinstance(resp, dict):
            return Guild.create(self, resp, ensure_cache_type="guild")
        return wrap_to_async(Guild, self, resp, ensure_cache_type="guild")

    def delete_guild(self, guild: Guild.TYPING):
        """
        Deletes guild. Client must be an owner to delete.

        :param guild: Guild to delete.
        """
        return self.http.delete_guild(int(guild))

    def request_guild_channels(self, guild: Guild.TYPING) -> Channel.RESPONSE_AS_LIST:
        """
        Requests channels of the guild.

        :param guild: Guild to request channels.
        :return: List[:class:`~.Channel`]
        """
        channels = self.http.request_guild_channels(int(guild))
        if isinstance(channels, list):
            return [Channel.create(self, x) for x in channels]
        return wrap_to_async(Channel, self, channels)

    def create_guild_channel(self,
                             guild: Guild.TYPING,
                             name: str,
                             *,
                             channel_type: Optional[Union[int, ChannelTypes]] = None,
                             topic: Optional[str] = None,
                             bitrate: Optional[int] = None,
                             user_limit: Optional[int] = None,
                             rate_limit_per_user: Optional[int] = None,
                             position: Optional[int] = None,
                             permission_overwrites: Optional[Union[dict, Overwrite]] = None,
                             parent: Optional[Channel.TYPING] = None,
                             nsfw: Optional[bool] = None,
                             reason: Optional[str] = None) -> Channel.RESPONSE:
        """
        Creates channel in guild.

        :param guild: Guild to create channel.
        :param str name: Name of the channel.
        :param channel_type: Type of the channel.
        :type channel_type: Optional[Union[int, ChannelTypes]]
        :param Optional[str] topic: Topic of the channel.
        :param Optional[int] bitrate: Bitrate of the channel.
        :param user_limit: User limit of the channel.
        :param Optional[int] rate_limit_per_user: Slowmode of the channel.
        :param Optional[int] position: Position of the channel.
        :param permission_overwrites: Permission overwrites of the channel.
        :type permission_overwrites: Optional[Union[dict, Overwrite]]
        :param parent: Parent category of the channel.
        :param Optional[bool] nsfw: Whether this channel is NSFW.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Channel`
        """
        if isinstance(parent, Channel) and not parent.type.guild_category:
            raise TypeError("parent must be category channel.")
        kwargs = {"name": name}
        if channel_type is not None:
            kwargs["channel_type"] = int(channel_type)
        if topic is not None:
            kwargs["topic"] = topic
        if bitrate is not None:
            kwargs["bitrate"] = bitrate
        if user_limit is not None:
            kwargs["user_limit"] = user_limit
        if rate_limit_per_user is not None:
            kwargs["rate_limit_per_user"] = rate_limit_per_user
        if position is not None:
            kwargs["position"] = position
        if permission_overwrites is not None:
            kwargs["permission_overwrites"] = permission_overwrites.to_dict() if isinstance(permission_overwrites, Overwrite) else permission_overwrites
        if parent is not None:
            kwargs["parent_id"] = str(int(parent))
        if nsfw is not None:
            kwargs["nsfw"] = nsfw
        resp = self.http.create_guild_channel(int(guild), **kwargs, reason=reason)
        if isinstance(resp, dict):
            return Channel.create(self, resp)
        return wrap_to_async(Channel, self, resp)

    def modify_guild_channel_positions(self, guild: Guild.TYPING, *params: dict, reason: Optional[str] = None):
        """
        Modifies position of the guild channels.

        :param guild: Guild to edit channel positions.
        :param params: Positions of the channel. Use :meth:`~.Channel.to_position_param`.
        :param Optional[str] reason: Reason of the action.
        """
        # You can get params by using Channel.to_position_param(...)
        return self.http.modify_guild_channel_positions(int(guild), [*params], reason=reason)

    def list_active_threads_as_guild(self, guild: Guild.TYPING) -> ListThreadsResponse.RESPONSE:
        """
        Lists active threads in guild.

        :param guild: Guild to get active threads.
        :return: :class:`~.ListThreadsResponse`
        """
        resp = self.http.list_active_threads_as_guild(int(guild))
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def request_guild_member(self, guild: Guild.TYPING, user: Union[GuildMember.TYPING, User.TYPING]) -> GuildMember.RESPONSE:
        """
        Requests member of the guild.

        :param guild: Guild to request member
        :param user: Member to request.
        :return: :class:`~.GuildMember`
        """
        resp = self.http.request_guild_member(int(guild), int(user))
        if isinstance(resp, dict):
            return GuildMember.create(self, resp, guild_id=int(guild))
        return wrap_to_async(GuildMember, self, resp, guild_id=int(guild))

    def list_guild_members(self, guild: Guild.TYPING, limit: Optional[int] = None, after: Optional[Union[GuildMember.TYPING, User.TYPING]] = None) -> GuildMember.RESPONSE_AS_LIST:
        """
        Lists members of the guild.

        :param guild: Guild to list members.
        :param Optional[int] limit: Limit of the count of the members.
        :param after: Member ID to list after.
        :return: List[:class:`~.GuildMember`]
        """
        resp = self.http.list_guild_members(int(guild), limit, after)
        if isinstance(resp, list):
            return [GuildMember.create(self, x, guild_id=int(guild)) for x in resp]
        return wrap_to_async(GuildMember, self, resp, guild_id=int(guild))

    def search_guild_members(self, guild: Guild.TYPING, query: str, limit: Optional[int] = None) -> GuildMember.RESPONSE_AS_LIST:
        """
        Searches members of the guild using query given. This will search for member nickname or username that starts with query.

        :param guild: Guild to search members
        :param str query: Query to use for searching.
        :param Optional[int] limit: Limit of the count of the results.
        :return: List[:class:`~.GuildMember`]
        """
        resp = self.http.search_guild_members(int(guild), query, limit)
        if isinstance(resp, list):
            return [GuildMember.create(self, x, guild_id=int(guild)) for x in resp]
        return wrap_to_async(GuildMember, self, resp, guild_id=int(guild))

    def add_guild_member(self,
                         guild: Guild.TYPING,
                         user: User.TYPING,
                         access_token: str,
                         nick: Optional[str] = None,
                         roles: Optional[List[Role.TYPING]] = None,
                         mute: Optional[bool] = None,
                         deaf: Optional[bool] = None) -> GuildMember.RESPONSE:
        """
        Adds member to guild. Requires OAuth2 access token with ``guilds.join`` scope.

        :param guild: Guild to add member.
        :param user: User that will be added.
        :param str access_token: OAuth2 access token with ``guilds.join`` scope.
        :param Optional[str] nick: Nickname of the member.
        :param roles: Roles of the member.
        :param Optional[bool] mute: Whether this member is muted in voice channels.
        :param Optional[bool] deaf: Whether this member is deafened in voice channels.
        :return: :class:`~.GuildMember`
        """
        kwargs = {"access_token": access_token}
        if nick is not None:
            kwargs["nick"] = nick
        if roles is not None:
            kwargs["roles"] = [str(int(x)) for x in roles]
        if mute is not None:
            kwargs["mute"] = mute
        if deaf is not None:
            kwargs["deaf"] = deaf
        resp = self.http.add_guild_member(int(guild), int(user), **kwargs)
        if isinstance(resp, dict):
            return GuildMember.create(self, resp, guild_id=int(guild))
        elif resp is None:
            return resp
        return wrap_to_async(GuildMember, self, resp, guild_id=int(guild))

    def modify_guild_member(self,
                            guild: Guild.TYPING,
                            user: User.TYPING,
                            *,
                            nick: Optional[str] = EmptyObject,
                            roles: Optional[List[Role.TYPING]] = EmptyObject,
                            mute: Optional[bool] = EmptyObject,
                            deaf: Optional[bool] = EmptyObject,
                            channel: Optional[Channel.TYPING] = EmptyObject,
                            reason: Optional[str] = None) -> GuildMember.RESPONSE:
        """
        Modifies guild member.

        :param guild: Guild of the member to modify.
        :param user: Member to modify
        :param Optional[str] nick: Nickname to modify.
        :param roles: Roles to modify.
        :param Optional[bool] mute: Whether this member is muted.
        :param Optional[bool] deaf: Whether this member is deafen.
        :param channel: Channel to move user to.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.GuildMember`
        """
        kwargs = {}
        if nick is not EmptyObject:
            kwargs["nick"] = nick
        if roles is not EmptyObject:
            kwargs["roles"] = [str(int(x)) for x in roles] if roles else roles
        if mute is not EmptyObject:
            kwargs["mute"] = mute
        if deaf is not EmptyObject:
            kwargs["deaf"] = deaf
        if channel is not EmptyObject:
            kwargs["channel_id"] = int(channel) if channel else channel  # noqa
        resp = self.http.modify_guild_member(int(guild), int(user), **kwargs, reason=reason)
        if isinstance(resp, dict):
            return GuildMember.create(self, resp, guild_id=int(guild))
        return wrap_to_async(GuildMember, self, resp, guild_id=int(guild))

    def modify_current_user_nick(self, guild: Guild.TYPING, nick: Optional[str] = EmptyObject, *, reason: Optional[str] = None):
        """
        Modifies nickname of the current client user.

        :param guild: Guild to modify nick at.
        :param Optional[str] nick: Nickname to modify.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.modify_current_user_nick(int(guild), nick, reason=reason)

    def add_guild_member_role(self,
                              guild: Guild.TYPING,
                              user: User.TYPING,
                              role: Role.TYPING,
                              *,
                              reason: Optional[str] = None):
        """
        Adds role to guild member.

        :param guild: Guild of the member.
        :param user: Member to add role.
        :param role: Role to add.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.add_guild_member_role(int(guild), int(user), int(role), reason=reason)

    def remove_guild_member_role(self,
                                 guild: Guild.TYPING,
                                 user: User.TYPING,
                                 role: Role.TYPING,
                                 *,
                                 reason: Optional[str] = None):
        """
        Removes role of the guild member.

        :param guild: Guild to remove member's role.
        :param user: Member to remove role.
        :param role: Role to remove.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.remove_guild_member_role(int(guild), int(user), int(role), reason=reason)

    def remove_guild_member(self, guild: Guild.TYPING, user: User.TYPING):
        """
        Removes guild member.

        :param guild: Guild to remove member.
        :param user: Member to remove.
        """
        return self.http.remove_guild_member(int(guild), int(user))

    @property
    def kick(self):
        """Alias of :meth:`.remove_guild_member`."""
        return self.remove_guild_member

    def request_guild_bans(self, guild: Guild.TYPING) -> Ban.RESPONSE_AS_LIST:
        """
        Requests bans of the guild.

        :param guild: Guild to request bans.
        :return: List[:class:`~.Ban`]
        """
        resp = self.http.request_guild_bans(int(guild))
        if isinstance(resp, list):
            return [Ban(self, x) for x in resp]
        return wrap_to_async(Ban, self, resp, as_create=False)

    def request_guild_ban(self, guild: Guild.TYPING, user: User.TYPING) -> Ban.RESPONSE:
        """
        Requests ban of the user in the guild.

        :param guild: Guild to request ban.
        :param user: User to request ban of.
        :return: :class:`~.Ban`
        """
        resp = self.http.request_guild_ban(int(guild), int(user))
        if isinstance(resp, dict):
            return Ban(self, resp)
        return wrap_to_async(Ban, self, resp, as_create=False)

    def create_guild_ban(self,
                         guild: Guild.TYPING,
                         user: User.TYPING,
                         *,
                         delete_message_days: Optional[int] = None,
                         reason: Optional[str] = None):
        """
        Creates guild ban.

        :param guild: Guild to create ban.
        :param user: User to ban.
        :param Optional[int] delete_message_days: Days of messages sent by the user to delete.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.create_guild_ban(int(guild), int(user), delete_message_days, reason)

    @property
    def ban(self):
        """Alias of :meth:`.create_guild_ban`."""
        return self.create_guild_ban

    def remove_guild_ban(self,
                         guild: Guild.TYPING,
                         user: User.TYPING,
                         *,
                         reason: Optional[str] = None):
        """
        Removes guild ban.

        :param guild: Guild to remove ban.
        :param user: User to remove ban.
        :param Optional[str] reason: Reason of the action.
        """
        return self.remove_guild_ban(int(guild), int(user), reason=reason)

    def request_guild_roles(self, guild: Guild.TYPING) -> Role.RESPONSE_AS_LIST:
        """
        Requests roles of the guild.

        :param guild: Guild to request roles.
        :return: List[:class:`~.Role`]
        """
        resp = self.http.request_guild_roles(int(guild))
        if isinstance(resp, list):
            return [Role.create(self, x, guild_id=int(guild)) for x in resp]
        return wrap_to_async(Role, self, resp, guild_id=int(guild))

    def create_guild_role(self,
                          guild: Guild.TYPING,
                          *,
                          name: Optional[str] = None,
                          permissions: Optional[Union[int, str, PermissionFlags]] = None,
                          color: Optional[int] = None,
                          hoist: Optional[bool] = None,
                          mentionable: Optional[bool] = None,
                          reason: Optional[str] = None) -> Role.RESPONSE:
        """
        Creates role in the guild.

        :param guild: Guild to create role.
        :param Optional[str] name: Name of the role.
        :param permissions: Permissions this role will have.
        :type permissions: Optional[Union[int, str, PermissionFlags]]
        :param Optional[int] color: Color of the role.
        :param Optional[bool] hoist: Whether this role is hoist.
        :param Optional[bool] mentionable: Whether this role is mentionable.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Role`
        """
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if permissions is not None:
            kwargs["permissions"] = str(int(permissions))
        if color is not None:
            kwargs["color"] = color
        if hoist is not None:
            kwargs["hoist"] = hoist
        if mentionable is not None:
            kwargs["mentionable"] = mentionable
        resp = self.http.create_guild_role(int(guild), **kwargs, reason=reason)
        if isinstance(resp, dict):
            return Role.create(self, resp, guild_id=int(guild))
        return wrap_to_async(Role, self, resp, guild_id=int(guild))

    def modify_guild_role_positions(self, guild: Guild.TYPING, *params: dict, reason: Optional[str] = None) -> Role.RESPONSE_AS_LIST:
        """
        Modifies positions of the guild role.

        :param guild: Guild to modify positions of the role.
        :param dict params: Position data to modify. You should use :meth:`~.Role.to_position_param`.
        :param Optional[str] reason: Reason of the action.
        :return: List[:class:`~.Role`]
        """
        # You can get params by using Role.to_position_param(...)
        resp = self.http.modify_guild_role_positions(int(guild), [*params], reason=reason)
        if isinstance(resp, list):
            return [Role.create(self, x, guild_id=int(guild)) for x in resp]
        return wrap_to_async(Role, self, resp, guild_id=int(guild))

    def modify_guild_role(self,
                          guild: Guild.TYPING,
                          role: Role.TYPING,
                          *,
                          name: Optional[str] = EmptyObject,
                          permissions: Optional[Union[int, str, PermissionFlags]] = EmptyObject,
                          color: Optional[int] = EmptyObject,
                          hoist: Optional[bool] = EmptyObject,
                          mentionable: Optional[bool] = EmptyObject,
                          reason: Optional[str] = None) -> Role.RESPONSE:
        """
        Modifies role of the guild.

        :param guild: Guild to modify role.
        :param role: Role to modify.
        :param Optional[str] name: Name of the role to modify.
        :param permissions: Permissions of the role to modify.
        :type permissions: Optional[Union[int, str, PermissionFlags]]
        :param Optional[int] color: Color of the role to modify.
        :param Optional[bool] hoist: Whether this role is hoist.
        :param Optional[bool] mentionable: Whether this role is mentionable.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Role`
        """
        kwargs = {}
        if name is not EmptyObject:
            kwargs["name"] = name
        if permissions is not EmptyObject:
            kwargs["permissions"] = permissions
        if color is not EmptyObject:
            kwargs["color"] = color
        if hoist is not EmptyObject:
            kwargs["hoist"] = hoist
        if mentionable is not EmptyObject:
            kwargs["mentionable"] = mentionable
        resp = self.http.modify_guild_role(int(guild), int(role), **kwargs, reason=reason)
        if isinstance(resp, dict):
            return Role.create(self, resp, guild_id=int(guild))
        return wrap_to_async(Role, self, resp, guild_id=int(guild))

    def delete_guild_role(self, guild: Guild.TYPING, role: Role.TYPING, *, reason: Optional[str] = None):
        """
        Deletes guild role.

        :param guild: Guild to delete role.
        :param role: Role to delete.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.delete_guild_role(int(guild), int(role), reason=reason)

    def request_guild_prune_count(self, guild: Guild.TYPING, *, days: Optional[int] = None, include_roles: Optional[List[Role.TYPING]] = None) -> Union[int, Awaitable[int]]:
        """
        Requests guild prune count.

        :param guild: Guild to request prune count.
        :param Optional[int] days: Days to count prune.
        :param include_roles: Roles to include.
        :return: Calculated prune count.
        """
        if include_roles is not None:
            include_roles = [*map(str, include_roles)]
        resp = self.http.request_guild_prune_count(int(guild), days, include_roles)
        if isinstance(resp, dict):
            return resp["pruned"]

        async def wrap() -> int:
            res = await resp
            return res["pruned"]

        return wrap()

    def begin_guild_prune(self,
                          guild: Guild.TYPING,
                          *,
                          days: Optional[int] = None,
                          compute_prune_count: Optional[bool] = None,
                          include_roles: Optional[List[Role.TYPING]] = None,
                          reason: Optional[str] = None) -> Optional[Union[int, Awaitable[int]]]:
        """
        Begins guild prune.

        :param guild: Guild to prune.
        :param Optional[int] days: Days to count prune.
        :param Optional[bool] compute_prune_count:
        :param include_roles: Roles to include.
        :param Optional[str] reason: Reason of the action.
        :return: Prune count, if ``compute_prune_count`` is True.
        """
        if include_roles is not None:
            include_roles = [*map(str, include_roles)]
        resp = self.http.begin_guild_prune(int(guild), days, compute_prune_count, include_roles, reason=reason)
        if isinstance(resp, dict):
            return resp["pruned"]

        async def wrap() -> int:
            res = await resp
            return res["pruned"]

        return wrap()

    def request_guild_voice_regions(self, guild: Guild.TYPING) -> VoiceRegion.RESPONSE_AS_LIST:
        """
        Requests list of guild voice regions.

        :param guild: Guild to request voice regions.
        :return: List[:class:`~.VoiceRegion`]
        """
        resp = self.http.request_guild_voice_regions(int(guild))
        if isinstance(resp, list):
            return [VoiceRegion(x) for x in resp]
        return wrap_to_async(VoiceRegion, None, resp, as_create=False)

    def request_guild_invites(self, guild: Guild.TYPING) -> Invite.RESPONSE_AS_LIST:
        """
        Requests list of guild invites.

        :param guild: Guild to request invites.
        :return: List[:class:`~.Invite`]
        """
        resp = self.http.request_guild_invites(int(guild))
        if isinstance(resp, list):
            return [Invite(self, x) for x in resp]
        return wrap_to_async(Invite, self, resp, as_create=False)

    def request_guild_integrations(self, guild: Guild.TYPING) -> Integration.RESPONSE_AS_LIST:
        """
        Requests list of guild integrations.

        :param guild: Guild to request integrations.
        :return: List[:class:`~.Integration`]
        """
        resp = self.http.request_guild_integrations(int(guild))
        if isinstance(resp, list):
            return [Integration(self, x) for x in resp]
        return wrap_to_async(Integration, self, resp, as_create=False)

    def delete_guild_integration(self, guild: Guild.TYPING, integration: Integration.TYPING, *, reason: Optional[str] = None):
        """
        Deletes guild integration.

        :param guild: Guild to delete integration.
        :param integration: Integration to delete.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.delete_guild_integration(int(guild), int(integration), reason=reason)

    def request_guild_widget_settings(self, guild: Guild.TYPING) -> GuildWidget.RESPONSE:
        """
        Requests guild widget settings.

        :param guild: Guild to request widget settings.
        :return: :class:`~.GuildWidget`
        """
        resp = self.http.request_guild_widget_settings(int(guild))
        if isinstance(resp, dict):
            return GuildWidget(resp)
        return wrap_to_async(GuildWidget, None, resp, as_create=False)

    def modify_guild_widget(self,
                            guild: Guild.TYPING,
                            *,
                            enabled: Optional[bool] = None,
                            channel: Optional[Channel.TYPING] = EmptyObject,
                            reason: Optional[str] = None) -> GuildWidget.RESPONSE:
        """
        Modifies guild widget.

        :param guild: Guild to modify widget.
        :param Optional[bool] enabled: Whether the widget is enabled.
        :param channel: Channel of the widget.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.GuildWidget`
        """
        resp = self.http.modify_guild_widget(int(guild), enabled, channel, reason=reason)  # noqa
        if isinstance(resp, dict):
            return GuildWidget(resp)
        return wrap_to_async(GuildWidget, None, resp, as_create=False)

    def request_guild_widget(self, guild: Guild.TYPING) -> "AbstractObject.RESPONSE":
        """
        Request guild's widget.

        :param guild: Guild to request widget.
        :return: Refer https://discord.com/developers/docs/resources/guild#get-guild-widget.
        """
        # TODO: don't use AbstractObject
        from .base.model import AbstractObject
        resp = self.http.request_guild_widget(int(guild))
        if isinstance(resp, dict):
            return AbstractObject(resp)
        return wrap_to_async(AbstractObject, None, resp, as_create=False)

    def request_guild_vanity_url(self, guild: Guild.TYPING) -> "AbstractObject.RESPONSE":
        """
        Requests guild vanity URL.

        :param guild: Guild to request guild vanity URL.
        :return: Refer https://discord.com/developers/docs/resources/guild#get-guild-vanity-url.
        """
        from .base.model import AbstractObject
        resp = self.http.request_guild_vanity_url(int(guild))
        if isinstance(resp, dict):
            return AbstractObject(resp)
        return wrap_to_async(AbstractObject, None, resp, as_create=False)

    def request_guild_widget_image(self, guild: Guild.TYPING, style: Optional[WidgetStyle] = None) -> BYTES_RESPONSE:
        """
        Requests guild widget image.

        :param guild: Guild to request widget image.
        :param Optional[str] style: Style of the widget. One of "shield", "banner1", "banner2", "banner3", and "banner4".
        :return: bytes
        """
        return self.http.request_guild_widget_image(int(guild), style)

    def request_guild_welcome_screen(self, guild: Guild.TYPING) -> WelcomeScreen.RESPONSE:
        """
        Requests guild welcome screen.

        :param guild: Guild to request welcome screen.
        :return: :class:`~.WelcomeScreen`
        """
        resp = self.http.request_guild_welcome_screen(int(guild))
        if isinstance(resp, dict):
            return WelcomeScreen(resp)
        return wrap_to_async(WelcomeScreen, None, resp, as_create=False)

    def modify_guild_welcome_screen(self,
                                    guild: Guild.TYPING,
                                    *,
                                    enabled: Optional[bool] = EmptyObject,
                                    welcome_channels: Optional[List[Union[WelcomeScreenChannel, dict]]] = EmptyObject,
                                    description: Optional[str] = EmptyObject,
                                    reason: Optional[str] = None) -> WelcomeScreen.RESPONSE:
        """
        Modifies guild welcome screen.

        :param guild: Guild to modify welcome screen.
        :param Optional[bool] enabled: Whether welcome screen is enabled.
        :param welcome_channels: Welcome channels to show. You can use :meth:`~.Channel.to_welcome_screen_channel`.
        :type welcome_channels: Optional[List[Union[WelcomeScreenChannel, dict]]]
        :param Optional[str] description: Description of the welcome screen.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.WelcomeScreen`
        """
        if welcome_channels is not EmptyObject:
            welcome_channels = [x if isinstance(x, dict) else x.to_dict() for x in welcome_channels or []]
        resp = self.http.modify_guild_welcome_screen(int(guild), enabled, welcome_channels, description, reason=reason)
        if isinstance(resp, dict):
            return WelcomeScreen(resp)
        return wrap_to_async(WelcomeScreen, None, resp, as_create=False)

    def modify_user_voice_state(self,
                                guild: Guild.TYPING,
                                channel: Channel.TYPING,
                                user: User.TYPING = "@me",
                                *,
                                suppress: Optional[bool] = None,
                                request_to_speak_timestamp: Optional[Union[datetime.datetime, str]] = None):
        """
        Modifies user's voice state.

        :param guild: Guild to modify user voice state.
        :param channel: Stage channel user is in.
        :param user: User to modify voice state. Ignore this parameter or pass ``"@me"`` to modify current user.
        :param suppress: Whether to toggle suppress status.
        :param request_to_speak_timestamp: Requests to speak. Time can be present or future.
        """
        user = int(user) if user != "@me" else user
        if request_to_speak_timestamp is not None:
            request_to_speak_timestamp = request_to_speak_timestamp if isinstance(request_to_speak_timestamp, str) else \
                request_to_speak_timestamp.isoformat()
        return self.http.modify_user_voice_state(int(guild), str(int(channel)), user, suppress, request_to_speak_timestamp)

    # Guild Scheduled Event

    def list_scheduled_events_for_guild(self, guild: Guild.TYPING, with_user_count: Optional[bool] = None) -> GuildScheduledEvent.RESPONSE_AS_LIST:
        """
        Lists scheduled events for guild.

        :param guild: Guild to list scheduled events.
        :param Optional[bool] with_user_count: Whether to include user count in response.
        :return: List[:class:`~.GuildScheduledEvent`]
        """
        resp = self.http.list_scheduled_events_for_guild(int(guild), with_user_count)
        if isinstance(resp, list):
            return [GuildScheduledEvent(self, x) for x in resp]
        return wrap_to_async(GuildScheduledEvent, self, resp, as_create=False)

    # TODO: fix all isoformat params

    def create_guild_scheduled_event(self,
                                     guild: Guild.TYPING,
                                     *,
                                     channel: Optional[Channel.TYPING] = None,
                                     entity_metadata: Optional[Union[dict, GuildScheduledEventEntityMetadata]] = None,
                                     name: str,
                                     privacy_level: Union[int, GuildScheduledEventPrivacyLevel],
                                     scheduled_start_time: Union[str, datetime.datetime],
                                     scheduled_end_time: Optional[Union[str, datetime.datetime]] = None,
                                     description: Optional[str] = None,
                                     entity_type: Union[int, GuildScheduledEventEntityTypes]) -> GuildScheduledEvent.RESPONSE:
        """
        Creates guild scheduled event.

        :param guild: Guild to create event.
        :param channel: Channel of the event. Can be optional if entity type is ``EXTERNAL``.
        :param entity_metadata: Metadata of the entity.
        :type entity_metadata: Optional[Union[dict, GuildScheduledEventEntityMetadata]]
        :param str name: Name of the event.
        :param privacy_level: Privacy level of the event.
        :type privacy_level: Union[int, GuildScheduledEventPrivacyLevel]
        :param scheduled_start_time: Scheduled start time of the event.
        :type scheduled_start_time: Union[str, datetime.datetime]
        :param scheduled_end_time: Scheduled end time of the event.
        :type scheduled_end_time: Union[str, datetime.datetime]
        :param Optional[str] description: Description of the event.
        :param entity_type: Type of the entity of the event.
        :type entity_type: Union[int, GuildScheduledEventEntityTypes]
        :return: :class:`~.GuildScheduledEvent`
        """
        kwargs = {
            "name": name,
            "privacy_level": int(privacy_level),
            "scheduled_start_time": scheduled_start_time.isoformat() if isinstance(scheduled_start_time, datetime.datetime) else scheduled_start_time,
            "entity_type": int(entity_type)
        }
        if channel is not None:
            kwargs["channel_id"] = str(int(channel))
        if entity_metadata is not None:
            kwargs["entity_metadata"] = entity_metadata if isinstance(entity_metadata, dict) else entity_metadata.to_dict()
        if scheduled_end_time is not None:
            kwargs["scheduled_end_time"] = scheduled_end_time.isoformat() if isinstance(scheduled_end_time, datetime.datetime) else scheduled_end_time
        if description is not None:
            kwargs["description"] = description
        resp = self.http.create_guild_scheduled_event(int(guild), **kwargs)
        if isinstance(resp, dict):
            return GuildScheduledEvent(self, resp)
        return wrap_to_async(GuildScheduledEvent, self, resp, as_create=False)

    def request_guild_scheduled_event(self, guild: Guild.TYPING, guild_scheduled_event: GuildScheduledEvent.TYPING, with_user_count: Optional[bool] = None) -> GuildScheduledEvent.RESPONSE:
        """
        Requests guild scheduled event.

        :param guild: Guild to request event.
        :param guild_scheduled_event: Event to request.
        :param Optional[bool] with_user_count: Whether to include user count.
        :return: :class:`~.GuildScheduledEvent`
        """
        resp = self.http.request_guild_scheduled_event(int(guild), int(guild_scheduled_event), with_user_count)
        if isinstance(resp, dict):
            return GuildScheduledEvent(self, resp)
        return wrap_to_async(GuildScheduledEvent, self, resp, as_create=False)

    def modify_guild_scheduled_event(self,
                                     guild: Guild.TYPING,
                                     guild_scheduled_event: GuildScheduledEvent.TYPING,
                                     *,
                                     channel: Optional[Channel.TYPING] = EmptyObject,
                                     entity_metadata: Optional[Union[dict, GuildScheduledEventEntityMetadata]] = None,
                                     name: Optional[str] = None,
                                     privacy_level: Optional[Union[int, GuildScheduledEventPrivacyLevel]] = None,
                                     scheduled_start_time: Optional[Union[str, datetime.datetime]] = None,
                                     scheduled_end_time: Optional[Union[str, datetime.datetime]] = None,
                                     description: Optional[str] = None,
                                     entity_type: Optional[Union[int, GuildScheduledEventEntityTypes]] = None,
                                     status: Optional[Union[int, GuildScheduledEventStatus]] = None) -> GuildScheduledEvent.RESPONSE:
        """
        Modifies guild scheduled event.

        :param guild: Guild to modify event.
        :param guild_scheduled_event: Event to modify.
        :param channel: Channel of the event. Set to ``None`` if you are changing event to ``EXTERNAL``.
        :param entity_metadata: Metadata of the entity.
        :type entity_metadata: Optional[Union[dict, GuildScheduledEventEntityMetadata]]
        :param Optional[str] name: Name of the event.
        :param privacy_level: Privacy level of the event.
        :type privacy_level: Optional[Union[int, GuildScheduledEventPrivacyLevel]]
        :param scheduled_start_time: Scheduled start time of the event.
        :type scheduled_start_time: Optional[Union[str, datetime.datetime]]
        :param scheduled_end_time: Scheduled end time of the event.
        :type scheduled_end_time: Optional[Union[str, datetime.datetime]]
        :param Optional[str] description: Description of the event.
        :param entity_type: Type of the entity of the event.
        :type entity_type: Optional[Union[int, GuildScheduledEventEntityTypes]]
        :param status: Status of the event.
        :type status: Optional[Union[int, GuildScheduledEventStatus]]
        :return: :class:`~.GuildScheduledEvent`
        """
        kwargs = {}
        if channel is not EmptyObject:
            kwargs["channel_id"] = channel if channel is None else str(int(channel))
        if entity_metadata is not None:
            kwargs["entity_metadata"] = entity_metadata if isinstance(entity_metadata, dict) else entity_metadata.to_dict()
        if name is not None:
            kwargs["name"] = name
        if privacy_level is not None:
            kwargs["privacy_level"] = int(privacy_level)
        if scheduled_start_time is not None:
            kwargs["scheduled_start_time"] = scheduled_start_time.isoformat() if isinstance(scheduled_start_time, datetime.datetime) else scheduled_start_time
        if scheduled_end_time is not None:
            kwargs["scheduled_end_time"] = scheduled_end_time.isoformat() if isinstance(scheduled_end_time, datetime.datetime) else scheduled_end_time
        if description is not None:
            kwargs["description"] = description
        if entity_type is not None:
            kwargs["entity_type"] = int(entity_type)
        if status is not None:
            kwargs["status"] = int(status)
        resp = self.http.modify_guild_scheduled_event(int(guild), int(guild_scheduled_event), **kwargs)
        if isinstance(resp, dict):
            return GuildScheduledEvent(self, resp)
        return wrap_to_async(GuildScheduledEvent, self, resp, as_create=False)

    def delete_guild_scheduled_event(self, guild: Guild.TYPING, guild_scheduled_event: GuildScheduledEvent.TYPING):
        """
        Deletes guild scheduled event.

        :param guild: Guild to delete event.
        :param guild_scheduled_event: Event to delete.
        """
        return self.http.delete_guild_scheduled_event(int(guild), int(guild_scheduled_event))

    def request_guild_scheduled_event_users(self,
                                            guild: Guild.TYPING,
                                            guild_scheduled_event: GuildScheduledEvent.TYPING,
                                            limit: Optional[int] = None,
                                            with_member: Optional[bool] = None,
                                            before: Optional[User.TYPING] = None,
                                            after: Optional[User.TYPING] = None) -> GuildScheduledEventUser.RESPONSE_AS_LIST:
        """
        Requests guild scheduled event users.

        :param guild: Guild to request guild scheduled event users.
        :param guild_scheduled_event: Event to get users.
        :param Optional[int] limit: Maximum number of users to return.
        :param Optional[bool] with_member: Whether to include member data.
        :param before: User to get users before.
        :param after: User to get users after.
        :return: List[:class:`~.GuildScheduledEventUser`]
        """
        resp = self.http.request_guild_scheduled_event_users(int(guild), int(guild_scheduled_event), limit, with_member, str(int(before)), str(int(after)))
        if isinstance(resp, list):
            return [GuildScheduledEventUser(self, x) for x in resp]
        return wrap_to_async(GuildScheduledEventUser, self, resp, as_create=False)

    # Guild Template

    def request_guild_template(self, template: GuildTemplate.TYPING) -> GuildTemplate.RESPONSE:
        """
        Requests guild template.

        :param template: Template to request. Must be code or guild template object.
        :type template: Union[str, GuildTemplate]
        :return: :class:`~.GuildTemplate`
        """
        resp = self.http.request_guild_template(str(template))
        if isinstance(resp, dict):
            return GuildTemplate(self, resp)
        return wrap_to_async(GuildTemplate, self, resp, as_create=False)

    def create_guild_from_template(self, template: GuildTemplate.TYPING, name: str, *, icon: Optional[str] = None) -> Guild.RESPONSE:
        """
        Creates guild from template.

        :param template: Template to use. Must be code or guild template object.
        :type template: Union[str, GuildTemplate]
        :param str name: Name of the guild.
        :param Optional[str] icon: Icon of the guild. Use :func:`.utils.to_image_data`.
        :return: :class:`~.Guild`
        """
        resp = self.http.create_guild_from_template(str(template), name, icon)
        if isinstance(resp, dict):
            return Guild.create(self, resp)
        return wrap_to_async(Guild, self, resp)

    def request_guild_templates(self, guild: Guild.TYPING) -> GuildTemplate.RESPONSE_AS_LIST:
        """
        Requests guild's all templates.

        :param guild: Guild to request templates.
        :return: List[:class:`~.GuildTemplate`]
        """
        resp = self.http.request_guild_templates(int(guild))
        if isinstance(resp, list):
            return [GuildTemplate(self, x) for x in resp]
        return wrap_to_async(GuildTemplate, self, resp, as_create=False)

    def create_guild_template(self, guild: Guild.TYPING, name: str, *, description: Optional[str] = EmptyObject) -> GuildTemplate.RESPONSE:
        """
        Creates template from guild.

        :param guild: Guild to create template.
        :param str name: Name of the template.
        :param Optional[str] description: Description of the template.
        :return: :class:`~.GuildTemplate`
        """
        resp = self.http.create_guild_template(int(guild), name, description)
        if isinstance(resp, dict):
            return GuildTemplate(self, resp)
        return wrap_to_async(GuildTemplate, self, resp, as_create=False)

    def sync_guild_template(self, guild: Guild.TYPING, template: GuildTemplate.TYPING) -> GuildTemplate.RESPONSE:
        """
        Syncs guild template.

        :param guild: Guild to sync template.
        :param template: Template to sync. Must be code or guild template object.
        :type template: Union[str, GuildTemplate]
        :return: :class:`~.GuildTemplate`
        """
        resp = self.http.sync_guild_template(int(guild), str(template))
        if isinstance(resp, dict):
            return GuildTemplate(self, resp)
        return wrap_to_async(GuildTemplate, self, resp, as_create=False)

    def modify_guild_template(self, guild: Guild.TYPING, template: GuildTemplate.TYPING, name: Optional[str] = None, description: Optional[str] = EmptyObject) -> GuildTemplate.RESPONSE:
        """
        Modifies guild template.

        :param guild: Guild to modify template.
        :param template: Template to modify. Must be code or guild template object.
        :type template: Union[str, GuildTemplate]
        :param Optional[str] name: Name of the template to modify.
        :param Optional[str] description: Description of the template to modify.
        :return: :class:`~.GuildTemplate`
        """
        resp = self.http.modify_guild_template(int(guild), str(template), name, description)
        if isinstance(resp, dict):
            return GuildTemplate(self, resp)
        return wrap_to_async(GuildTemplate, self, resp, as_create=False)

    def delete_guild_template(self, guild: Guild.TYPING, template: GuildTemplate.TYPING) -> GuildTemplate.RESPONSE:
        """
        Deletes guild template.

        :param guild: Guild to delete template.
        :param template: Template to delete. Must be code or guild template object.
        :type template: Union[str, GuildTemplate]
        :return: :class:`~.GuildTemplate`
        """
        resp = self.http.delete_guild_template(int(guild), str(template))
        if isinstance(resp, dict):
            return GuildTemplate(self, resp)
        return wrap_to_async(GuildTemplate, self, resp, as_create=False)

    # Invite

    def request_invite(self, invite_code: Union[str, Invite], *, with_counts: Optional[bool] = None, with_expiration: Optional[bool] = None) -> Invite.RESPONSE:
        """
        Requests invite.

        :param invite_code: Code of the invite or invite object.
        :type invite_code: Union[str, Invite]
        :param Optional[bool] with_counts: Whether to include approximate member counts.
        :param Optional[bool] with_expiration: Whether to include the expiration date.
        :return: :class:`~.Invite`
        """
        resp = self.http.request_invite(str(invite_code), with_counts, with_expiration)
        if isinstance(resp, dict):
            return Invite(self, resp)
        return wrap_to_async(Invite, self, resp, as_create=False)

    def delete_invite(self, invite_code: Union[str, Invite], *, reason: Optional[str] = None) -> Invite.RESPONSE:
        """
        Deletes invite.

        :param invite_code: Code of the invite or invite object.
        :type invite_code: Union[str, Invite]
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Invite`
        """
        resp = self.http.delete_invite(str(invite_code), reason=reason)
        if isinstance(resp, dict):
            return Invite(self, resp)
        return wrap_to_async(Invite, self, resp, as_create=False)

    # Stage Instance

    def create_stage_instance(self, channel: Channel.TYPING, topic: str, privacy_level: Optional[Union[int, PrivacyLevel]] = None, *, reason: Optional[str] = None) -> StageInstance.RESPONSE:
        """
        Creates stage instance.

        :param channel: Stage channel to create instance.
        :param str topic: Topic of the instance.
        :param privacy_level: Privacy level to set.
        :type privacy_level: Optional[Union[int, PrivacyLevel]]
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.StageInstance`
        """
        resp = self.http.create_stage_instance(str(int(channel)), topic, int(privacy_level) if privacy_level is not None else privacy_level, reason=reason)
        if isinstance(resp, dict):
            return StageInstance.create(self, resp)
        return wrap_to_async(StageInstance, self, resp)

    def request_stage_instance(self, channel: Channel.TYPING):
        """
        Requests stage instance.

        :param channel: Stage channel to request instance.
        :return: :class:`~.StageInstance`
        """
        resp = self.http.request_stage_instance(int(channel))
        if isinstance(resp, dict):
            return StageInstance.create(self, resp)
        return wrap_to_async(StageInstance, self, resp)

    def modify_stage_instance(self, channel: Channel.TYPING, topic: Optional[str] = None, privacy_level: Optional[Union[int, PrivacyLevel]] = None, *, reason: Optional[str] = None) -> StageInstance.RESPONSE:
        """
        Modifies stage instance.

        :param channel: Stage channel to modify instance.
        :param Optional[str] topic: Topic of the instance to change.
        :param privacy_level: Privacy level to change.
        :type privacy_level: Optional[Union[int, PrivacyLevel]]
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.StageInstance`
        """
        resp = self.http.modify_stage_instance(int(channel), topic, int(privacy_level) if privacy_level is not None else privacy_level, reason=reason)
        if isinstance(resp, dict):
            return StageInstance.create(self, resp)
        return wrap_to_async(StageInstance, self, resp)

    def delete_stage_instance(self, channel: Channel.TYPING, *, reason: Optional[str] = None):
        """
        Deletes stage instance.

        :param channel: Stage channel to delete instance.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.delete_stage_instance(int(channel), reason=reason)

    # Sticker

    def request_sticker(self, sticker: Sticker.TYPING) -> Sticker.RESPONSE:
        """
        Requests sticker.

        :param sticker: Sticker to request.
        :return: :class:`~.Sticker`
        """
        resp = self.http.request_sticker(int(sticker))
        if isinstance(resp, dict):
            return Sticker.create(self, resp)
        return wrap_to_async(Sticker, self, resp)

    def list_nitro_sticker_packs(self) -> "AbstractObject.RESPONSE":
        """
        Lists nitro sticker packs.

        :return: :class:`~.AbstractObject`
        """
        from .base.model import AbstractObject
        resp = self.http.list_nitro_sticker_packs()
        if isinstance(resp, dict):
            return AbstractObject(resp)
        return wrap_to_async(AbstractObject, None, resp, as_create=False)

    def list_guild_stickers(self, guild: Guild.TYPING) -> Sticker.RESPONSE_AS_LIST:
        """
        Lists guild stickers.

        :param guild: Guild to list stickers.
        :return: List[:class:`~.Sticker`]
        """
        resp = self.http.list_guild_stickers(int(guild))
        if isinstance(resp, list):
            return [Sticker.create(self, x) for x in resp]
        return wrap_to_async(Sticker, self, resp)

    def request_guild_sticker(self, guild: Guild.TYPING, sticker: Sticker.TYPING) -> Sticker.RESPONSE:
        """
        Requests guild sticker.

        :param guild: Guild to request sticker.
        :param sticker: Sticker to request.
        :return: :class:`~.Sticker`
        """
        resp = self.http.request_guild_sticker(int(guild), int(sticker))
        if isinstance(resp, dict):
            return Sticker.create(self, resp)
        return wrap_to_async(Sticker, self, resp)

    def create_guild_sticker(self, guild: Guild.TYPING, *, name: str, description: str, tags: str, file: FILE_TYPE, reason: Optional[str] = None) -> Sticker.RESPONSE:
        """
        Creates guild sticker.

        :param guild: Guild to create sticker.
        :param str name: Name of the sticker.
        :param str description: Description of the sticker.
        :param str tags: Tags of the sticker.
        :param FILE_TYPE file: Image file of the sticker.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Sticker`
        """
        if isinstance(file, str):
            file = open(file, "rb")
        try:
            resp = self.http.create_guild_sticker(int(guild), name, description, tags, file, reason=reason)
            if isinstance(resp, dict):
                return Sticker.create(self, resp)
            return wrap_to_async(Sticker, self, resp)
        finally:
            file.close()

    def modify_guild_sticker(self,
                             guild: Guild.TYPING,
                             sticker: Sticker.TYPING,
                             *,
                             name: Optional[str] = None,
                             description: Optional[str] = EmptyObject,
                             tags: Optional[str] = None,
                             reason: Optional[str] = None) -> Sticker.RESPONSE:
        """
        Modifies guild sticker.

        :param guild: Guild to modify sticker.
        :param sticker: Sticker to modify.
        :param Optional[str] name: Name of the sticker to modify.
        :param Optional[str] description: Description of the sticker to modify.
        :param Optional[str] tags: Tags of the sticker to modify.
        :param Optional[str] reason: Reason of the action.
        :return: :class:`~.Sticker`
        """
        resp = self.http.modify_guild_sticker(int(guild), int(sticker), name, description, tags, reason=reason)
        if isinstance(resp, dict):
            return Sticker.create(self, resp)
        return wrap_to_async(Sticker, self, resp)

    def delete_guild_sticker(self, guild: Guild.TYPING, sticker: Sticker.TYPING, *, reason: Optional[str] = None):
        """
        Deletes guild sticker.

        :param guild: Guild to delete sticker.
        :param sticker: Sticker to delete.
        :param Optional[str] reason: Reason of the action.
        """
        return self.http.delete_guild_sticker(int(guild), int(sticker), reason=reason)

    # User

    def request_user(self, user: User.TYPING = "@me") -> User.RESPONSE:
        """
        Requests user.

        :param user: User to request. Defaults to current user.
        :return: :class:`~.User`
        """
        resp = self.http.request_user(int(user) if user != "@me" else user)
        if isinstance(resp, dict):
            return User.create(self, resp)
        return wrap_to_async(User, self, resp)

    def modify_current_user(self, username: Optional[str] = None, avatar: Optional[FILE_TYPE] = EmptyObject) -> User.RESPONSE:
        """
        Modifies current user.

        :param Optional[str] username: Username of the user to modify.
        :param Optional[FILE_TYPE] avatar: Avatar of the user to modify.
        :return: :class:`~.User`
        """
        avatar = to_image_data(avatar) if avatar is not None or avatar is not EmptyObject else avatar
        resp = self.http.modify_current_user(username, avatar)
        if isinstance(resp, dict):
            return User.create(self, resp)
        return wrap_to_async(User, self, resp)

    def request_current_user_guilds(self) -> Guild.RESPONSE_AS_LIST:
        """
        Requests current user guilds.

        :return: List[:class:`~.Guild`]
        """
        resp = self.http.request_current_user_guilds()
        if isinstance(resp, list):
            return [Guild.create(self, x) for x in resp]
        return wrap_to_async(Guild, self, resp)

    def leave_guild(self, guild: Guild.TYPING):
        """
        Leaves guild.

        :param guild: Guild to leave.
        """
        return self.leave_guild(int(guild))

    def create_dm(self, recipient: User.TYPING) -> Channel.RESPONSE:
        """
        Creates direct message channel.

        :param recipient: Recipient of the direct message.
        :return: :class:`~.Channel`
        """
        resp = self.http.create_dm(str(int(recipient)))
        if isinstance(resp, dict):
            return Channel.create(self, resp)
        return wrap_to_async(Channel, self, resp)

    def create_group_dm(self, access_tokens: List[str], nicks: Dict[User.TYPING, str]) -> Channel.RESPONSE:
        """
        Creates group direct message channel.

        :param List[str] access_tokens: Access tokens of the group members.
        :param nicks: Nicknames of the group members.
        :return: :class:`~.Channel`
        """
        nicks = {str(int(k)): v for k, v in nicks.items()}
        resp = self.http.create_group_dm(access_tokens, nicks)
        if isinstance(resp, dict):
            return Channel.create(self, resp)
        return wrap_to_async(Channel, self, resp)

    # Voice

    def list_voice_regions(self) -> VoiceRegion.RESPONSE_AS_LIST:
        """
        Lists voice regions.

        :return: List[:class:`~.VoiceRegion`]
        """
        resp = self.http.list_voice_regions()
        if isinstance(resp, list):
            return [VoiceRegion(x) for x in resp]
        return wrap_to_async(VoiceRegion, None, resp, as_create=False)

    # Webhook

    def create_webhook(self, channel: Channel.TYPING, *, name: Optional[str] = None, avatar: Optional[str] = None) -> Webhook.RESPONSE:
        """
        Creates webhook.

        :param channel: Channel to create webhook in.
        :param Optional[str] name: Name of the webhook.
        :param Optional[str] avatar: Avatar of the webhook.
        :return: :class:`~.Webhook`
        """
        hook = self.http.create_webhook(int(channel), name, avatar)
        if isinstance(hook, dict):
            return Webhook(self, hook)
        return wrap_to_async(Webhook, self, hook, as_create=False)

    def request_channel_webhooks(self, channel: Channel.TYPING) -> Webhook.RESPONSE_AS_LIST:
        """
        Requests channel webhooks.

        :param channel: Channel to request webhooks from.
        :return: List[:class:`~.Webhook`]
        """
        hooks = self.http.request_channel_webhooks(int(channel))
        if isinstance(hooks, list):
            return [Webhook(self, x) for x in hooks]
        return wrap_to_async(Webhook, self, hooks, as_create=False)

    def request_guild_webhooks(self, guild: Guild.TYPING) -> Webhook.RESPONSE_AS_LIST:
        """
        Requests guild webhooks.

        :param guild: Guild to request webhooks from.
        :return: List[:class:`~.Webhook`]
        """
        hooks = self.http.request_guild_webhooks(int(guild))
        if isinstance(hooks, list):
            return [Webhook(self, x) for x in hooks]
        return wrap_to_async(Webhook, self, hooks, as_create=False)

    def request_webhook(self, webhook: Webhook.TYPING, webhook_token: Optional[str] = None) -> Webhook.RESPONSE:
        """
        Requests webhook.

        :param webhook: Webhook to request.
        :param Optional[str] webhook_token: Token of the webhook, if ``webhook`` parameter is not a :class:`~.Webhook` instance.
        :return: :class:`~.Webhook`
        """
        if isinstance(webhook, Webhook):
            webhook_token = webhook_token or webhook.token
        hook = self.http.request_webhook(int(webhook)) if not webhook_token else self.http.request_webhook_with_token(int(webhook), webhook_token)
        if isinstance(hook, dict):
            return Webhook(self, hook)
        return wrap_to_async(Webhook, self, hook, as_create=False)

    def modify_webhook(self,
                       webhook: Webhook.TYPING,
                       *,
                       webhook_token: Optional[str] = None,
                       name: Optional[str] = None,
                       avatar: Optional[str] = None,
                       channel: Optional[Channel.TYPING] = None) -> Webhook.RESPONSE:
        """
        Modifies webhook.

        :param webhook: Webhook to modify.
        :param Optional[str] webhook_token: Token of the webhook, if ``webhook`` parameter is not a :class:`~.Webhook` instance.
        :param Optional[str] name: Name of the webhook to modify.
        :param Optional[str] avatar: Avatar of the webhook to modify.
        :param channel: Channel to move the webhook to.
        :return: :class:`~.Webhook`
        """
        hook = self.http.modify_webhook(int(webhook), name, avatar, str(int(channel)) if channel is not None else channel) if not webhook_token \
            else self.http.modify_webhook_with_token(int(webhook), webhook_token, name, avatar)
        if isinstance(hook, dict):
            return Webhook(self, hook)
        return wrap_to_async(Webhook, self, hook, as_create=False)

    def delete_webhook(self, webhook: Webhook.TYPING, webhook_token: Optional[str] = None):
        """
        Deletes webhook.

        :param webhook: Webhook to delete.
        :param webhook_token: Token of the webhook, if ``webhook`` parameter is not a :class:`~.Webhook` instance.
        :return: :class:`~.Webhook`
        """
        return self.http.delete_webhook(int(webhook)) if not webhook_token else self.http.delete_webhook_with_token(int(webhook), webhook_token)

    def execute_webhook(self,
                        webhook: Webhook.TYPING,
                        *,
                        webhook_token: Optional[str] = None,
                        wait: Optional[bool] = None,
                        thread: Channel.TYPING = None,
                        content: Optional[str] = None,
                        username: Optional[str] = None,
                        avatar_url: Optional[str] = None,
                        tts: Optional[bool] = False,
                        file: Optional[FILE_TYPE] = None,
                        files: Optional[List[FILE_TYPE]] = None,
                        embed: Optional[Union[Embed, dict]] = None,
                        embeds: Optional[List[Union[Embed, dict]]] = None,
                        allowed_mentions: Optional[Union[AllowedMentions, dict]] = None,
                        components: Optional[List[Union[dict, Component]]] = None) -> Message.RESPONSE:
        """
        Executes webhook.

        :param webhook: Webhook to execute.
        :param Optional[str] webhook_token: Token of the webhook, if ``webhook`` parameter is not a :class:`~.Webhook` instance.
        :param Optional[bool] wait: Whether to wait for the message to be created.
        :param thread: Thread channel to send the message in.
        :param Optional[str] content: Content of the message.
        :param Optional[str] username: Username of the message.
        :param Optional[str] avatar_url: Avatar of the message.
        :param Optional[bool] tts: Whether the message should be TTS.
        :param Optional[FILE_TYPE] file: File to send with the message.
        :param Optional[List[FILE_TYPE]] files: List of files to send with the message.
        :param embed: Embed to send with the message.
        :type embed: Optional[Union[Embed, dict]]
        :param embeds: List of embeds to send with the message.
        :type embeds: Optional[List[Union[Embed, dict]]]
        :param allowed_mentions: Allowed mentions of the message.
        :type allowed_mentions: Optional[Union[AllowedMentions, dict]]
        :param components: List of components to send with the message.
        :type components: Optional[List[Union[dict, Component]]]
        :return: :class:`~.Message`
        """
        if webhook_token is None and not isinstance(webhook, Webhook):
            raise TypeError("you must pass webhook_token if webhook is not dico.Webhook object.")
        if thread and isinstance(thread, Channel) and not thread.is_thread_channel():
            raise TypeError("thread must be thread channel.")
        if file and files:
            raise TypeError("you can't pass both file and files.")
        if embed and embeds:
            raise TypeError("you can't pass both embed and embeds.")
        if file:
            files = [file]
        if files:
            for x in range(len(files)):
                sel = files[x]
                if isinstance(sel, str):
                    files[x] = open(sel, "rb")
        if embed:
            embeds = [embed]
        if embeds:
            embeds = [x.to_dict() if not isinstance(x, dict) else x for x in embeds]
        if components:
            components = [x.to_dict() if not isinstance(x, dict) else x for x in components]
        params = {"webhook_id": int(webhook),
                  "webhook_token": webhook_token if not isinstance(webhook, Webhook) else webhook.token,
                  "wait": wait,
                  "thread_id": str(int(thread)) if thread else thread,
                  "content": content,
                  "username": username,
                  "avatar_url": avatar_url,
                  "tts": tts,
                  "embeds": embeds,
                  "allowed_mentions": self.get_allowed_mentions(allowed_mentions),
                  "components": components}
        if files:
            params["files"] = files
        try:
            msg = self.http.execute_webhook(**params) if not files else self.http.execute_webhook_with_files(**params)
            if isinstance(msg, dict):
                return Message.create(self, msg, webhook_token=webhook_token or webhook.token)
            return wrap_to_async(Message, self, msg, webhook_token=webhook_token or webhook.token)
        finally:
            if files:
                [x.close() for x in files if not x.closed]

    def request_webhook_message(self,
                                webhook: Webhook.TYPING,
                                message: Message.TYPING,
                                *,
                                webhook_token: Optional[str] = None) -> Message.RESPONSE:
        """
        Requests webhook message.

        :param webhook: Webhook to request message.
        :param message: Message to request.
        :param Optional[str] webhook_token: Token of the webhook, if ``webhook`` parameter is not a :class:`~.Webhook` instance.
        :return: :class:`~.Message`
        """
        if not isinstance(webhook, Webhook) and not webhook_token:
            raise TypeError("you must pass webhook_token if webhook is not dico.Webhook object.")
        msg = self.http.request_webhook_message(int(webhook), webhook_token or webhook.token, int(message))
        if isinstance(msg, dict):
            return Message.create(self, msg, webhook_token=webhook_token or webhook.token)
        return wrap_to_async(Message, self, msg, webhook_token=webhook_token or webhook.token)

    def edit_webhook_message(self,
                             webhook: Webhook.TYPING,
                             message: Message.TYPING,
                             *,
                             webhook_token: Optional[str] = None,
                             content: Optional[str] = EmptyObject,
                             embed: Optional[Union[Embed, dict]] = EmptyObject,
                             embeds: Optional[List[Union[Embed, dict]]] = EmptyObject,
                             file: Optional[FILE_TYPE] = EmptyObject,
                             files: Optional[List[FILE_TYPE]] = EmptyObject,
                             allowed_mentions: Optional[Union[AllowedMentions, dict]] = EmptyObject,
                             attachments: Optional[List[Union[Attachment, dict]]] = EmptyObject,
                             component: Optional[Union[dict, Component]] = EmptyObject,
                             components: Optional[List[Union[dict, Component]]] = EmptyObject) -> Message.RESPONSE:
        """
        Edits webhook message.

        :param webhook: Webhook to edit message.
        :param message: Message to edit.
        :param Optional[str] webhook_token: Token of the webhook, if ``webhook`` parameter is not a :class:`~.Webhook` instance.
        :param Optional[str] content: Content of the message to edit.
        :param embed: Embed to edit.
        :type embed: Optional[Union[Embed, dict]]
        :param embeds: List of embeds to edit.
        :type embeds: Optional[List[Union[Embed, dict]]]
        :param file: File to edit.
        :type file: Optional[FILE_TYPE]
        :param files: List of files to edit.
        :type files: Optional[List[FILE_TYPE]]
        :param allowed_mentions: Allowed mentions to edit.
        :type allowed_mentions: Optional[Union[AllowedMentions, dict]]
        :param attachments: List of attachments to edit.
        :type attachments: Optional[List[Union[Attachment, dict]]]
        :param component: Component to edit.
        :type component: Optional[Union[dict, Component]]
        :param components: List of components to edit.
        :type components: Optional[List[Union[dict, Component]]]
        :return: :class:`~.Message`
        """
        if not isinstance(webhook, Webhook) and not webhook_token:
            raise TypeError("you must pass webhook_token if webhook is not dico.Webhook object.")
        if file and files:
            raise TypeError("you can't pass both file and files.")
        if embed and embeds:
            raise TypeError("you can't pass both embed and embeds.")
        if component and components:
            raise TypeError("you can't pass both component and components.")
        if file is None or files is None:
            files = None
        else:
            if file:
                files = [file]
            if files:
                for x in range(len(files)):
                    sel = files[x]
                    if isinstance(sel, str):
                        files[x] = open(sel, "rb")
        if embed is None or embeds is None:
            embeds = None
        else:
            if embed:
                embeds = [embed]
            if embeds:
                embeds = [x if isinstance(x, dict) else x.to_dict() for x in embeds]
        if component is None or components is None:
            components = None
        else:
            if component:
                components = [component]
            if components:
                components = [*map(lambda n: n if isinstance(n, dict) else n.to_dict(), components)]
        _att = []
        if attachments:
            for x in attachments:
                if not isinstance(x, dict):
                    x = x.to_dict()
                _att.append(x)
        params = {"webhook_id": int(webhook),
                  "webhook_token": webhook_token or webhook.token,
                  "message_id": int(message),
                  "content": content,
                  "embeds": embeds,
                  "files": files,
                  "allowed_mentions": self.get_allowed_mentions(allowed_mentions),
                  "attachments": _att,
                  "components": components}
        try:
            msg = self.http.edit_webhook_message(**params)
            if isinstance(msg, dict):
                return Message.create(self, msg, webhook_token=webhook_token or webhook.token)
            return wrap_to_async(Message, self, msg, webhook_token=webhook_token or webhook.token)
        finally:
            if files:
                [x.close() for x in files if not x.closed]

    def delete_webhook_message(self,
                               webhook: Webhook.TYPING,
                               message: Message.TYPING,
                               *,
                               webhook_token: Optional[str] = None):
        """
        Delete a message from a webhook.

        :param webhook: Webhook to delete message from.
        :param message: Message to delete.
        :param Optional[str] webhook_token: Token of the webhook, if ``webhook`` parameter is not a :class:`~.Webhook` instance.
        :return:
        """
        if not isinstance(webhook, Webhook) and not webhook_token:
            raise TypeError("you must pass webhook_token if webhook is not dico.Webhook object.")
        return self.http.delete_webhook_message(int(webhook), webhook_token or webhook.token, int(message))

    # Interaction

    def request_application_commands(self,
                                     guild: Optional[Guild.TYPING] = None,
                                     *,
                                     application_id: Optional[Snowflake.TYPING] = None) -> ApplicationCommand.RESPONSE_AS_LIST:
        """
        Request application commands.

        :param guild: Guild to request commands from. Default global commands.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :return: List[:class:`~.ApplicationCommand`]
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        app_commands = self.http.request_application_commands(int(application_id or self.application_id), int(guild) if guild else guild)
        if isinstance(app_commands, list):
            return [ApplicationCommand.create(x) for x in app_commands]
        return wrap_to_async(ApplicationCommand, None, app_commands)

    def create_application_command(self,
                                   guild: Optional[Guild.TYPING] = None,
                                   *,
                                   name: str,
                                   description: Optional[str] = None,
                                   options: Optional[List[Union[ApplicationCommandOption, dict]]] = None,
                                   default_permission: Optional[bool] = None,
                                   command_type: Optional[Union[ApplicationCommandTypes, int]] = None,
                                   application_id: Optional[Snowflake.TYPING] = None) -> ApplicationCommand.RESPONSE:
        """
        Creates application command.

        :param guild: Guild to create command in. Default global command.
        :param str name: Name of the command.
        :param Optional[str] description: Description of the command.
        :param options: List of command options.
        :type options: Optional[List[Union[:class:`~.ApplicationCommandOption`, dict]]]
        :param Optional[bool] default_permission: Whether default permission is enabled or not.
        :param command_type: Type of the command.
        :type command_type: Optional[Union[:class:`~.ApplicationCommandTypes`, int]]
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :return: :class:`~.ApplicationCommand`
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        if description is None and (command_type is None or int(command_type) == 1):
            raise ValueError("CHAT_INPUT requires description.")
        options = [x if isinstance(x, dict) else x.to_dict() for x in options or []]
        command_type = int(command_type) if command_type is not None else command_type
        resp = self.http.create_application_command(int(application_id or self.application_id), name, description, options, default_permission, command_type, int(guild) if guild else guild)
        if isinstance(resp, dict):
            return ApplicationCommand.create(resp)
        return wrap_to_async(ApplicationCommand, None, resp)

    def request_application_command(self,
                                    command: ApplicationCommand.TYPING,
                                    *,
                                    guild: Optional[Guild.TYPING] = None,
                                    application_id: Optional[Snowflake.TYPING] = None) -> ApplicationCommand.RESPONSE:
        """
        Requests application command.

        :param command: Command to request.
        :param guild: Guild to request command from, if command is guild's.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :return: :class:`~.ApplicationCommand`
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        command_id = command.id if isinstance(command, ApplicationCommand) else int(command)
        resp = self.http.request_application_command(int(application_id or self.application_id), command_id, int(guild))
        if isinstance(resp, dict):
            return ApplicationCommand.create(resp)
        return wrap_to_async(ApplicationCommand, None, resp)

    def edit_application_command(self,
                                 command: ApplicationCommand.TYPING,
                                 *,
                                 name: Optional[str] = None,
                                 description: Optional[str] = None,
                                 options: Optional[List[Union[ApplicationCommandOption, dict]]] = None,
                                 default_permission: Optional[bool] = None,
                                 guild: Optional[Guild.TYPING] = None,
                                 application_id: Optional[Snowflake.TYPING] = None) -> ApplicationCommand.RESPONSE:
        """
        Edits application command.

        :param command: Command to edit.
        :param Optional[str] name: Name of the command to edit.
        :param Optional[str] description: Description of the command to edit.
        :param options: List of command options to edit.
        :type options: Optional[List[Union[:class:`~.ApplicationCommandOption`, dict]]]
        :param Optional[bool] default_permission: Whether default permission is enabled or not.
        :param guild: Guild to edit command in, if command is guild's.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :return: :class:`~.ApplicationCommand`
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        command_id = int(command)
        options = [x if isinstance(x, dict) else x.to_dict() for x in options or []]
        resp = self.http.edit_application_command(int(application_id or self.application_id), command_id, name, description, options, default_permission, int(guild) if guild else guild)
        if isinstance(resp, dict):
            return ApplicationCommand.create(resp)
        return wrap_to_async(ApplicationCommand, None, resp)

    def delete_application_command(self,
                                   command: ApplicationCommand.TYPING,
                                   *,
                                   guild: Optional[Guild.TYPING] = None,
                                   application_id: Optional[Snowflake.TYPING] = None):
        """
        Deletes application command.

        :param command: Command to delete.
        :param guild: Guild to delete command from, if command is guild's.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        command_id = int(command)
        return self.http.delete_application_command(int(application_id or self.application_id), command_id, int(guild) if guild else guild)

    def bulk_overwrite_application_commands(self,
                                            *commands: Union[dict, ApplicationCommand],
                                            guild: Optional[Guild.TYPING] = None,
                                            application_id: Optional[Snowflake.TYPING] = None) -> ApplicationCommand.RESPONSE_AS_LIST:
        """
        Bulk overwrites application commands.

        :param commands: Commands to overwrite.
        :type commands: Union[dict, :class:`~.ApplicationCommand`]
        :param guild: Guild to overwrite commands in, if commands are guild's.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :return: List[:class:`~.ApplicationCommand`]
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        commands = [x if isinstance(x, dict) else x.to_dict() for x in commands]
        app_commands = self.http.bulk_overwrite_application_commands(int(application_id or self.application_id), commands, int(guild) if guild else guild)
        if isinstance(app_commands, list):
            return [ApplicationCommand.create(x) for x in app_commands]
        return wrap_to_async(ApplicationCommand, None, app_commands)

    def create_interaction_response(self,
                                    interaction: Interaction.TYPING,
                                    interaction_response: Union[dict, InteractionResponse],
                                    *,
                                    interaction_token: Optional[str] = None):
        """
        Creates interaction response.

        :param interaction: Interaction to create response for.
        :param interaction_response: Response of interaction to create.
        :type interaction_response: Union[dict, :class:`~.InteractionResponse`]
        :param Optional[str] interaction_token: Token of the interaction, if parameter ``interaction`` is not an Interaction instance.
        """
        if not isinstance(interaction, Interaction) and not interaction_token:
            raise TypeError("you must pass interaction_token if interaction is not dico.Interaction object.")
        interaction_response = interaction_response if isinstance(interaction_response, dict) else interaction_response.to_dict()
        return self.http.create_interaction_response(int(interaction), interaction_token or interaction.token, interaction_response)

    def request_interaction_response(self,
                                     interaction: Optional[Interaction.TYPING] = None,
                                     message: Message.TYPING = "@original",
                                     *,
                                     interaction_token: Optional[str] = None,
                                     application_id: Optional[Snowflake.TYPING] = None) -> Message.RESPONSE:
        """
        Requests interaction response.

        :param interaction: Interaction to request response for.
        :param message: Message to request. Defaults to initial response.
        :param Optional[str] interaction_token: Token of the interaction, if parameter ``interaction`` is not an Interaction instance.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :return: :class:`~.Message`
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        if not isinstance(interaction, Interaction) and not interaction_token:
            raise TypeError("you must pass interaction_token if interaction is not dico.Interaction object.")
        msg = self.http.request_interaction_response(application_id or self.application_id, interaction_token or interaction.token, int(message) if message != "@original" else message)
        original_response = message == "@original"
        if isinstance(msg, dict):
            return Message.create(self, msg, interaction_token=interaction_token or interaction.token, original_response=original_response)
        return wrap_to_async(Message, self, msg, interaction_token=interaction_token or interaction.token, original_response=original_response)

    def create_followup_message(self,
                                interaction: Optional[Interaction.TYPING] = None,
                                *,
                                interaction_token: Optional[str] = None,
                                application_id: Optional[Snowflake.TYPING] = None,
                                content: Optional[str] = None,
                                username: Optional[str] = None,
                                avatar_url: Optional[str] = None,
                                tts: Optional[bool] = False,
                                file: Optional[FILE_TYPE] = None,
                                files: Optional[List[FILE_TYPE]] = None,
                                embed: Optional[Union[Embed, dict]] = None,
                                embeds: Optional[List[Union[Embed, dict]]] = None,
                                allowed_mentions: Optional[Union[AllowedMentions, dict]] = None,
                                components: Optional[List[Union[dict, Component]]] = None,
                                ephemeral: Optional[bool] = False) -> Message.RESPONSE:
        """
        Creates followup message.

        :param interaction: Interaction to create followup message for.
        :param Optional[str] interaction_token: Token of the interaction, if parameter ``interaction`` is not an Interaction instance.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :param Optional[str] content: Content of the message.
        :param Optional[str] username: Username of the message.
        :param Optional[str] avatar_url: Avatar URL of the message.
        :param Optional[bool] tts: Whether the message should be TTS.
        :param Optional[FILE_TYPE] file: File to send.
        :param Optional[List[FILE_TYPE]] files: List of files to send.
        :param embed: Embed to send.
        :type embed: Optional[Union[Embed, dict]]
        :param embeds: List of embeds to send.
        :type embeds: Optional[List[Union[Embed, dict]]]
        :param allowed_mentions: Allowed mentions of the message.
        :type allowed_mentions: Optional[Union[AllowedMentions, dict]]
        :param components: List of components to send.
        :type components: Optional[List[Union[dict, Component]]]
        :param Optional[bool] ephemeral: Whether the message should be ephemeral.
        :return: :class:`~.Message`
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        if not isinstance(interaction, Interaction) and not interaction_token:
            raise TypeError("you must pass interaction_token if interaction is not dico.Interaction object.")
        if file and files:
            raise TypeError("you can't pass both file and files.")
        if embed and embeds:
            raise TypeError("you can't pass both embed and embeds.")
        if file:
            files = [file]
        if files:
            for x in range(len(files)):
                sel = files[x]
                if isinstance(sel, str):
                    files[x] = open(sel, "rb")
        if embed:
            embeds = [embed]
        if embeds:
            embeds = [x.to_dict() if not isinstance(x, dict) else x for x in embeds]
        if components:
            components = [x.to_dict() if not isinstance(x, dict) else x for x in components]
        params = {"application_id": application_id or self.application_id,
                  "interaction_token": interaction_token or interaction.token,
                  "content": content,
                  "username": username,
                  "avatar_url": avatar_url,
                  "tts": tts,
                  "embeds": embeds,
                  "allowed_mentions": self.get_allowed_mentions(allowed_mentions),
                  "components": components}
        if files:
            params["files"] = files
        if ephemeral:
            params["flags"] = 64
        try:
            msg = self.http.create_followup_message(**params)
            if isinstance(msg, dict):
                return Message.create(self, msg, interaction_token=interaction_token or interaction.token)
            return wrap_to_async(Message, self, msg, interaction_token=interaction_token or interaction.token)
        finally:
            if files:
                [x.close() for x in files if not x.closed]

    def edit_interaction_response(self,
                                  interaction: Optional[Interaction.TYPING] = None,
                                  message: Message.TYPING = "@original",
                                  *,
                                  interaction_token: Optional[str] = None,
                                  application_id: Optional[Snowflake.TYPING] = None,
                                  content: Optional[str] = EmptyObject,
                                  file: Optional[FILE_TYPE] = EmptyObject,
                                  files: Optional[List[FILE_TYPE]] = EmptyObject,
                                  embed: Optional[Union[Embed, dict]] = EmptyObject,
                                  embeds: Optional[List[Union[Embed, dict]]] = EmptyObject,
                                  allowed_mentions: Optional[Union[AllowedMentions, dict]] = EmptyObject,
                                  attachments: Optional[List[Union[Attachment, dict]]] = EmptyObject,
                                  component: Optional[Union[dict, Component]] = EmptyObject,
                                  components: Optional[List[Union[dict, Component]]] = EmptyObject) -> Message.RESPONSE:
        """
        Edits interaction response.

        :param interaction: Interaction to edit response.
        :param message: Message to edit.
        :param Optional[str] interaction_token: Token of the interaction, if parameter ``interaction`` is not an Interaction instance.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :param Optional[str] content: Content of the message to edit.
        :param Optional[FILE_TYPE] file: File to edit.
        :param Optional[List[FILE_TYPE]] files: List of files to edit.
        :param embed: Embed to edit.
        :type embed: Optional[Union[Embed, dict]]
        :param embeds: List of embeds to edit.
        :type embeds: Optional[List[Union[Embed, dict]]]
        :param allowed_mentions: Allowed mentions to edit.
        :type allowed_mentions: Optional[Union[AllowedMentions, dict]]
        :param attachments: Attachments to edit.
        :type attachments: Optional[List[Union[Attachment, dict]]]
        :param component: Component to edit.
        :type component: Optional[Union[dict, Component]]
        :param components: List of components to edit.
        :type components: Optional[List[Union[dict, Component]]]
        :return: :class:`~.Message`
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        if not isinstance(interaction, Interaction) and not interaction_token:
            raise TypeError("you must pass interaction_token if interaction is not dico.Interaction object.")
        if file and files:
            raise TypeError("you can't pass both file and files.")
        if embed and embeds:
            raise TypeError("you can't pass both embed and embeds.")
        if component and components:
            raise TypeError("you can't pass both component and components.")
        if file is None or files is None:
            files = None
        else:
            if file:
                files = [file]
            if files:
                for x in range(len(files)):
                    sel = files[x]
                    if isinstance(sel, str):
                        files[x] = open(sel, "rb")
        if embed is None or embeds is None:
            embeds = None
        else:
            if embed:
                embeds = [embed]
            if embeds:
                embeds = [x if isinstance(x, dict) else x.to_dict() for x in embeds]
        if component is None or components is None:
            components = None
        else:
            if component:
                components = [component]
            if components:
                components = [*map(lambda n: n if isinstance(n, dict) else n.to_dict(), components)]
        _att = []
        if attachments:
            for x in attachments:
                if not isinstance(x, dict):
                    x = x.to_dict()
                _att.append(x)
        params = {"application_id": application_id or self.application_id,
                  "interaction_token": interaction_token or interaction.token,
                  "message_id": int(message) if message != "@original" else message,
                  "content": content,
                  "embeds": embeds,
                  "files": files,
                  "allowed_mentions": self.get_allowed_mentions(allowed_mentions),
                  "attachments": _att,
                  "components": components}
        try:
            msg = self.http.edit_interaction_response(**params)
            if isinstance(msg, dict):
                return Message.create(self, msg, interaction_token=interaction_token or interaction.token, original_response=message is None or message == "@original")
            return wrap_to_async(Message, self, msg, interaction_token=interaction_token or interaction.token, original_response=message is None or message == "@original")
        finally:
            if files:
                [x.close() for x in files if not x.closed]

    @property
    def edit_followup_message(self):
        """Alias of :meth:`.edit_interaction_response`."""
        return self.edit_interaction_response

    def delete_interaction_response(self,
                                    interaction: Optional[Interaction.TYPING] = None,
                                    message: Message.TYPING = "@original",
                                    *,
                                    interaction_token: Optional[str] = None,
                                    application_id: Optional[Snowflake.TYPING] = None):
        """
        Deletes interaction response.

        :param interaction: Interaction to delete response.
        :param message: Message to delete.
        :param Optional[str] interaction_token: Token of the interaction, if parameter ``interaction`` is not an Interaction instance.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        if not isinstance(interaction, Interaction) and not interaction_token:
            raise TypeError("you must pass interaction_token if interaction is not dico.Interaction object.")
        return self.http.delete_interaction_response(int(application_id or self.application_id), interaction_token or interaction.token, int(message) if message != "@original" else message)

    def request_guild_application_command_permissions(self,
                                                      guild: Guild.TYPING,
                                                      *, application_id: Optional[Snowflake.TYPING] = None) -> GuildApplicationCommandPermissions.RESPONSE_AS_LIST:
        """
        Requests guild application command permissions.

        :param guild: Guild to request application command permissions.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :return: List[:class:`~.GuildApplicationCommandPermissions`]
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        resp = self.http.request_guild_application_command_permissions(int(application_id or self.application_id), int(guild))
        if isinstance(resp, list):
            return [GuildApplicationCommandPermissions(x) for x in resp]
        return wrap_to_async(GuildApplicationCommandPermissions, None, resp, as_create=False)

    def request_application_command_permissions(self,
                                                guild: Guild.TYPING,
                                                command: ApplicationCommand.TYPING,
                                                *, application_id: Optional[Snowflake.TYPING] = None) -> GuildApplicationCommandPermissions.RESPONSE:
        """
        Requests application command permissions.

        :param guild: Guild to request application command permissions.
        :param command: Command to request permissions.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :return: :class:`~.GuildApplicationCommandPermissions`
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        resp = self.http.request_application_command_permissions(int(application_id or self.application_id), int(guild), int(command))
        if isinstance(resp, dict):
            return GuildApplicationCommandPermissions(resp)
        return wrap_to_async(GuildApplicationCommandPermissions, None, resp, as_create=False)

    def edit_application_command_permissions(self,
                                             guild: Guild.TYPING,
                                             command: ApplicationCommand.TYPING,
                                             *permissions: Union[dict, ApplicationCommandPermissions],
                                             application_id: Optional[Snowflake.TYPING] = None) -> GuildApplicationCommandPermissions.RESPONSE:
        """
        Edits application command permissions.

        :param guild: Guild to edit application command permissions.
        :param command: Command to edit permissions.
        :param permissions: Permissions to edit.
        :type permissions: Union[dict, :class:`~.GuildApplicationCommandPermissions`]
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :return: :class:`~.GuildApplicationCommandPermissions`
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        permissions = [x if isinstance(x, dict) else x.to_dict() for x in permissions]
        resp = self.http.edit_application_command_permissions(int(application_id or self.application_id), int(guild), int(command), permissions)
        if isinstance(resp, dict):
            return GuildApplicationCommandPermissions(resp)
        return wrap_to_async(GuildApplicationCommandPermissions, None, resp, as_create=False)

    def batch_edit_application_command_permissions(self,
                                                   guild: Guild.TYPING,
                                                   permissions_dict: Dict[ApplicationCommand.TYPING, List[Union[dict, ApplicationCommandPermissions]]],
                                                   *, application_id: Optional[Snowflake.TYPING] = None) -> GuildApplicationCommandPermissions.RESPONSE_AS_LIST:
        """
        Batch edits application command permissions.

        :param guild: Guild to edit application command permissions.
        :param permissions_dict: Dict of command: permission.
        :param application_id: ID of the application, if ``application_id`` is not set on the client.
        :return: List[:class:`~.GuildApplicationCommandPermissions`]
        """
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        permissions_dicts = [{"id": str(int(k)), "permissions": [x if isinstance(x, dict) else x.to_dict() for x in v]} for k, v in permissions_dict.items()]
        resp = self.http.batch_edit_application_command_permissions(int(application_id or self.application_id), int(guild), permissions_dicts)
        if isinstance(resp, list):
            return [GuildApplicationCommandPermissions(x) for x in resp]
        return wrap_to_async(GuildApplicationCommandPermissions, None, resp, as_create=False)

    # OAuth2

    def request_current_bot_application_information(self) -> Application.RESPONSE:
        """
        Requests current bot application information.

        :return: :class:`~.Application`
        """
        resp = self.http.request_current_bot_application_information()
        if isinstance(resp, dict):
            return Application(self, resp)
        return wrap_to_async(Application, self, resp, as_create=False)

    # Gateway

    def request_gateway(self, *, bot: bool = True) -> Union[GetGateway, Awaitable[GetGateway]]:
        """
        Requests gateway.

        :param bool bot: Whether this client is bot. This must be ``True``.
        :return: :class:`~.GetGateway`
        """
        resp = self.http.request_gateway(bot)
        if isinstance(resp, dict):
            return GetGateway(resp)
        return wrap_to_async(GetGateway, None, resp, as_create=False)

    # Misc

    def get_allowed_mentions(self, allowed_mentions):
        """
        Automatically converts allowed_mentions to dict.

        :param allowed_mentions: Allowed mentions.
        :return: dict
        """
        _all_men = allowed_mentions or self.default_allowed_mentions
        if _all_men and not isinstance(_all_men, dict):
            _all_men = _all_men.to_dict()
        return _all_men

    @property
    def get(self):
        """Empty function that may be implemented if cache is present of the client."""
        raise NotImplementedError

    @property
    def has_cache(self) -> bool:
        """Whether this client supports caching."""
        return hasattr(self, "cache")
