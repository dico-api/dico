import io
import typing
import datetime
from .base.http import HTTPRequestBase, EmptyObject
from .model import Channel, Message, MessageReference, AllowedMentions, Snowflake, Embed, Attachment, Overwrite, \
    Emoji, User, Interaction, InteractionResponse, Webhook, Guild, ApplicationCommand, Invite, Application, FollowedChannel, \
    ThreadMember, ListThreadsResponse, Component, Role, ApplicationCommandOption, GuildApplicationCommandPermissions, \
    ApplicationCommandPermissions, VerificationLevel, DefaultMessageNotificationLevel, ExplicitContentFilterLevel, \
    SystemChannelFlags, GuildPreview, ChannelTypes, GuildMember, Ban, PermissionFlags, GuildWidget, FILE_TYPE, \
    VoiceRegion, Integration, ApplicationCommandTypes, WelcomeScreen, WelcomeScreenChannel
from .utils import from_emoji, wrap_to_async, to_image_data

if typing.TYPE_CHECKING:
    from .base.model import AbstractObject


class APIClient:
    """
    REST API handling client.

    :param token: Token of the client.
    :param base: HTTP request handler to use. Must inherit :class:`.base.http.HTTPRequestBase`.
    :param default_allowed_mentions: Default :class:`.model.channel.AllowedMentions` object to use. Default None.
    :param application_id: ID of the application. Required if you use interactions.
    :param **http_options: Options of HTTP request handler.

    :ivar http: HTTP request client.
    :ivar default_allowed_mentions: Default :class:`.model.channel.AllowedMentions` object of the API client.
    :ivar application_id: ID of the application. Can be ``None``, and if it is, you must pass parameter application_id for all methods that has it.
    """

    def __init__(self,
                 token: str,
                 *,
                 base: typing.Type[HTTPRequestBase],
                 default_allowed_mentions: typing.Optional[AllowedMentions] = None,
                 application_id: typing.Optional[Snowflake.TYPING] = None,
                 **http_options):
        self.http: HTTPRequestBase = base.create(token, **http_options)
        self.default_allowed_mentions: typing.Optional[AllowedMentions] = default_allowed_mentions
        self.application_id: typing.Optional[Snowflake] = Snowflake.ensure_snowflake(application_id)

    # Channel

    def request_channel(self, channel: Channel.TYPING) -> Channel.RESPONSE:
        channel = self.http.request_channel(int(channel))
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def modify_guild_channel(self,
                             channel: Channel.TYPING,
                             *,
                             name: str = None,
                             channel_type: int = None,
                             position: int = EmptyObject,
                             topic: str = EmptyObject,
                             nsfw: bool = EmptyObject,
                             rate_limit_per_user: int = EmptyObject,
                             bitrate: int = EmptyObject,
                             user_limit: int = EmptyObject,
                             permission_overwrites: typing.List[Overwrite] = EmptyObject,
                             parent: Channel.TYPING = EmptyObject,
                             rtc_region: str = EmptyObject,
                             video_quality_mode: int = EmptyObject,
                             reason: str = None) -> Channel.RESPONSE:
        if permission_overwrites:
            permission_overwrites = [x.to_dict() for x in permission_overwrites]
        if parent:
            parent = int(parent)
        channel = self.http.modify_guild_channel(int(channel), name, channel_type, position, topic, nsfw, rate_limit_per_user,
                                                 bitrate, user_limit, permission_overwrites, parent, rtc_region, video_quality_mode, reason=reason)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def modify_group_dm_channel(self, channel: Channel.TYPING, *, name: str = None, icon: bin = None, reason: str = None) -> Channel.RESPONSE:
        channel = self.http.modify_group_dm_channel(int(channel), name, icon, reason=reason)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def modify_thread_channel(self,
                              channel: Channel.TYPING, *,
                              name: str = None,
                              archived: bool = None,
                              auto_archive_duration: int = None,
                              locked: bool = None,
                              rate_limit_per_user: int = EmptyObject,
                              reason: str = None) -> Channel.RESPONSE:
        channel = self.http.modify_thread_channel(int(channel), name, archived, auto_archive_duration, locked, rate_limit_per_user, reason=reason)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def delete_channel(self, channel: Channel.TYPING, *, reason: str = None) -> Channel.RESPONSE:
        return self.http.delete_channel(int(channel), reason=reason)

    def request_channel_messages(self,
                                 channel: Channel.TYPING, *,
                                 around: Message.TYPING = None,
                                 before: Message.TYPING = None,
                                 after: Message.TYPING = None,
                                 limit: int = 50) -> Message.RESPONSE_AS_LIST:
        messages = self.http.request_channel_messages(int(channel), around and str(int(around)), before and str(int(before)), after and str(int(after)), limit)
        # This looks unnecessary, but this is to ensure they are all numbers.
        if isinstance(messages, list):
            messages = [Message.create(self, x) for x in messages]
        return wrap_to_async(Message, self, messages)

    def request_channel_message(self, channel: Channel.TYPING, message: Message.TYPING) -> Message.RESPONSE:
        message = self.http.request_channel_message(int(channel), int(message))
        if isinstance(message, dict):
            message = Message.create(self, channel)
        return wrap_to_async(Message, self, message)

    def create_message(self,
                       channel: Channel.TYPING,
                       content: str = None,
                       *,
                       embed: typing.Union[Embed, dict] = None,
                       embeds: typing.List[typing.Union[Embed, dict]] = None,
                       file: FILE_TYPE = None,
                       files: typing.List[FILE_TYPE] = None,
                       tts: bool = False,
                       allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                       message_reference: typing.Union[Message, MessageReference, dict] = None,
                       component: typing.Union[dict, Component] = None,
                       components: typing.List[typing.Union[dict, Component]] = None) -> Message.RESPONSE:
        """
        Sends message create request to API.

        .. note::
            - FileIO object passed to ``file`` or ``files`` parameter will be automatically closed when requesting,
              therefore it is recommended to pass file path.

        .. warning::
            - You must pass at least one of ``content`` or ``embed`` or ``file`` or ``files`` parameter.
            - You can't use ``file`` and ``files`` at the same time.

        :param channel: Channel to create message. Accepts both :class:`.model.channel.Channel` and channel ID.
        :param content: Content of the message.
        :param embed: Embed of the message.
        :param embeds: List of embeds of the message.
        :param file: File of the message.
        :param files: Files of the message.
        :param tts: Whether to speak message.
        :param allowed_mentions: :class:`.model.channel.AllowedMentions` to use for this request.
        :param message_reference: Message to reply.
        :param component: Component of the message.
        :param components: List of  components of the message.
        :return: Union[:class:`.model.channel.Message`, Coroutine[dict]]
        """
        if files and file:
            raise TypeError("you can't pass both file and files.")
        if file:
            files = [file]
        if files:
            for x in range(len(files)):
                sel = files[x]
                if not isinstance(sel, io.FileIO):
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
        params = {"channel_id": int(channel),
                  "content": content,
                  "embeds": embeds,
                  "nonce": None,  # What does this do tho?
                  "message_reference": message_reference,
                  "tts": tts,
                  "allowed_mentions": self.get_allowed_mentions(allowed_mentions),
                  "components": components}
        if files:
            params["files"] = files
        try:
            msg = self.http.create_message_with_files(**params) if files else self.http.create_message(**params)
            if isinstance(msg, dict):
                msg = Message.create(self, msg)
            return wrap_to_async(Message, self, msg)
        finally:
            if files:
                [x.close() for x in files if not x.closed]

    def crosspost_message(self,
                          channel: Channel.TYPING,
                          message: Message.TYPING) -> Message.RESPONSE:
        msg = self.http.crosspost_message(int(channel), int(message))
        if isinstance(msg, dict):
            return Message.create(self, msg)
        return wrap_to_async(Message, self, msg)

    def create_reaction(self,
                        channel: Channel.TYPING,
                        message: Message.TYPING,
                        emoji: typing.Union[str, Emoji]):
        return self.http.create_reaction(int(channel), int(message), from_emoji(emoji))

    def delete_reaction(self,
                        channel: Channel.TYPING,
                        message: Message.TYPING,
                        emoji: typing.Union[str, Emoji],
                        user: User.TYPING = "@me"):
        return self.http.delete_reaction(int(channel), int(message), from_emoji(emoji), int(user) if user != "@me" else user)

    def request_reactions(self,
                          channel: Channel.TYPING,
                          message: Message.TYPING,
                          emoji: typing.Union[str, Emoji],
                          after: User.TYPING = None,
                          limit: int = None) -> User.RESPONSE_AS_LIST:
        users = self.http.request_reactions(int(channel), int(message), from_emoji(emoji), int(after), limit)
        if isinstance(users, list):
            return [User.create(self, x) for x in users]
        return wrap_to_async(User, self, users)

    def delete_all_reactions(self, channel: Channel.TYPING, message: Message.TYPING):
        return self.http.delete_all_reactions(int(channel), int(message))

    def delete_all_reactions_emoji(self,
                                   channel: Channel.TYPING,
                                   message: Message.TYPING,
                                   emoji: typing.Union[str, Emoji]):
        return self.http.delete_all_reactions_emoji(int(channel), int(message), from_emoji(emoji))

    def edit_message(self,
                     channel: Channel.TYPING,
                     message: Message.TYPING,
                     *,
                     content: str = None,
                     embed: typing.Union[Embed, dict] = EmptyObject,
                     embeds: typing.List[typing.Union[Embed, dict]] = EmptyObject,
                     file: FILE_TYPE = EmptyObject,
                     files: typing.List[FILE_TYPE] = EmptyObject,
                     allowed_mentions: typing.Union[AllowedMentions, dict] = EmptyObject,
                     attachments: typing.List[typing.Union[Attachment, dict]] = EmptyObject,
                     component: typing.Union[dict, Component] = EmptyObject,
                     components: typing.List[typing.Union[dict, Component]] = EmptyObject) -> Message.RESPONSE:
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
                    if not isinstance(sel, io.FileIO):
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
                       reason: str = None):
        return self.http.delete_message(int(channel), int(message), reason=reason)

    def bulk_delete_messages(self, channel: Channel.TYPING, *messages: Message.TYPING, reason: str = None):
        return self.http.bulk_delete_messages(int(channel), list(map(int, messages)), reason=reason)

    def edit_channel_permissions(self, channel: Channel.TYPING, overwrite: Overwrite, *, reason: str = None):
        ow_dict = overwrite.to_dict()
        return self.http.edit_channel_permissions(int(channel), ow_dict["id"], ow_dict["allow"], ow_dict["deny"], ow_dict["type"], reason=reason)

    def request_channel_invites(self, channel: Channel.TYPING) -> Invite.RESPONSE_AS_LIST:
        invites = self.http.request_channel_invites(int(channel))
        if isinstance(invites, list):
            return [Invite(self, x) for x in invites]
        return wrap_to_async(Invite, self, invites, as_create=False)

    def create_channel_invite(self,
                              channel: Channel.TYPING,
                              *,
                              max_age: int = None,
                              max_uses: int = None,
                              temporary: bool = None,
                              unique: bool = None,
                              target_type: int = None,
                              target_user: User.TYPING = None,
                              target_application: Application.TYPING = None,
                              reason: str = None) -> Invite.RESPONSE:
        invite = self.http.create_channel_invite(int(channel), max_age, max_uses, temporary, unique, target_type,
                                                 int(target_user) if target_user is not None else target_user,
                                                 int(target_application) if target_application is not None else target_application, reason=reason)
        if isinstance(invite, dict):
            return Invite(self, invite)
        return wrap_to_async(Invite, self, invite, as_create=False)

    def delete_channel_permission(self, channel: Channel.TYPING, overwrite: Overwrite, *, reason: str = None):
        return self.http.delete_channel_permission(int(channel), int(overwrite.id), reason=reason)

    def follow_news_channel(self, channel: Channel.TYPING, target_channel: Channel.TYPING) -> FollowedChannel.RESPONSE:
        fc = self.http.follow_news_channel(int(channel), str(target_channel))
        if isinstance(fc, dict):
            return FollowedChannel(self, fc)
        return wrap_to_async(FollowedChannel, self, fc, as_create=False)

    def trigger_typing_indicator(self, channel: Channel.TYPING):
        return self.http.trigger_typing_indicator(int(channel))

    def request_pinned_messages(self, channel: Channel.TYPING) -> Message.RESPONSE_AS_LIST:
        msgs = self.http.request_pinned_messages(int(channel))
        if isinstance(msgs, list):
            return [Message.create(self, x) for x in msgs]
        return wrap_to_async(Message, self, msgs)

    def pin_message(self, channel: Channel.TYPING, message: Message.TYPING, *, reason: str = None):
        return self.http.pin_message(int(channel), int(message), reason=reason)

    def unpin_message(self, channel: Channel.TYPING, message: Message.TYPING, *, reason: str = None):
        return self.http.unpin_message(int(channel), int(message), reason=reason)

    def group_dm_add_recipient(self,
                               channel: Channel.TYPING,
                               user: User.TYPING,
                               access_token: str,
                               nick: str):
        return self.http.group_dm_add_recipient(int(channel), int(user), access_token, nick)

    def group_dm_remove_recipient(self,
                                  channel: Channel.TYPING,
                                  user: User.TYPING):
        return self.http.group_dm_remove_recipient(int(channel), int(user))

    def start_thread(self,
                     channel: Channel.TYPING,
                     message: Message.TYPING = None,
                     *,
                     name: str,
                     auto_archive_duration: int,
                     reason: str = None) -> Channel.RESPONSE:
        channel = self.http.start_thread_with_message(int(channel), int(message), name, auto_archive_duration, reason=reason) if message else \
            self.http.start_thread_without_message(int(channel), name, auto_archive_duration, reason=reason)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def join_thread(self, channel: Channel.TYPING):
        return self.http.join_thread(int(channel))

    def add_thread_member(self, channel: Channel.TYPING, user: User.TYPING):
        return self.http.add_thread_member(int(channel), int(user))

    def leave_thread(self, channel: Channel.TYPING):
        return self.http.leave_thread(int(channel))

    def remove_thread_member(self, channel: Channel.TYPING, user: User.TYPING):
        return self.http.remove_thread_member(int(channel), int(user))

    def list_thread_members(self, channel: Channel.TYPING) -> ThreadMember.RESPONSE_AS_LIST:
        members = self.http.list_thread_members(int(channel))
        if isinstance(members, list):
            return [ThreadMember(self, x) for x in members]
        return wrap_to_async(ThreadMember, self, members, as_create=False)

    def list_active_threads(self, channel: Channel.TYPING) -> ListThreadsResponse.RESPONSE:
        resp = self.http.list_active_threads(int(channel))
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def list_public_archived_threads(self,
                                     channel: Channel.TYPING,
                                     *,
                                     before: typing.Union[str, datetime.datetime] = None,
                                     limit: int = None) -> ListThreadsResponse.RESPONSE:
        resp = self.http.list_public_archived_threads(int(channel), before, limit)
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def list_private_archived_threads(self,
                                      channel: Channel.TYPING,
                                      *,
                                      before: typing.Union[str, datetime.datetime] = None,
                                      limit: int = None) -> ListThreadsResponse.RESPONSE:
        resp = self.http.list_private_archived_threads(int(channel), before, limit)
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def list_joined_private_archived_threads(self,
                                             channel: Channel.TYPING,
                                             *,
                                             before: typing.Union[str, datetime.datetime] = None,
                                             limit: int = None) -> ListThreadsResponse.RESPONSE:
        resp = self.http.list_joined_private_archived_threads(int(channel), before, limit)
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    # Emoji

    def list_guild_emojis(self, guild: Guild.TYPING) -> Emoji.RESPONSE_AS_LIST:
        resp = self.http.list_guild_emojis(int(guild))
        if isinstance(resp, list):
            return [Emoji(self, x) for x in resp]
        return wrap_to_async(Emoji, self, resp, as_create=False)

    def request_guild_emoji(self, guild: Guild.TYPING, emoji: Emoji.TYPING) -> Emoji.RESPONSE:
        resp = self.http.request_guild_emoji(int(guild), int(emoji))
        if isinstance(resp, dict):
            return Emoji(self, resp)
        return wrap_to_async(Emoji, self, resp, as_create=False)

    def create_guild_emoji(self,
                           guild: Guild.TYPING,
                           *,
                           name: str,
                           image: str,
                           roles: typing.List[Role.TYPING] = None,
                           reason: str = None) -> Emoji.RESPONSE:
        resp = self.http.create_guild_emoji(int(guild), name, image, [str(int(x)) for x in roles or []], reason=reason)
        if isinstance(resp, dict):
            return Emoji(self, resp)
        return wrap_to_async(Emoji, self, resp, as_create=False)

    def modify_guild_emoji(self,
                           guild: Guild.TYPING,
                           emoji: Emoji.TYPING,
                           *,
                           name: str,
                           roles: typing.List[Role.TYPING],
                           reason: str = None) -> Emoji.RESPONSE:
        resp = self.http.modify_guild_emoji(int(guild), int(emoji), name, [str(int(x)) for x in roles], reason=reason)
        if isinstance(resp, dict):
            return Emoji(self, resp)
        return wrap_to_async(Emoji, self, resp, as_create=False)

    def delete_guild_emoji(self, guild: Guild.TYPING, emoji: Emoji.TYPING, reason: str = None):
        return self.http.delete_guild_emoji(int(guild), int(emoji), reason=reason)

    # Guild

    def create_guild(self,
                     name: str,
                     *,
                     icon: str = None,
                     verification_level: typing.Union[int, VerificationLevel] = None,
                     default_message_notifications: typing.Union[int, DefaultMessageNotificationLevel] = None,
                     explicit_content_filter: typing.Union[int, ExplicitContentFilterLevel] = None,
                     roles: typing.List[dict] = None,  # TODO: role and channel generator
                     channels: typing.List[dict] = None,
                     afk_channel_id: Snowflake.TYPING = None,
                     afk_timeout: int = None,
                     system_channel_id: Snowflake.TYPING = None,
                     system_channel_flags: typing.Union[int, SystemChannelFlags] = None) -> Guild.RESPONSE:
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
        resp = self.http.request_guild(int(guild), with_counts)
        if isinstance(resp, dict):
            return Guild.create(self, resp, ensure_cache_type="guild")
        return wrap_to_async(Guild, self, resp, ensure_cache_type="guild")

    def request_guild_preview(self, guild: Guild.TYPING) -> GuildPreview.RESPONSE:
        resp = self.http.request_guild_preview(int(guild))
        if isinstance(resp, dict):
            return GuildPreview(self, resp)
        return wrap_to_async(GuildPreview, self, resp)

    def modify_guild(self,
                     guild: Guild.TYPING,
                     *,
                     name: str = None,
                     verification_level: typing.Union[int, VerificationLevel] = None,
                     default_message_notifications: typing.Union[int, DefaultMessageNotificationLevel] = None,
                     explicit_content_filter: typing.Union[int, ExplicitContentFilterLevel] = None,
                     afk_channel: Channel.TYPING = None,
                     afk_timeout: int = None,
                     icon: str = None,
                     owner: User.TYPING = None,
                     splash: str = None,
                     discovery_splash: str = None,
                     banner: str = None,
                     system_channel: Channel.TYPING = None,
                     system_channel_flags: typing.Union[int, SystemChannelFlags] = None,
                     rules_channel: Channel.TYPING = None,
                     public_updates_channel: Channel.TYPING = None,
                     preferred_locale: str = None,
                     features: typing.List[str] = None,
                     description: str = None,
                     reason: str = None) -> Guild.RESPONSE:
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if verification_level is not None:
            kwargs["verification_level"] = int(verification_level)
        if default_message_notifications is not None:
            kwargs["default_message_notifications"] = int(default_message_notifications)
        if explicit_content_filter is not None:
            kwargs["explicit_content_filter"] = int(explicit_content_filter)
        if afk_channel is not None:
            kwargs["afk_channel_id"] = str(int(afk_channel))
        if afk_timeout is not None:
            kwargs["afk_timeout"] = afk_timeout
        if icon is not None:
            kwargs["icon"] = icon
        if owner is not None:
            kwargs["owner_id"] = str(int(owner))
        if splash is not None:
            kwargs["splash"] = splash
        if discovery_splash is not None:
            kwargs["discovery_splash"] = discovery_splash
        if banner is not None:
            kwargs["banner"] = banner
        if system_channel is not None:
            kwargs["system_channel_id"] = str(int(system_channel))
        if system_channel_flags is not None:
            kwargs["system_channel_flags"] = int(system_channel_flags)
        if rules_channel is not None:
            kwargs["rules_channel_id"] = str(int(rules_channel))
        if public_updates_channel is not None:
            kwargs["public_updates_channel_id"] = str(int(public_updates_channel))
        if preferred_locale is not None:
            kwargs["preferred_locale"] = preferred_locale
        if features is not None:
            kwargs["features"] = features
        if description is not None:
            kwargs["description"] = description
        resp = self.http.modify_guild(int(guild), **kwargs, reason=reason)
        if isinstance(resp, dict):
            return Guild.create(self, resp, ensure_cache_type="guild")
        return wrap_to_async(Guild, self, resp, ensure_cache_type="guild")

    def delete_guild(self, guild: Guild.TYPING):
        return self.http.delete_guild(int(guild))

    def request_guild_channels(self, guild: Guild.TYPING) -> Channel.RESPONSE_AS_LIST:
        channels = self.http.request_guild_channels(int(guild))
        if isinstance(channels, list):
            return [Channel.create(self, x) for x in channels]
        return wrap_to_async(Channel, self, channels)

    def create_guild_channel(self,
                             guild: Guild.TYPING,
                             name: str,
                             *,
                             channel_type: typing.Union[int, ChannelTypes] = None,
                             topic: str = None,
                             bitrate: int = None,
                             user_limit: int = None,
                             rate_limit_per_user: int = None,
                             position: int = None,
                             permission_overwrites: typing.Union[dict, Overwrite] = None,
                             parent: Channel.TYPING = None,
                             nsfw: bool = None,
                             reason: str = None) -> Channel.RESPONSE:
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

    def modify_guild_channel_positions(self, guild: Guild.TYPING, *params: dict, reason: str = None):
        # You can get params by using Channel.to_position_param(...)
        return self.http.modify_guild_channel_positions(int(guild), [*params], reason=reason)

    def list_active_threads_as_guild(self, guild: Guild.TYPING) -> ListThreadsResponse.RESPONSE:
        resp = self.http.list_active_threads_as_guild(int(guild))
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def request_guild_member(self, guild: Guild.TYPING, user: User.TYPING) -> GuildMember.RESPONSE:
        resp = self.http.request_guild_member(int(guild), int(user))
        if isinstance(resp, dict):
            return GuildMember.create(self, resp, guild_id=int(guild))
        return wrap_to_async(GuildMember, self, resp, guild_id=int(guild))

    def list_guild_members(self, guild: Guild.TYPING, limit: int = None, after: str = None) -> GuildMember.RESPONSE_AS_LIST:
        resp = self.http.list_guild_members(int(guild), limit, after)
        if isinstance(resp, list):
            return [GuildMember.create(self, x, guild_id=int(guild)) for x in resp]
        return wrap_to_async(GuildMember, self, resp, guild_id=int(guild))

    def search_guild_members(self, guild: Guild.TYPING, query: str, limit: int = None) -> GuildMember.RESPONSE_AS_LIST:
        resp = self.http.search_guild_members(int(guild), query, limit)
        if isinstance(resp, list):
            return [GuildMember.create(self, x, guild_id=int(guild)) for x in resp]
        return wrap_to_async(GuildMember, self, resp, guild_id=int(guild))

    def add_guild_member(self,
                         guild: Guild.TYPING,
                         user: User.TYPING,
                         access_token: str,
                         nick: str = None,
                         roles: typing.List[Role.TYPING] = None,
                         mute: bool = None,
                         deaf: bool = None) -> GuildMember.RESPONSE:
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
                            nick: str = EmptyObject,
                            roles: typing.List[Role.TYPING] = EmptyObject,
                            mute: bool = EmptyObject,
                            deaf: bool = EmptyObject,
                            channel: Channel.TYPING = EmptyObject,
                            *,
                            reason: str = None) -> GuildMember.RESPONSE:
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
            kwargs["channel_id"] = int(channel) if channel else channel
        resp = self.http.modify_guild_member(int(guild), int(user), **kwargs, reason=reason)
        if isinstance(resp, dict):
            return GuildMember.create(self, resp, guild_id=int(guild))
        return wrap_to_async(GuildMember, self, resp, guild_id=int(guild))

    def modify_current_user_nick(self, guild: Guild.TYPING, nick: typing.Union[str, None] = EmptyObject, *, reason: str = None):
        return self.http.modify_current_user_nick(int(guild), nick, reason=reason)

    def add_guild_member_role(self,
                              guild: Guild.TYPING,
                              user: User.TYPING,
                              role: Role.TYPING,
                              *,
                              reason: str = None):
        return self.http.add_guild_member_role(int(guild), int(user), int(role), reason=reason)

    def remove_guild_member_role(self,
                                 guild: Guild.TYPING,
                                 user: User.TYPING,
                                 role: Role.TYPING,
                                 *,
                                 reason: str = None):
        return self.http.remove_guild_member_role(int(guild), int(user), int(role), reason=reason)

    def remove_guild_member(self, guild: Guild.TYPING, user: User.TYPING):
        return self.http.remove_guild_member(int(guild), int(user))

    @property
    def kick(self):
        return self.remove_guild_member

    def request_guild_bans(self, guild: Guild.TYPING) -> Ban.RESPONSE_AS_LIST:
        resp = self.http.request_guild_bans(int(guild))
        if isinstance(resp, list):
            return [Ban(self, x) for x in resp]
        return wrap_to_async(Ban, self, resp, as_create=False)

    def request_guild_ban(self, guild: Guild.TYPING, user: User.TYPING) -> Ban.RESPONSE:
        resp = self.http.request_guild_ban(int(guild), int(user))
        if isinstance(resp, dict):
            return Ban(self, resp)
        return wrap_to_async(Ban, self, resp, as_create=False)

    def create_guild_ban(self,
                         guild: Guild.TYPING,
                         user: User.TYPING,
                         *,
                         delete_message_days: int = None,
                         reason: str = None):
        return self.http.create_guild_ban(int(guild), int(user), delete_message_days, reason)

    @property
    def ban(self):
        return self.create_guild_ban

    def remove_guild_ban(self,
                         guild: Guild.TYPING,
                         user: User.TYPING,
                         *,
                         reason: str = None):
        return self.remove_guild_ban(int(guild), int(user), reason=reason)

    def request_guild_roles(self, guild: Guild.TYPING) -> Role.RESPONSE_AS_LIST:
        resp = self.http.request_guild_roles(int(guild))
        if isinstance(resp, list):
            return [Role.create(self, x, guild_id=int(guild)) for x in resp]
        return wrap_to_async(Role, self, resp, guild_id=int(guild))

    def create_guild_role(self,
                          guild: Guild.TYPING,
                          *,
                          name: str = None,
                          permissions: typing.Union[int, str, PermissionFlags] = None,
                          color: int = None,
                          hoist: bool = None,
                          mentionable: bool = None,
                          reason: str = None) -> Role.RESPONSE:
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

    def modify_guild_role_positions(self, guild: Guild.TYPING, *params: dict, reason: str = None) -> Role.RESPONSE_AS_LIST:
        # You can get params by using Role.to_position_param(...)
        resp = self.http.modify_guild_role_positions(int(guild), [*params], reason=reason)
        if isinstance(resp, list):
            return [Role.create(self, x, guild_id=int(guild)) for x in resp]
        return wrap_to_async(Role, self, resp, guild_id=int(guild))

    def modify_guild_role(self,
                          guild: Guild.TYPING,
                          role: Role.TYPING,
                          *,
                          name: str = EmptyObject,
                          permissions: typing.Union[int, str, PermissionFlags] = EmptyObject,
                          color: int = EmptyObject,
                          hoist: bool = EmptyObject,
                          mentionable: bool = EmptyObject,
                          reason: str = None) -> Role.RESPONSE:
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

    def delete_guild_role(self, guild: Guild.TYPING, role: Role.TYPING, *, reason: str = None):
        return self.http.delete_guild_role(int(guild), int(role), reason=reason)

    def request_guild_prune_count(self, guild: Guild.TYPING, *, days: int = None, include_roles: typing.List[Role.TYPING] = None) -> "AbstractObject.RESPONSE":
        from .base.model import AbstractObject
        if include_roles is not None:
            include_roles = [*map(str, include_roles)]
        resp = self.http.request_guild_prune_count(int(guild), days, include_roles)
        if isinstance(resp, dict):
            return AbstractObject(resp)
        return wrap_to_async(AbstractObject, None, resp, as_create=False)

    def begin_guild_prune(self,
                          guild: Guild.TYPING,
                          *,
                          days: int = 7,
                          compute_prune_count: bool = True,
                          include_roles: typing.List[Role.TYPING] = None,
                          reason: str = None) -> "AbstractObject.RESPONSE":
        from .base.model import AbstractObject
        if include_roles is not None:
            include_roles = [*map(str, include_roles)]
        resp = self.http.begin_guild_prune(int(guild), days, compute_prune_count, include_roles, reason=reason)
        if isinstance(resp, dict):
            return AbstractObject(resp)
        return wrap_to_async(AbstractObject, None, resp, as_create=False)

    def request_guild_voice_regions(self, guild: Guild.TYPING) -> VoiceRegion.RESPONSE_AS_LIST:
        resp = self.http.request_guild_voice_regions(int(guild))
        if isinstance(resp, list):
            return [VoiceRegion(x) for x in resp]
        return wrap_to_async(VoiceRegion, None, resp, as_create=False)

    def request_guild_invites(self, guild: Guild.TYPING) -> Invite.RESPONSE_AS_LIST:
        resp = self.http.request_guild_invites(int(guild))
        if isinstance(resp, list):
            return [Invite(self, x) for x in resp]
        return wrap_to_async(Invite, self, resp, as_create=False)

    def request_guild_integrations(self, guild: Guild.TYPING) -> Integration.RESPONSE_AS_LIST:
        resp = self.http.request_guild_integrations(int(guild))
        if isinstance(resp, list):
            return [Integration(self, x) for x in resp]
        return wrap_to_async(Integration, self, resp, as_create=False)

    def delete_guild_integration(self, guild: Guild.TYPING, integration: Integration.TYPING, *, reason: str = None):
        return self.http.delete_guild_integration(int(guild), int(integration), reason=reason)

    def request_guild_widget_settings(self, guild: Guild.TYPING) -> GuildWidget.RESPONSE:
        resp = self.http.request_guild_widget_settings(int(guild))
        if isinstance(resp, dict):
            return GuildWidget(resp)
        return wrap_to_async(GuildWidget, None, resp, as_create=False)

    def modify_guild_widget(self, guild: Guild.TYPING, *, enabled: bool = None, channel: Channel.TYPING = EmptyObject, reason: str = None) -> GuildWidget.RESPONSE:
        resp = self.http.modify_guild_widget(int(guild), enabled, channel, reason=reason)
        if isinstance(resp, dict):
            return GuildWidget(resp)
        return wrap_to_async(GuildWidget, None, resp, as_create=False)

    def request_guild_widget(self, guild: Guild.TYPING) -> "AbstractObject.RESPONSE":
        from .base.model import AbstractObject
        resp = self.http.request_guild_widget(int(guild))
        if isinstance(resp, dict):
            return AbstractObject(resp)
        return wrap_to_async(AbstractObject, None, resp, as_create=False)

    def request_guild_vanity_url(self, guild: Guild.TYPING) -> "AbstractObject.RESPONSE":
        from .base.model import AbstractObject
        resp = self.http.request_guild_vanity_url(int(guild))
        if isinstance(resp, dict):
            return AbstractObject(resp)
        return wrap_to_async(AbstractObject, None, resp, as_create=False)

    def request_guild_widget_image(self, guild: Guild.TYPING, style: typing.Optional[str] = None) -> bytes:
        return self.http.request_guild_widget_image(int(guild), style)

    def request_guild_welcome_screen(self, guild: Guild.TYPING) -> WelcomeScreen.RESPONSE:
        resp = self.http.request_guild_welcome_screen(int(guild))
        if isinstance(resp, dict):
            return WelcomeScreen(resp)
        return wrap_to_async(WelcomeScreen, None, resp, as_create=False)

    def modify_guild_welcome_screen(self,
                                    guild: Guild.TYPING,
                                    *,
                                    enabled: bool = EmptyObject,
                                    welcome_channels: typing.List[typing.Union[WelcomeScreenChannel, dict]] = EmptyObject,
                                    description: str = EmptyObject,
                                    reason: str = None) -> WelcomeScreen.RESPONSE:
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
                                suppress: bool = None,
                                request_to_speak_timestamp: typing.Union[datetime.datetime, str] = None):
        user = int(user) if user != "@me" else user
        if request_to_speak_timestamp is not None:
            request_to_speak_timestamp = request_to_speak_timestamp if isinstance(request_to_speak_timestamp, str) else \
                request_to_speak_timestamp.isoformat()
        return self.http.modify_user_voice_state(int(guild), str(int(channel)), user, suppress, request_to_speak_timestamp)

    # Invite

    def request_invite(self, invite_code: typing.Union[str, Invite], *, with_counts: bool = None, with_expiration: bool = None) -> Invite.RESPONSE:
        resp = self.http.request_invite(str(invite_code), with_counts, with_expiration)
        if isinstance(resp, dict):
            return Invite(self, resp)
        return wrap_to_async(Invite, self, resp, as_create=False)

    def delete_invite(self, invite_code, *, reason: str = None) -> Invite.RESPONSE:
        resp = self.http.delete_invite(str(invite_code), reason=reason)
        if isinstance(resp, dict):
            return Invite(self, resp)
        return wrap_to_async(Invite, self, resp, as_create=False)

    # User

    def request_user(self, user: User.TYPING = "@me") -> User.RESPONSE:
        resp = self.http.request_user(int(user) if user != "@me" else user)
        if isinstance(resp, dict):
            return User.create(self, resp)
        return wrap_to_async(User, self, resp)

    def modify_current_user(self, username: str = None, avatar: typing.Union[FILE_TYPE] = EmptyObject) -> User.RESPONSE:
        avatar = to_image_data(avatar) if avatar is not None or avatar is not EmptyObject else avatar
        resp = self.http.modify_current_user(username, avatar)
        if isinstance(resp, dict):
            return User.create(self, resp)
        return wrap_to_async(User, self, resp)

    def request_current_user_guilds(self) -> Guild.RESPONSE_AS_LIST:
        resp = self.http.request_current_user_guilds()
        if isinstance(resp, list):
            return [Guild.create(self, x) for x in resp]
        return wrap_to_async(Guild, self, resp)

    def leave_guild(self, guild: Guild.TYPING):
        return self.leave_guild(int(guild))

    def create_dm(self, recipient: User.TYPING) -> Channel.RESPONSE:
        resp = self.http.create_dm(str(int(recipient)))
        if isinstance(resp, dict):
            return Channel.create(self, resp)
        return wrap_to_async(Channel, self, resp)

    def create_group_dm(self, access_tokens: typing.List[str], nicks: typing.Dict[User.TYPING, str]):
        nicks = {str(int(k)): v for k, v in nicks.items()}
        resp = self.http.create_group_dm(access_tokens, nicks)
        if isinstance(resp, dict):
            return Channel.create(self, resp)
        return wrap_to_async(Channel, self, resp)

    # Webhook

    def create_webhook(self, channel: Channel.TYPING, *, name: str = None, avatar: str = None) -> Webhook.RESPONSE:
        hook = self.http.create_webhook(int(channel), name, avatar)
        if isinstance(hook, dict):
            return Webhook(self, hook)
        return wrap_to_async(Webhook, self, hook, as_create=False)

    def request_channel_webhooks(self, channel: Channel.TYPING) -> Webhook.RESPONSE_AS_LIST:
        hooks = self.http.request_channel_webhooks(int(channel))
        if isinstance(hooks, list):
            return [Webhook(self, x) for x in hooks]
        return wrap_to_async(Webhook, self, hooks, as_create=False)

    def request_guild_webhooks(self, guild: Guild.TYPING) -> Webhook.RESPONSE_AS_LIST:
        hooks = self.http.request_guild_webhooks(int(guild))
        if isinstance(hooks, list):
            return [Webhook(self, x) for x in hooks]
        return wrap_to_async(Webhook, self, hooks, as_create=False)

    def request_webhook(self, webhook: Webhook.TYPING, webhook_token: str = None) -> Webhook.RESPONSE:  # Requesting webhook using webhook, seems legit.
        if isinstance(webhook, Webhook):
            webhook_token = webhook_token or webhook.token
        hook = self.http.request_webhook(int(webhook)) if not webhook_token else self.http.request_webhook_with_token(int(webhook), webhook_token)
        if isinstance(hook, dict):
            return Webhook(self, hook)
        return wrap_to_async(Webhook, self, hook, as_create=False)

    def modify_webhook(self,
                       webhook: Webhook.TYPING,
                       *,
                       webhook_token: str = None,
                       name: str = None,
                       avatar: str = None,
                       channel: Channel.TYPING = None) -> Webhook.RESPONSE:
        hook = self.http.modify_webhook(int(webhook), name, avatar, str(int(channel)) if channel is not None else channel) if not webhook_token \
            else self.http.modify_webhook_with_token(int(webhook), webhook_token, name, avatar)
        if isinstance(hook, dict):
            return Webhook(self, hook)
        return wrap_to_async(Webhook, self, hook, as_create=False)

    def delete_webhook(self, webhook: Webhook.TYPING, webhook_token: str = None):
        return self.http.delete_webhook(int(webhook)) if not webhook_token else self.http.delete_webhook_with_token(int(webhook), webhook_token)

    def execute_webhook(self,
                        webhook: Webhook.TYPING,
                        *,
                        webhook_token: str = None,
                        wait: bool = None,
                        thread: Channel.TYPING = None,
                        content: str = None,
                        username: str = None,
                        avatar_url: str = None,
                        tts: bool = False,
                        file: FILE_TYPE = None,
                        files: typing.List[FILE_TYPE] = None,
                        embed: typing.Union[Embed, dict] = None,
                        embeds: typing.List[typing.Union[Embed, dict]] = None,
                        allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                        components: typing.List[typing.Union[dict, Component]] = None) -> Message.RESPONSE:
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
                if not isinstance(sel, io.FileIO):
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
                                webhook_token: str = None) -> Message.RESPONSE:
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
                             webhook_token: str = None,
                             content: str = EmptyObject,
                             embed: typing.Union[Embed, dict] = EmptyObject,
                             embeds: typing.List[typing.Union[Embed, dict]] = EmptyObject,
                             file: FILE_TYPE = EmptyObject,
                             files: typing.List[FILE_TYPE] = EmptyObject,
                             allowed_mentions: typing.Union[AllowedMentions, dict] = EmptyObject,
                             attachments: typing.List[typing.Union[Attachment, dict]] = EmptyObject,
                             component: typing.Union[dict, Component] = EmptyObject,
                             components: typing.List[typing.Union[dict, Component]] = EmptyObject) -> Message.RESPONSE:
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
                    if not isinstance(sel, io.FileIO):
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
                               webhook_token: str = None):
        if not isinstance(webhook, Webhook) and not webhook_token:
            raise TypeError("you must pass webhook_token if webhook is not dico.Webhook object.")
        return self.http.delete_webhook_message(int(webhook), webhook_token or webhook.token, int(message))

    # Interaction

    def request_application_commands(self,
                                     guild: Guild.TYPING = None,
                                     *,
                                     application_id: Snowflake.TYPING = None) -> ApplicationCommand.RESPONSE_AS_LIST:
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        app_commands = self.http.request_application_commands(int(application_id or self.application_id), int(guild) if guild else guild)
        if isinstance(app_commands, list):
            return [ApplicationCommand.create(x) for x in app_commands]
        return wrap_to_async(ApplicationCommand, None, app_commands)

    def create_application_command(self,
                                   guild: Guild.TYPING = None,
                                   *,
                                   name: str,
                                   description: str = None,
                                   options: typing.List[typing.Union[ApplicationCommandOption, dict]] = None,
                                   default_permission: bool = None,
                                   command_type: typing.Union[ApplicationCommandTypes, int] = None,
                                   application_id: Snowflake.TYPING = None) -> ApplicationCommand.RESPONSE:
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
                                    guild: Guild.TYPING = None,
                                    application_id: Snowflake.TYPING = None) -> ApplicationCommand.RESPONSE:
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
                                 name: str = None,
                                 description: str = None,
                                 options: typing.List[typing.Union[ApplicationCommandOption, dict]] = None,
                                 default_permission: bool = None,
                                 guild: Guild.TYPING = None,
                                 application_id: Snowflake.TYPING = None) -> ApplicationCommand.RESPONSE:
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
                                   guild: Guild.TYPING = None,
                                   application_id: Snowflake.TYPING = None):
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        command_id = int(command)
        return self.http.delete_application_command(int(application_id or self.application_id), command_id, int(guild) if guild else guild)

    def bulk_overwrite_application_commands(self,
                                            *commands: typing.Union[dict, ApplicationCommand],
                                            guild: Guild.TYPING = None,
                                            application_id: Snowflake.TYPING = None) -> ApplicationCommand.RESPONSE_AS_LIST:
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        commands = [x if isinstance(x, dict) else x.to_dict() for x in commands]
        app_commands = self.http.bulk_overwrite_application_commands(int(application_id or self.application_id), commands, int(guild) if guild else guild)
        if isinstance(app_commands, list):
            return [ApplicationCommand.create(x) for x in app_commands]
        return wrap_to_async(ApplicationCommand, None, app_commands)

    def create_interaction_response(self,
                                    interaction: Interaction.TYPING,
                                    interaction_response: InteractionResponse,
                                    *,
                                    interaction_token: str = None):
        if not isinstance(interaction, Interaction) and not interaction_token:
            raise TypeError("you must pass interaction_token if interaction is not dico.Interaction object.")
        return self.http.create_interaction_response(int(interaction), interaction_token or interaction.token, interaction_response.to_dict())

    def request_interaction_response(self,
                                     interaction: Interaction.TYPING = None,
                                     message: Message.TYPING = "@original",
                                     *,
                                     interaction_token: str = None,
                                     application_id: Snowflake.TYPING = None) -> Message.RESPONSE:
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
                                interaction: Interaction.TYPING = None,
                                *,
                                interaction_token: str = None,
                                application_id: Snowflake.TYPING = None,
                                content: str = None,
                                username: str = None,
                                avatar_url: str = None,
                                tts: bool = False,
                                file: FILE_TYPE = None,
                                files: typing.List[FILE_TYPE] = None,
                                embed: typing.Union[Embed, dict] = None,
                                embeds: typing.List[typing.Union[Embed, dict]] = None,
                                allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                                components: typing.List[typing.Union[dict, Component]] = None,
                                ephemeral: bool = False) -> Message.RESPONSE:
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
                if not isinstance(sel, io.FileIO):
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
                                  interaction: Interaction.TYPING = None,
                                  message: Message.TYPING = "@original",
                                  *,
                                  interaction_token: str = None,
                                  application_id: Snowflake.TYPING = None,
                                  content: str = EmptyObject,
                                  file: FILE_TYPE = EmptyObject,
                                  files: typing.List[FILE_TYPE] = EmptyObject,
                                  embed: typing.Union[Embed, dict] = EmptyObject,
                                  embeds: typing.List[typing.Union[Embed, dict]] = EmptyObject,
                                  allowed_mentions: typing.Union[AllowedMentions, dict] = EmptyObject,
                                  attachments: typing.List[typing.Union[Attachment, dict]] = EmptyObject,
                                  component: typing.Union[dict, Component] = EmptyObject,
                                  components: typing.List[typing.Union[dict, Component]] = EmptyObject) -> Message.RESPONSE:
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
                    if not isinstance(sel, io.FileIO):
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
        return self.edit_interaction_response

    def delete_interaction_response(self,
                                    interaction: Interaction.TYPING = None,
                                    message: Message.TYPING = "@original",
                                    *,
                                    interaction_token: str = None,
                                    application_id: Snowflake.TYPING = None):
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        if not isinstance(interaction, Interaction) and not interaction_token:
            raise TypeError("you must pass interaction_token if interaction is not dico.Interaction object.")
        return self.http.delete_interaction_response(int(application_id or self.application_id), interaction_token or interaction.token, int(message) if message != "@original" else message)

    def request_guild_application_command_permissions(self, guild: Guild.TYPING, *, application_id: Snowflake.TYPING = None) -> GuildApplicationCommandPermissions.RESPONSE_AS_LIST:
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        resp = self.http.request_guild_application_command_permissions(int(application_id or self.application_id), int(guild))
        if isinstance(resp, list):
            return [GuildApplicationCommandPermissions(x) for x in resp]
        return wrap_to_async(GuildApplicationCommandPermissions, None, resp, as_create=False)

    def request_application_command_permissions(self,
                                                guild: Guild.TYPING,
                                                command: ApplicationCommand.TYPING,
                                                *, application_id: Snowflake.TYPING = None) -> GuildApplicationCommandPermissions.RESPONSE:
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        resp = self.http.request_application_command_permissions(int(application_id or self.application_id), int(guild), int(command))
        if isinstance(resp, dict):
            return GuildApplicationCommandPermissions(resp)
        return wrap_to_async(GuildApplicationCommandPermissions, None, resp, as_create=False)

    def edit_application_command_permissions(self,
                                             guild: Guild.TYPING,
                                             command: ApplicationCommand.TYPING,
                                             *permissions: typing.Union[dict, ApplicationCommandPermissions],
                                             application_id: Snowflake.TYPING = None) -> GuildApplicationCommandPermissions.RESPONSE:
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        permissions = [x if isinstance(x, dict) else x.to_dict() for x in permissions]
        resp = self.http.edit_application_command_permissions(int(application_id or self.application_id), int(guild), int(command), permissions)
        if isinstance(resp, dict):
            return GuildApplicationCommandPermissions(resp)
        return wrap_to_async(GuildApplicationCommandPermissions, None, resp, as_create=False)

    def batch_edit_application_command_permissions(self,
                                                   guild: Guild.TYPING,
                                                   permissions_dict: typing.Dict[ApplicationCommand.TYPING, typing.List[typing.Union[dict, ApplicationCommandPermissions]]],
                                                   *, application_id: Snowflake.TYPING = None) -> GuildApplicationCommandPermissions.RESPONSE:
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        permissions_dicts = [{"id": str(int(k)), "permissions": [x if isinstance(x, dict) else x.to_dict() for x in v]} for k, v in permissions_dict.items()]
        resp = self.http.batch_edit_application_command_permissions(int(application_id or self.application_id), int(guild), permissions_dicts)
        if isinstance(resp, list):
            return [GuildApplicationCommandPermissions(x) for x in resp]
        return wrap_to_async(GuildApplicationCommandPermissions, None, resp, as_create=False)

    # Misc

    def get_allowed_mentions(self, allowed_mentions):
        _all_men = allowed_mentions or self.default_allowed_mentions
        if _all_men and not isinstance(_all_men, dict):
            _all_men = _all_men.to_dict()
        return _all_men

    @property
    def get(self):
        raise NotImplementedError

    @property
    def has_cache(self) -> bool:
        return hasattr(self, "cache")
