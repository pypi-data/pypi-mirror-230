from enum import Enum


class BackgroundTaskType(str, Enum):
    APPLICATION_STATS = "application.stats"
    ENDPOINT_RECOVER = "endpoint.recover"
    ENDPOINT_REPLAY = "endpoint.replay"
    MESSAGE_BROADCAST = "message.broadcast"

    def __str__(self) -> str:
        return str(self.value)
