class ApplicationCommand:
    def __init__(self, resp: dict, command_creation: bool = False):
        self.id = resp["id"]
        self.application_id = resp["application_id"]
        self.name = resp["name"]
        self.description = resp["description"]
        self.options = [ApplicationCommandOption(x) for x in resp.get("options", [])]
        self.default_permission = resp.get("default_permission", True)
        self.__command_creation = command_creation

    def to_dict(self):
        if self.__command_creation:
            return {"name": self.name, "description": self.description, "options": [x.to_dict() for x in self.options], "default_permission": self.default_permission}
        return {"id": self.id, "application_id": self.application_id, "name": self.name,
                "description": self.description, "options": self.options, "default_permission": self.default_permission}

    @classmethod
    def create(cls, name, description, options, default_permission):
        return cls({"name": name, "description": description, "options": options, "default_permission": default_permission}, command_creation=True)


class ApplicationCommandOption:
    def __init__(self, resp: dict):
        self.type = resp["type"]
        self.application_id = resp["application_id"]
        self.name = resp["name"]
        self.description = resp["description"]
        self.required = resp.get("required", False)
        self.choices = [ApplicationCommandOptionChoice(x) for x in resp.get("choices", [])]
        self.options = [ApplicationCommandOption(x) for x in resp.get("options", [])]

    def to_dict(self):
        ret = {"type": self.type, "application_id": self.application_id, "name": self.name, "description": self.description,
               "required": self.required, "choices": [x.to_dict() for x in self.choices], "options": [x.to_dict() for x in self.options]}
        if not ret["options"]:
            del ret["options"]
        else:
            del ret["choices"]
        return ret


class ApplicationCommandOptionType:
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


class ApplicationCommandOptionChoice:
    def __init__(self, resp: dict):
        self.name = resp["name"]
        self.value = resp["value"]

    def to_dict(self):
        return {"name": self.name, "value": self.value}

    @classmethod
    def create(cls, name, value):
        return cls({"name": name, "value": value})


class GuildApplicationCommandPermissions:
    pass


class ApplicationCommandPermissionType:
    pass


class Interaction:
    pass


class InteractionType:
    pass


class ApplicationCommandInteractionData:
    pass


class ApplicationCommandInteractionDataResolved:
    pass


class ApplicationCommandInteractionDataOption:
    pass


class InteractionResponseType:
    pass


class InteractionApplicationCommandCallbackData:
    pass


class MessageInteraction:
    pass
