from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, cast

import attr

if TYPE_CHECKING:
    from ..models.message_attempt_headers_out_sent_headers import MessageAttemptHeadersOutSentHeaders


T = TypeVar("T", bound="MessageAttemptHeadersOut")


@attr.s(auto_attribs=True)
class MessageAttemptHeadersOut:
    """
    Attributes:
        sensitive (List[str]):
        sent_headers (MessageAttemptHeadersOutSentHeaders):
    """

    sensitive: List[str]
    sent_headers: "MessageAttemptHeadersOutSentHeaders"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        sensitive = self.sensitive

        sent_headers = self.sent_headers

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sensitive": sensitive,
                "sentHeaders": sent_headers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        sensitive = cast(List[str], d.pop("sensitive"))

        sent_headers = d.pop("sentHeaders")

        message_attempt_headers_out = cls(
            sensitive=sensitive,
            sent_headers=sent_headers,
        )

        message_attempt_headers_out.additional_properties = d
        return message_attempt_headers_out

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
