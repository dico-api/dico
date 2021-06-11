import io
import typing
import pathlib
import datetime
from .base.http import HTTPRequestBase
from .model import Channel, Message, MessageReference, AllowedMentions, Snowflake, Embed, Attachment, Overwrite, \
    Emoji, User, Interaction, InteractionResponse, Webhook, Guild, ApplicationCommand, Invite, Application, FollowedChannel, \
    ThreadMember, ListThreadsResponse, Component, Role
from .utils import from_emoji, wrap_to_async


class APIClient:
    """
    REST API handling client.

    .. note::
        If you chose to use async request handler, all request functions will return coroutine which will return raw instance.

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
                 token,
                 *,
                 base: typing.Type[HTTPRequestBase],
                 default_allowed_mentions: AllowedMentions = None,
                 application_id: typing.Union[int, str, Snowflake] = None,
                 **http_options):
        self.http = base.create(token, **http_options)
        self.default_allowed_mentions = default_allowed_mentions
        self.application_id = Snowflake.ensure_snowflake(application_id)

    # Channel

    def request_channel(self, channel: typing.Union[int, str, Snowflake, Channel]):
        channel = self.http.request_channel(int(channel))
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def modify_guild_channel(self,
                             channel: typing.Union[int, str, Snowflake, Channel],
                             *,
                             name: str = None,
                             channel_type: int = None,
                             position: int = None,
                             topic: str = None,
                             nsfw: bool = None,
                             rate_limit_per_user: int = None,
                             bitrate: int = None,
                             user_limit: int = None,
                             permission_overwrites: typing.List[Overwrite] = None,
                             parent: typing.Union[int, str, Snowflake, Channel] = None,
                             rtc_region: str = None,
                             video_quality_mode: int = None):
        if permission_overwrites:
            permission_overwrites = [x.to_dict() for x in permission_overwrites]
        if parent:
            parent = int(parent)
        channel = self.http.modify_guild_channel(int(channel), name, channel_type, position, topic, nsfw, rate_limit_per_user,
                                                 bitrate, user_limit, permission_overwrites, parent, rtc_region, video_quality_mode)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def modify_group_dm_channel(self, channel: typing.Union[int, str, Snowflake, Channel], *, name: str = None, icon: bin = None):
        channel = self.http.modify_group_dm_channel(int(channel), name, icon)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def modify_thread_channel(self,
                              channel: typing.Union[int, str, Snowflake, Channel], *,
                              name: str = None,
                              archived: bool = None,
                              auto_archive_duration: int = None,
                              locked: bool = None,
                              rate_limit_per_user: int = None):
        channel = self.http.modify_thread_channel(int(channel), name, archived, auto_archive_duration, locked, rate_limit_per_user)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def delete_channel(self, channel: typing.Union[int, str, Snowflake, Channel]):
        return self.http.delete_channel(int(channel))

    def request_channel_messages(self,
                                 channel: typing.Union[int, str, Snowflake, Channel], *,
                                 around: typing.Union[int, str, Snowflake, Message] = None,
                                 before: typing.Union[int, str, Snowflake, Message] = None,
                                 after: typing.Union[int, str, Snowflake, Message] = None,
                                 limit: int = 50):
        messages = self.http.request_channel_messages(int(channel), around and str(int(around)), before and str(int(before)), after and str(int(after)), limit)
        # This looks unnecessary, but this is to ensure they are all numbers.
        if isinstance(messages, list):
            messages = [Message.create(self, x) for x in messages]
        return wrap_to_async(Message, self, messages)

    def request_channel_message(self, channel: typing.Union[int, str, Snowflake, Channel], message: typing.Union[int, str, Snowflake, Message]):
        message = self.http.request_channel_message(int(channel), int(message))
        if isinstance(message, dict):
            message = Message.create(self, channel)
        return wrap_to_async(Message, self, message)

    def create_message(self,
                       channel: typing.Union[int, str, Snowflake, Channel],
                       content: str = None,
                       *,
                       embed: typing.Union[Embed, dict] = None,
                       file: typing.Union[io.FileIO, pathlib.Path, str] = None,
                       files: typing.List[typing.Union[io.FileIO, pathlib.Path, str]] = None,
                       tts: bool = False,
                       allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                       message_reference: typing.Union[Message, MessageReference, dict] = None,
                       component: typing.Union[dict, Component] = None,
                       components: typing.List[typing.Union[dict, Component]] = None) -> typing.Union[Message, typing.Coroutine[dict, Message, dict]]:
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
        :param file: File of the message.
        :param files: Files of the message.
        :param tts: Whether to speak message.
        :param allowed_mentions: :class:`.model.channel.AllowedMentions` to use for this request.
        :param message_reference: Message to reply.
        :param components: Component of the message.
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
        if embed and not isinstance(embed, dict):
            embed = embed.to_dict()
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
                  "embed": embed,
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
                          channel: typing.Union[int, str, Snowflake, Channel],
                          message: typing.Union[int, str, Snowflake, Message]):
        msg = self.http.crosspost_message(int(channel), int(message))
        if isinstance(msg, dict):
            return Message.create(self, msg)
        return wrap_to_async(Message, self, msg)

    def create_reaction(self,
                        channel: typing.Union[int, str, Snowflake, Channel],
                        message: typing.Union[int, str, Snowflake, Message],
                        emoji: typing.Union[str, Emoji]):
        return self.http.create_reaction(int(channel), int(message), from_emoji(emoji))

    def delete_reaction(self,
                        channel: typing.Union[int, str, Snowflake, Channel],
                        message: typing.Union[int, str, Snowflake, Message],
                        emoji: typing.Union[str, Emoji],
                        user: typing.Union[int, str, Snowflake, User] = "@me"):
        return self.http.delete_reaction(int(channel), int(message), from_emoji(emoji), int(user) if user != "@me" else user)

    def request_reactions(self,
                          channel: typing.Union[int, str, Snowflake, Channel],
                          message: typing.Union[int, str, Snowflake, Message],
                          emoji: typing.Union[str, Emoji],
                          after: typing.Union[int, str, Snowflake, User] = None,
                          limit: int = None):
        users = self.http.request_reactions(int(channel), int(message), from_emoji(emoji), int(after), limit)
        if isinstance(users, list):
            return [User.create(self, x) for x in users]
        return wrap_to_async(User, self, users)

    def delete_all_reactions(self, channel: typing.Union[int, str, Snowflake, Channel], message: typing.Union[int, str, Snowflake, Message]):
        return self.http.delete_all_reactions(int(channel), int(message))

    def delete_all_reactions_emoji(self,
                                   channel: typing.Union[int, str, Snowflake, Channel],
                                   message: typing.Union[int, str, Snowflake, Message],
                                   emoji: typing.Union[str, Emoji]):
        return self.http.delete_all_reactions_emoji(int(channel), int(message), from_emoji(emoji))

    def edit_message(self,
                     channel: typing.Union[int, str, Snowflake, Channel],
                     message: typing.Union[int, str, Snowflake, Message],
                     *,
                     content: str = None,
                     embed: typing.Union[Embed, dict] = None,
                     file: typing.Union[io.FileIO, pathlib.Path, str] = None,
                     files: typing.List[typing.Union[io.FileIO, pathlib.Path, str]] = None,
                     allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                     attachments: typing.List[typing.Union[Attachment, dict]] = None,
                     component: typing.Union[dict, Component] = None,
                     components: typing.List[typing.Union[dict, Component]] = None) -> typing.Union[Message, typing.Coroutine[dict, Message, dict]]:
        if files and file:
            raise TypeError("you can't pass both file and files.")
        if file:
            files = [file]
        if files:
            for x in range(len(files)):
                sel = files[x]
                if not isinstance(sel, io.FileIO):
                    files[x] = open(sel, "rb")
        if embed and not isinstance(embed, dict):
            embed = embed.to_dict()
        _att = []
        if attachments:
            for x in attachments:
                if not isinstance(x, dict):
                    x = x.to_dict()
                _att.append(x)
        if component and components:
            raise TypeError("you can't pass both component and components.")
        if component:
            components = [component]
        if components:
            components = [*map(lambda n: n if isinstance(n, dict) else n.to_dict(), components)]
        params = {"channel_id": int(channel),
                  "message_id": int(message),
                  "content": content,
                  "embed": embed,
                  "flags": None,
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
                       channel: typing.Union[int, str, Snowflake, Channel],
                       message: typing.Union[int, str, Snowflake, Message]):
        return self.http.delete_message(int(channel), int(message))

    def bulk_delete_messages(self, channel: typing.Union[int, str, Snowflake, Channel], messages: typing.List[typing.Union[int, str, Snowflake, Message]]):
        return self.http.bulk_delete_messages(int(channel), list(map(int, messages)))

    def edit_channel_permissions(self, channel: typing.Union[int, str, Snowflake, Channel], overwrite: Overwrite):
        ow_dict = overwrite.to_dict()
        return self.http.edit_channel_permissions(int(channel), ow_dict["id"], ow_dict["allow"], ow_dict["deny"], ow_dict["type"])

    def request_channel_invites(self, channel: typing.Union[int, str, Snowflake, Channel]):
        invites = self.http.request_channel_invites(int(channel))
        if isinstance(invites, list):
            return [Invite(self, x) for x in invites]
        return wrap_to_async(Invite, self, invites, as_create=False)

    def create_channel_invite(self,
                              channel: typing.Union[int, str, Snowflake, Channel],
                              *,
                              max_age: int = None,
                              max_uses: int = None,
                              temporary: bool = None,
                              unique: bool = None,
                              target_type: int = None,
                              target_user: typing.Union[int, str, Snowflake, User] = None,
                              target_application: typing.Union[int, str, Snowflake, Application] = None):
        invite = self.http.create_channel_invite(int(channel), max_age, max_uses, temporary, unique, target_type,
                                                 int(target_user) if target_user is not None else target_user,
                                                 int(target_application) if target_application is not None else target_application)
        if isinstance(invite, dict):
            return Invite(self, invite)
        return wrap_to_async(Invite, self, invite, as_create=False)

    def delete_channel_permission(self, channel: typing.Union[int, str, Snowflake, Channel], overwrite: Overwrite):
        return self.http.delete_channel_permission(int(channel), int(overwrite.id))

    def follow_news_channel(self, channel: typing.Union[int, str, Snowflake, Channel], target_channel: typing.Union[int, str, Snowflake, Channel]):
        fc = self.http.follow_news_channel(int(channel), str(target_channel))
        if isinstance(fc, dict):
            return FollowedChannel(self, fc)
        return wrap_to_async(FollowedChannel, self, fc, as_create=False)

    def trigger_typing_indicator(self, channel: typing.Union[int, str, Snowflake, Channel]):
        return self.http.trigger_typing_indicator(int(channel))

    def request_pinned_messages(self, channel: typing.Union[int, str, Snowflake, Channel]):
        msgs = self.http.request_pinned_messages(int(channel))
        if isinstance(msgs, list):
            return [Message.create(self, x) for x in msgs]
        return wrap_to_async(Message, self, msgs)

    def pin_message(self, channel: typing.Union[int, str, Snowflake, Channel], message: typing.Union[int, str, Snowflake, Message]):
        return self.http.pin_message(int(channel), int(message))

    def unpin_message(self, channel: typing.Union[int, str, Snowflake, Channel], message: typing.Union[int, str, Snowflake, Message]):
        return self.http.unpin_message(int(channel), int(message))

    def group_dm_add_recipient(self,
                               channel: typing.Union[int, str, Snowflake, Channel],
                               user: typing.Union[int, str, Snowflake, User],
                               access_token: str,
                               nick: str):
        return self.http.group_dm_add_recipient(int(channel), int(user), access_token, nick)

    def group_dm_remove_recipient(self,
                                  channel: typing.Union[int, str, Snowflake, Channel],
                                  user: typing.Union[int, str, Snowflake, User]):
        return self.http.group_dm_remove_recipient(int(channel), int(user))

    def start_thread(self,
                     channel: typing.Union[int, str, Snowflake, Channel],
                     message: typing.Union[int, str, Snowflake, Message] = None,
                     *,
                     name: str,
                     auto_archive_duration: int):
        channel = self.http.start_thread_with_message(int(channel), int(message), name, auto_archive_duration) if message else \
            self.http.start_thread_without_message(int(channel), name, auto_archive_duration)
        if isinstance(channel, dict):
            channel = Channel.create(self, channel)
        return wrap_to_async(Channel, self, channel)

    def join_thread(self, channel: typing.Union[int, str, Snowflake, Channel]):
        return self.http.join_thread(int(channel))

    def add_thread_member(self, channel: typing.Union[int, str, Snowflake, Channel], user: typing.Union[int, str, Snowflake, User]):
        return self.http.add_thread_member(int(channel), int(user))

    def leave_thread(self, channel: typing.Union[int, str, Snowflake, Channel]):
        return self.http.leave_thread(int(channel))

    def remove_thread_member(self, channel: typing.Union[int, str, Snowflake, Channel], user: typing.Union[int, str, Snowflake, User]):
        return self.http.remove_thread_member(int(channel), int(user))

    def list_thread_members(self, channel: typing.Union[int, str, Snowflake, Channel]):
        members = self.http.list_thread_members(int(channel))
        if isinstance(members, list):
            return [ThreadMember(self, x) for x in members]
        return wrap_to_async(ThreadMember, self, members, as_create=False)

    def list_active_threads(self, channel: typing.Union[int, str, Snowflake, Channel]):
        resp = self.http.list_active_threads(int(channel))
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def list_public_archived_threads(self,
                                     channel: typing.Union[int, str, Snowflake, Channel],
                                     *,
                                     before: typing.Union[str, datetime.datetime] = None,
                                     limit: int = None):
        resp = self.http.list_public_archived_threads(int(channel), before, limit)
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def list_private_archived_threads(self,
                                      channel: typing.Union[int, str, Snowflake, Channel],
                                      *,
                                      before: typing.Union[str, datetime.datetime] = None,
                                      limit: int = None):
        resp = self.http.list_private_archived_threads(int(channel), before, limit)
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    def list_joined_private_archived_threads(self,
                                             channel: typing.Union[int, str, Snowflake, Channel],
                                             *,
                                             before: typing.Union[str, datetime.datetime] = None,
                                             limit: int = None):
        resp = self.http.list_joined_private_archived_threads(int(channel), before, limit)
        if isinstance(resp, dict):
            return ListThreadsResponse(self, resp)
        return wrap_to_async(ListThreadsResponse, self, resp, as_create=False)

    # Emoji

    def request_guild_emoji(self, guild: typing.Union[int, str, Snowflake, Guild], emoji: typing.Union[int, str, Snowflake, Emoji]):
        resp = self.http.request_guild_emoji(int(guild), int(emoji))
        if isinstance(resp, dict):
            return Emoji(self, resp)
        return wrap_to_async(Emoji, self, resp, as_create=False)

    def create_guild_emoji(self, guild: typing.Union[int, str, Snowflake, Guild], name: str, image: str, roles: typing.List[typing.Union[str, int, Snowflake, Role]] = None):
        resp = self.http.create_guild_emoji(int(guild), name, image, [int(x) for x in roles or []])
        if isinstance(resp, dict):
            return Emoji(self, resp)
        return wrap_to_async(Emoji, self, resp, as_create=False)

    def modify_guild_emoji(self,
                           guild: typing.Union[int, str, Snowflake, Guild],
                           emoji: typing.Union[int, str, Snowflake, Emoji],
                           name: str,
                           roles: typing.List[typing.Union[str, int, Snowflake, Role]]):
        resp = self.http.modify_guild_emoji(int(guild), int(emoji), name, [str(int(x)) for x in roles])
        if isinstance(resp, dict):
            return Emoji(self, resp)
        return wrap_to_async(Emoji, self, resp, as_create=False)

    # Webhook

    def create_webhook(self, channel: typing.Union[int, str, Snowflake, Channel], *, name: str = None, avatar: str = None):
        hook = self.http.create_webhook(int(channel), name, avatar)
        if isinstance(hook, dict):
            return Webhook(self, hook)
        return wrap_to_async(Webhook, self, hook, as_create=False)

    def request_channel_webhooks(self, channel: typing.Union[int, str, Snowflake, Channel]):
        hooks = self.http.request_channel_webhooks(int(channel))
        if isinstance(hooks, list):
            return [Webhook(self, x) for x in hooks]
        return wrap_to_async(Webhook, self, hooks, as_create=False)

    def request_guild_webhooks(self, guild: typing.Union[int, str, Snowflake, Guild]):
        hooks = self.http.request_guild_webhooks(int(guild))
        if isinstance(hooks, list):
            return [Webhook(self, x) for x in hooks]
        return wrap_to_async(Webhook, self, hooks, as_create=False)

    def request_webhook(self, webhook: typing.Union[int, str, Snowflake, Webhook], webhook_token: str = None):  # Requesting webhook using webhook, seems legit.
        hook = self.http.request_webhook(int(webhook)) if not webhook_token else self.http.request_webhook_with_token(int(webhook), webhook_token)
        if isinstance(hook, dict):
            return Webhook(self, hook)
        return wrap_to_async(Webhook, self, hook, as_create=False)

    def modify_webhook(self,
                       webhook: typing.Union[int, str, Snowflake, Webhook],
                       *,
                       webhook_token: str = None,
                       name: str = None,
                       avatar: str = None,
                       channel: typing.Union[int, str, Snowflake, Channel] = None):
        hook = self.http.modify_webhook(int(webhook), name, avatar, str(int(channel)) if channel is not None else channel) if not webhook_token \
            else self.http.modify_webhook_with_token(int(webhook), webhook_token, name, avatar)
        if isinstance(hook, dict):
            return Webhook(self, hook)
        return wrap_to_async(Webhook, self, hook, as_create=False)

    def delete_webhook(self, webhook: typing.Union[int, str, Snowflake, Webhook], webhook_token: str = None):
        return self.http.delete_webhook(int(webhook)) if not webhook_token else self.http.delete_webhook_with_token(int(webhook), webhook_token)

    def execute_webhook(self,
                        webhook: typing.Union[int, str, Snowflake, Webhook],
                        *,
                        webhook_token: str = None,
                        wait: bool = None,
                        thread: typing.Union[int, str, Snowflake, Channel] = None,
                        content: str = None,
                        username: str = None,
                        avatar_url: str = None,
                        tts: bool = False,
                        file: typing.Union[io.FileIO, pathlib.Path, str] = None,
                        files: typing.List[typing.Union[io.FileIO, pathlib.Path, str]] = None,
                        embed: typing.Union[Embed, dict] = None,
                        embeds: typing.List[typing.Union[Embed, dict]] = None,
                        allowed_mentions: typing.Union[AllowedMentions, dict] = None):
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
            embeds = [x.to_dict() for x in embeds if not isinstance(x, dict)]
        params = {"webhook_id": int(webhook),
                  "webhook_token": webhook_token if not isinstance(webhook, Webhook) else webhook.token,
                  "wait": wait,
                  "thread_id": str(int(thread)) if thread else thread,
                  "content": content,
                  "username": username,
                  "avatar_url": avatar_url,
                  "tts": tts,
                  "embeds": embeds,
                  "allowed_mentions": self.get_allowed_mentions(allowed_mentions)}
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
                                webhook: typing.Union[int, str, Snowflake, Webhook],
                                message: typing.Union[int, str, Snowflake, Message],
                                *,
                                webhook_token: str = None):
        if not isinstance(webhook, Webhook) and not webhook_token:
            raise TypeError("you must pass webhook_token if webhook is not dico.Webhook object.")
        msg = self.http.request_webhook_message(int(webhook), webhook_token or webhook.token, int(message))
        if isinstance(msg, dict):
            return Message.create(self, msg, webhook_token=webhook_token or webhook.token)
        return wrap_to_async(Message, self, msg, webhook_token=webhook_token or webhook.token)

    def edit_webhook_message(self,
                             webhook: typing.Union[int, str, Snowflake, Webhook],
                             message: typing.Union[int, str, Snowflake, Message],
                             *,
                             webhook_token: str = None,
                             content: str = None,
                             embed: typing.Union[Embed, dict] = None,
                             embeds: typing.List[typing.Union[Embed, dict]] = None,
                             file: typing.Union[io.FileIO, pathlib.Path, str] = None,
                             files: typing.List[typing.Union[io.FileIO, pathlib.Path, str]] = None,
                             allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                             attachments: typing.List[typing.Union[Attachment, dict]] = None):
        if not isinstance(webhook, Webhook) and not webhook_token:
            raise TypeError("you must pass webhook_token if webhook is not dico.Webhook object.")
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
            embeds = [x.to_dict() for x in embeds if not isinstance(x, dict)]
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
                  "attachments": _att}
        try:
            msg = self.http.edit_webhook_message(**params)
            if isinstance(msg, dict):
                return Message.create(self, msg, webhook_token=webhook_token or webhook.token)
            return wrap_to_async(Message, self, msg, webhook_token=webhook_token or webhook.token)
        finally:
            if files:
                [x.close() for x in files if not x.closed]

    def delete_webhook_message(self,
                               webhook: typing.Union[int, str, Snowflake, Webhook],
                               message: typing.Union[int, str, Snowflake, Message],
                               *,
                               webhook_token: str = None):
        if not isinstance(webhook, Webhook) and not webhook_token:
            raise TypeError("you must pass webhook_token if webhook is not dico.Webhook object.")
        return self.http.delete_webhook_message(int(webhook), webhook_token or webhook.token, int(message))

    # Interaction

    def request_application_commands(self,
                                     guild: typing.Union[int, str, Snowflake, Guild] = None,
                                     *,
                                     application_id: typing.Union[int, str, Snowflake] = None):
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        app_commands = self.http.request_application_commands(int(application_id or self.application_id), int(guild) if guild else guild)
        if isinstance(app_commands, list):
            return [ApplicationCommand(x) for x in app_commands]
        return wrap_to_async(ApplicationCommand, None, app_commands, as_create=False)

    def create_interaction_response(self,
                                    interaction: typing.Union[int, str, Snowflake, Interaction],
                                    interaction_response: InteractionResponse,
                                    *,
                                    interaction_token: str = None):
        if not isinstance(interaction, Interaction) and not interaction_token:
            raise TypeError("you must pass interaction_token if interaction is not dico.Interaction object.")
        return self.http.create_interaction_response(int(interaction), interaction_token or interaction.token, interaction_response.to_dict())

    def request_original_interaction_response(self,
                                              interaction: typing.Union[int, str, Snowflake, Interaction] = None,
                                              *,
                                              interaction_token: str = None,
                                              application_id: typing.Union[int, str, Snowflake] = None):
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        if not isinstance(interaction, Interaction) and not interaction_token:
            raise TypeError("you must pass interaction_token if interaction is not dico.Interaction object.")
        msg = self.http.request_original_interaction_response(application_id or self.application_id, interaction_token or interaction.token)
        if isinstance(msg, dict):
            return Message.create(self, msg, interaction_token=interaction_token or interaction.token, original_response=True)
        return wrap_to_async(Message, self, msg, interaction_token=interaction_token or interaction.token, original_response=True)

    def create_followup_message(self,
                                interaction: typing.Union[int, str, Snowflake, Interaction] = None,
                                *,
                                interaction_token: str = None,
                                application_id: typing.Union[int, str, Snowflake] = None,
                                content: str = None,
                                username: str = None,
                                avatar_url: str = None,
                                tts: bool = False,
                                file: typing.Union[io.FileIO, pathlib.Path, str] = None,
                                files: typing.List[typing.Union[io.FileIO, pathlib.Path, str]] = None,
                                embed: typing.Union[Embed, dict] = None,
                                embeds: typing.List[typing.Union[Embed, dict]] = None,
                                allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                                ephemeral: bool = False):
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
            embeds = [x.to_dict() for x in embeds if not isinstance(x, dict)]
        params = {"application_id": application_id or self.application_id,
                  "interaction_token": interaction_token or interaction.token,
                  "content": content,
                  "username": username,
                  "avatar_url": avatar_url,
                  "tts": tts,
                  "embeds": embeds,
                  "allowed_mentions": self.get_allowed_mentions(allowed_mentions)}
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
                                  interaction: typing.Union[int, str, Snowflake, Interaction] = None,
                                  message: typing.Union[int, str, Snowflake, Message] = "@original",
                                  *,
                                  interaction_token: str = None,
                                  application_id: typing.Union[int, str, Snowflake] = None,
                                  content: str = None,
                                  file: typing.Union[io.FileIO, pathlib.Path, str] = None,
                                  files: typing.List[typing.Union[io.FileIO, pathlib.Path, str]] = None,
                                  embed: typing.Union[Embed, dict] = None,
                                  embeds: typing.List[typing.Union[Embed, dict]] = None,
                                  allowed_mentions: typing.Union[AllowedMentions, dict] = None,
                                  attachments: typing.List[typing.Union[Attachment, dict]] = None):
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
            embeds = [x.to_dict() for x in embeds if not isinstance(x, dict)]
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
                  "attachments": _att}
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
                                    interaction: typing.Union[int, str, Snowflake, Interaction] = None,
                                    message: typing.Union[int, str, Snowflake, Message] = "@original",
                                    *,
                                    interaction_token: str = None,
                                    application_id: typing.Union[int, str, Snowflake] = None):
        if not application_id and not self.application_id:
            raise TypeError("you must pass application_id if it is not set in client instance.")
        if not isinstance(interaction, Interaction) and not interaction_token:
            raise TypeError("you must pass interaction_token if interaction is not dico.Interaction object.")
        return self.http.delete_interaction_response(application_id or self.application_id, interaction_token or interaction.token, int(message) if message != "@original" else message)

    # Misc

    def get_allowed_mentions(self, allowed_mentions):
        _all_men = allowed_mentions or self.default_allowed_mentions
        if _all_men and not isinstance(_all_men, dict):
            _all_men = _all_men.to_dict()
        return _all_men

    @property
    def has_cache(self):
        return hasattr(self, "cache")
