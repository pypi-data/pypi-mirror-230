import json
import logging
import os
import typing

import pydantic
import requests

from .util import IDMNotReachableError

if typing.TYPE_CHECKING:
    from requests import Response


__all__ = ["BaseGWDGUser"]


DATA_TYPE = str | list | dict | None


class IDMRequest(pydantic.BaseModel):
    username: str
    password: str
    api_url: str = os.environ.get("IDM_API_URL", "")

    def run_request(
        self, func: typing.Callable[..., "Response"], url: str, data: DATA_TYPE = None
    ) -> "Response":
        try:
            return func(
                url,
                auth=(self.username, self.password),
                timeout=240,  # Needs to be this high to allow for an all-objects query
                headers={
                    "Accept": "application/json",
                    "Accept-Language": "en",
                    "Content-Type": "application/json",
                },
                data=data,
            )
        except Exception as e:
            raise IDMNotReachableError(
                f"Could not connect to IDM: IDM not reachable!\n{e}"
            )

    def get_request(self, url: str) -> "Response":
        return self.run_request(requests.get, url)

    def put_request(self, url: str, data: DATA_TYPE) -> "Response":
        return self.run_request(requests.put, url, data)

    def post_request(self, url: str, data: DATA_TYPE) -> "Response":
        return self.run_request(requests.post, url, data)


class ChangeTemplate(pydantic.BaseModel):
    id: str
    goesternExpirationDate: str = None
    isScheduledForDeletion: str = None
    goesternUserStatus: str = None

    @pydantic.validator("isScheduledForDeletion")
    @classmethod
    def to_upper(cls, value):
        return value.upper()

    @staticmethod
    def update_dict(name: str, value: str | list[str] | None) -> dict:
        if value is not None:
            value = [value] if not isinstance(value, list) else value
        else:
            value = []
        data = {
            "name": name,
            "value": value,
        }
        return {"attributes": [data]}

    @staticmethod
    def update_json(name: str, value: str | list[str] | None) -> str:
        return json.dumps(ChangeTemplate.update_dict(name, value))

    @classmethod
    def from_json(cls, json: dict) -> "ChangeTemplate":
        response_dict: dict[str, list[str] | str]

        response_dict = {
            "id": [json["id"]],
            "dn": [json["dn"]],
        }
        response_dict.update(
            {entry["name"]: entry["value"] for entry in json["attributes"]}
        )

        remove_keys = []
        for key, value in response_dict.items():
            try:
                expected_type = type(cls.__fields__[key].outer_type_())
            except KeyError:
                remove_keys.append(key)
                logging.debug(
                    "\n"
                    "  key unknown to model\n"
                    f"  User: {response_dict['id']}\n"
                    f"  Key: {key}"
                    f"  Value: {value}"
                )
                continue
            if isinstance(value, expected_type):
                continue

            if isinstance(value, expected_type):
                continue
            elif expected_type is str and isinstance(value, list):
                if len(value) > 1:
                    logging.warning(
                        "\n"
                        "  str expected, but found list: Using first element\n"
                        "  Please check your class specifications.\n"
                        f"  User: {response_dict['id']}\n"
                        f"  Key: {key}"
                        f"  Value: {value}"
                    )
                try:
                    new_val: str = value[0]
                except IndexError:
                    logging.warning(
                        "  str expected, but empty list found: Set to empty string\n"
                        "  Please check your class specifications.\n"
                        f"  User: {response_dict['id']}\n"
                        f"  Key: {key}"
                        f"  Value: {value}"
                    )
                    new_val: str = ""
                response_dict[key] = new_val
            else:
                assert False, (
                    "  Only str and list types are supported so far!"
                    "  Please check your class specifications.\n"
                    f"  User: {response_dict['id']}\n"
                    f"  Key: {key}"
                    f"  Value: {value}"
                )

        return cls(**{key: value for key, value in response_dict.items() if key not in set(remove_keys)})  # type: ignore


class CreateTemplate(pydantic.BaseModel):
    create_template_name: str

    def to_dict(self) -> dict:
        data = [
            {
                "name": key.removeprefix("_"),
                "value": [value] if not isinstance(value, list) else value,
            }
            for key, value in self.dict().items()
            if key != "create_template_name"
        ]
        return {"attributes": data}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class BaseGWDGUser(ChangeTemplate):
    # Common fields
    ou: str = None
    employeeNumber: str = None
    mpgEmployeeNumber: str = None
    employeeType: str = None
    employeeStatus: str = None
    accountType: str = None
    uid: str = None
    oldUid: list[str] = None
    goesternSAMAccountName: str = None
    ou: str = None
    goesternUserType: str = None
    givenName: str = None
    sn: str = None
    goesternGWDGadDisplayName: str = None
    description: str = None
    departmentNumber: str = None
    title: str = None
    telephoneNumber: str = None
    mobile: str = None
    facsimileTelephoneNumber: str = None
    roomNumber: str = None
    street: str = None
    postalCode: str = None
    city: str = None
    st: str = None
    l: str = None
    goesternProxyAddresses: list[str] = None
    mail: str = None
    goesternExchangeQuota: str = None
    goesternMailboxServer: str = None
    goesternMailboxZugehoerigkeit: str = None
    exchangeTargetAddress: str = None
    goesternMailRoutingAddresses: list[str] = None
    goesternExchHideFromAddressLists: str = None
    externalEmailAddress: list[str] = None
    filterAttribute1: list[str] = None
    filterAttribute2: list[str] = None
    filterAttribute3: list[str] = None
    goesternDisableReason: str = None
    goesternDisableDate: str = None
    goesternRemoveDate: str = None
    goesternLockoutTime: str = None
    ownCloudQuota: str = None
    memberOfStaticExchangeDistGrp: list[str] = None
    isInitialPassword: str = None
    createTimestamp: str = None
    modifyTimeStamp: str = None
    pwdChangedTime: str = None
    passwordExpirationTime: str = None
    isInitialAdditionalPassword: str = None
    additionalPasswordModifyTime: str = None
    additionalPasswordExpirationTime: str = None
    eduPersonPrincipalName: str = None
    effectivePrivilege: list[str] = None
    responsiblePerson: list[str] = None
