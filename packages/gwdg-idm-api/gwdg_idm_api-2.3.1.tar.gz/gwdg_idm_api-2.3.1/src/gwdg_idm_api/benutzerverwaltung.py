import datetime
import json
import typing
import urllib.parse

from .models import BaseGWDGUser, ChangeTemplate, CreateTemplate, IDMRequest
from .util import (
    AlreadyDeletedError,
    BadJsonError,
    IDMRequestError,
    UnexpectedJsonError,
)

if typing.TYPE_CHECKING:
    from requests import Response


class Benutzerverwaltung(IDMRequest):
    api_suffix: str = "/Benutzerverwaltung/objects"
    user_class: type[ChangeTemplate] = BaseGWDGUser

    def set_user_class(self, user_class: type[ChangeTemplate]):
        self.user_class = user_class

    def get_single_user(self, user_id: str) -> ChangeTemplate:
        request_url: str
        resp: "Response"
        json_resp: dict

        request_url = f"{self.api_url}{self.api_suffix}/{user_id}"
        resp = self.get_request(request_url)
        try:
            json_resp = json.loads(resp.text)
        except json.decoder.JSONDecodeError:
            raise BadJsonError(resp.text)
        return self.user_class.from_json(json_resp)

    def get_multiple_users(
        self, filter_string: str | None = None
    ) -> list[ChangeTemplate]:
        request_url: str
        resp: "Response"
        json_resp: dict

        request_url = f"{self.api_url}{self.api_suffix}"
        if filter_string is not None:
            request_url = f"{request_url}?filter={urllib.parse.quote(filter_string)}"
        resp = self.get_request(request_url)
        try:
            json_resp = json.loads(resp.text)
        except json.decoder.JSONDecodeError:
            raise BadJsonError(resp.text)
        try:
            return [self.user_class.from_json(obj) for obj in json_resp["Objects"]]
        except Exception:
            raise UnexpectedJsonError(resp.text)

    def update_user(
        self,
        user: ChangeTemplate,
        update_dict: dict[str, str | list[str] | None],
        *,
        single_call: bool = False,
    ) -> ChangeTemplate:
        request_url: str = f"{self.api_url}{self.api_suffix}/{user.id}"
        resp: "Response"
        data: str

        if "mail" in update_dict:
            # Run mail at the very last to avoid missing proxyMail entries
            mail = update_dict.pop("mail")
            update_dict["mail"] = mail

        if not single_call:
            for key, value in update_dict.items():
                data = user.update_json(key, value)

                resp = self.put_request(request_url, data)
                if "success" not in resp.text:
                    raise IDMRequestError(
                        f"Could not connect to IDM: Invalid combination\n{key=}\n{value=}\n{resp.text=}"
                    )
        else:
            data_list = []
            for key, value in update_dict.items():
                data_list.append(user.update_dict(key, value))
            base_data = data_list[0]
            for data_entry in data_list[1:]:
                base_data["attributes"].extend(data_entry["attributes"])
            resp = self.put_request(request_url, json.dumps(base_data))
            if "success" not in resp.text:
                raise IDMRequestError(
                    f"Could not connect to IDM: Invalid combination\n{data_list=}\n{resp.text=}"
                )
        return self.get_single_user(user.id)

    def create_user(self, new_user: CreateTemplate) -> ChangeTemplate:
        request_url: str = (
            f"{self.api_url}{self.api_suffix}/{new_user.create_template_name}"
        )
        resp: "Response"
        data: str

        data = new_user.to_json()
        resp = self.post_request(request_url, data)
        if "success" not in resp.text:
            raise IDMRequestError(
                f"Could not connect to IDM: Invalid combination\n{resp.text=}"
            )
        user_id = resp.headers["location"]
        return self.get_single_user(user_id)

    def delete_user(
        self, user: ChangeTemplate, expire_datetime: datetime.datetime | datetime.date
    ):
        today: datetime.date
        expire_date: datetime.date
        activate_now: bool
        change_data: dict[str, str]

        today = datetime.datetime.now().date()
        try:
            expire_date = expire_datetime.date()
        except AttributeError:
            expire_date = expire_datetime

        current_user_status = self.get_single_user(user.id)

        activate_now = (expire_date - today).total_seconds() <= 0
        status_deleted = current_user_status.goesternUserStatus in ("2", "255")

        change_data = {}
        change_data["isScheduledForDeletion"] = "FALSE"
        change_data["goesternExpirationDate"] = ""

        self.update_user(user, change_data, single_call=True)  # type: ignore

        if activate_now and not status_deleted:
            change_data = {
                "isScheduledForDeletion": "TRUE",
            }
        elif activate_now:
            change_data = {}
        else:
            change_data = {
                "goesternExpirationDate": expire_date.strftime("%d.%m.%Y"),
            }

        return self.update_user(user, change_data)  # type: ignore

    def reactivate_user(self, user: ChangeTemplate, create_mailbox: bool = True):
        current_user_status = self.get_single_user(user.id)

        if current_user_status.goesternUserStatus == "255":
            raise AlreadyDeletedError
        elif current_user_status.goesternUserStatus != "2":
            return user

        if current_user_status.goesternExpirationDate:
            change_data = {"goesternExpirationDate": ""}
            user = self.update_user(user, change_data)  # type: ignore

        change_data = {
            "goesternUserStatus": "0",
        }
        if create_mailbox:
            change_data["externalTaskCommand"] = "CreateMailbox"
        return self.update_user(user, change_data)  # type: ignore
