import inspect
from .model.event import *


class EventHandler:
    def __init__(self, client):
        self.events = {}
        self.client = client

    def add(self, event, func):
        if event not in self.events:
            self.events[event] = []

        async def ensure_coro(*args, **kwargs):
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        self.events[event].append(ensure_coro)

    def get(self, event) -> list:
        return self.events.get(event, [])

    def dispatch_from_raw(self, name, resp):
        model_dict = {
            "READY": Ready,
            "CHANNEL_CREATE": ChannelCreate,
            "CHANNEL_UPDATE": ChannelUpdate,
            "CHANNEL_DELETE": ChannelDelete,
            "CHANNEL_PINS_UPDATE": ChannelPinsUpdate,
            "GUILD_CREATE": GuildCreate,
            "GUILD_UPDATE": GuildUpdate,
            "GUILD_DELETE": GuildDelete,
            "GUILD_BAN_ADD": GuildBanAdd,
            "GUILD_BAN_REMOVE": GuildBanRemove,
            "GUILD_EMOJIS_UPDATE": GuildEmojisUpdate,
            "GUILD_INTEGRATIONS_UPDATE": GuildIntegrationsUpdate,
            "GUILD_MEMBER_ADD": GuildMemberAdd,
            "GUILD_MEMBER_REMOVE": GuildBanRemove,
            "GUILD_MEMBER_UPDATE": GuildMemberUpdate,
            "GUILD_ROLE_CREATE": GuildRoleCreate,
            "GUILD_ROLE_UPDATE": GuildRoleUpdate,
            "GUILD_ROLE_DELETE": GuildRoleDelete,
            "INVITE_CREATE": InviteCreate,
            "INVITE_DELETE": InviteDelete,
            "MESSAGE_CREATE": MessageCreate,
            "MESSAGE_UPDATE": MessageUpdate,
            "MESSAGE_DELETE": MessageDelete,
            "MESSAGE_DELETE_BULK": MessageDeleteBulk,
            "MESSAGE_REACTION_ADD": MessageReactionAdd,
            "MESSAGE_REACTION_REMOVE": MessageReactionRemove,
            "MESSAGE_REACTION_REMOVE_ALL": MessageReactionRemoveAll,
            "MESSAGE_REACTION_REMOVE_EMOJI": MessageReactionRemoveEmoji
        }
        if name in model_dict:
            ret = model_dict[name].create(self.client, resp)
        else:
            ret = resp
        self.client.dispatch(name, ret)
