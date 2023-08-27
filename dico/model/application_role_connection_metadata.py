import typing

from ..base.model import TypeBase


class ApplicationRoleConnectionMetadata:
    RESPONSE_AS_LIST = typing.Union[
        typing.List["ApplicationRoleConnectionMetadata"],
        typing.Awaitable[typing.List["ApplicationRoleConnectionMetadata"]],
    ]

    def __init__(self, resp: dict):
        self.type: "ApplicationRoleConnectionMetadataType" = (
            ApplicationRoleConnectionMetadataType(resp["type"])
        )
        self.key: str = resp["key"]
        self.name: str = resp["name"]
        self.name_localizations: typing.Optional[typing.Dict[str, str]] = resp.get(
            "name_localizations"
        )
        self.description: str = resp["description"]
        self.description_localizations: typing.Optional[
            typing.Dict[str, str]
        ] = resp.get("description_localizations")


class ApplicationRoleConnectionMetadataType(TypeBase):
    INTEGER_LESS_THAN_OR_EQUAL = 1
    INTEGER_GREATER_THAN_OR_EQUAL = 2
    INTEGER_EQUAL = 3
    INTEGER_NOT_EQUAL = 4
    DATETIME_LESS_THAN_OR_EQUAL = 5
    DATETIME_GREATER_THAN_OR_EQUAL = 6
    BOOLEAN_EQUAL = 7
    BOOLEAN_NOT_EQUAL = 8
