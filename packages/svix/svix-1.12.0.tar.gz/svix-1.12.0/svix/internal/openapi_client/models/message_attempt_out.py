import datetime
from typing import Any, Dict, List, Type, TypeVar

import attr
from dateutil.parser import isoparse

from ..models.message_attempt_trigger_type import MessageAttemptTriggerType
from ..models.message_status import MessageStatus

T = TypeVar("T", bound="MessageAttemptOut")


@attr.s(auto_attribs=True)
class MessageAttemptOut:
    """
    Attributes:
        endpoint_id (str): The ep's ID Example: ep_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        id (str): The attempt's ID Example: atmpt_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        msg_id (str): The msg's ID Example: msg_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        response (str):  Example: {}.
        response_status_code (int):  Example: 200.
        status (MessageStatus): The sending status of the message:
            - Success = 0
            - Pending = 1
            - Fail = 2
            - Sending = 3
        timestamp (datetime.datetime):
        trigger_type (MessageAttemptTriggerType): The reason an attempt was made:
            - Scheduled = 0
            - Manual = 1
        url (str):  Example: https://example.com/webhook/.
    """

    endpoint_id: str
    id: str
    msg_id: str
    response: str
    response_status_code: int
    status: MessageStatus
    timestamp: datetime.datetime
    trigger_type: MessageAttemptTriggerType
    url: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        endpoint_id = self.endpoint_id
        id = self.id
        msg_id = self.msg_id
        response = self.response
        response_status_code = self.response_status_code
        status = self.status.value

        timestamp = self.timestamp.isoformat()

        trigger_type = self.trigger_type.value

        url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "endpointId": endpoint_id,
                "id": id,
                "msgId": msg_id,
                "response": response,
                "responseStatusCode": response_status_code,
                "status": status,
                "timestamp": timestamp,
                "triggerType": trigger_type,
                "url": url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        endpoint_id = d.pop("endpointId")

        id = d.pop("id")

        msg_id = d.pop("msgId")

        response = d.pop("response")

        response_status_code = d.pop("responseStatusCode")

        status = MessageStatus(d.pop("status"))

        timestamp = isoparse(d.pop("timestamp"))

        trigger_type = MessageAttemptTriggerType(d.pop("triggerType"))

        url = d.pop("url")

        message_attempt_out = cls(
            endpoint_id=endpoint_id,
            id=id,
            msg_id=msg_id,
            response=response,
            response_status_code=response_status_code,
            status=status,
            timestamp=timestamp,
            trigger_type=trigger_type,
            url=url,
        )

        message_attempt_out.additional_properties = d
        return message_attempt_out

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
