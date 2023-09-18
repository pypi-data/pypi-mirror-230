from __future__ import annotations

import uuid
from datetime import datetime

import pendulum

from impaction_ai.api_client import APIClient
from impaction_ai.buffer_storage import BufferStorage
from impaction_ai.constants import (
    FLUSH_TIMEOUT_SECONDS,
    ROLE_ASSISTANT,
    ROLE_USER,
    SERVER_BASE_URL,
    EventTypes,
)
from impaction_ai.ingestion.v1alpha.event_pb2 import Event, EventProperties
from impaction_ai.logger import get_logger
from impaction_ai.utils import datetime_to_timestamp
from impaction_ai.worker import Worker


class ImpactionAI:
    def __init__(self, project_id: str, api_key: str, api_host: str = SERVER_BASE_URL):
        self.project_id = project_id
        self.logger = get_logger("INFO")
        api_client = APIClient(api_host=api_host, api_key=api_key)
        self.worker = Worker(api_client=api_client, logger=self.logger)
        self.buffer_storage = BufferStorage()
        self.worker.setup(self.buffer_storage)
        self.worker.start()

    def open_session(self, session_id: str, user_id: str, assistant_id: str | None = None) -> None:
        session_properties_args = {"session_id": session_id, "user_id": user_id}
        if assistant_id is not None:
            session_properties_args["assistant_id"] = assistant_id

        open_session_event = Event(
            id=uuid.uuid4().hex,
            type=EventTypes.SESSION_OPEN,
            create_time=datetime_to_timestamp(pendulum.now()),
            properties=EventProperties(session_properties=EventProperties.SessionProperties(**session_properties_args)),
            project_id=self.project_id,
        )
        self._collect(open_session_event)

    def close_session(self, session_id: str) -> None:
        close_session_event = Event(
            id=uuid.uuid4().hex,
            type=EventTypes.SESSION_CLOSE,
            create_time=datetime_to_timestamp(pendulum.now()),
            properties=EventProperties(session_properties=EventProperties.SessionProperties(session_id=session_id)),
            project_id=self.project_id,
        )
        self._collect(close_session_event)

    def identify_user(
        self,
        user_id: str,
        email: str | None = None,
        ip: str | None = None,
        country_code: str | None = None,
        create_time: datetime | None = None,
        display_name: str | None = None,
    ) -> None:
        user_properties_args = {"user_id": user_id}
        if email is not None:
            user_properties_args["user_email"] = email
        if ip is not None:
            user_properties_args["user_ip"] = ip
        if country_code is not None:
            user_properties_args["user_location"] = EventProperties.UserProperties.Location(country_code=country_code)
        if create_time is not None:
            user_properties_args["user_create_time"] = datetime_to_timestamp(create_time)
        if display_name is not None:
            user_properties_args["user_display_name"] = display_name

        identify_user_event = Event(
            id=uuid.uuid4().hex,
            type=EventTypes.USER_RECOGNIZE,
            create_time=datetime_to_timestamp(pendulum.now()),
            properties=EventProperties(user_properties=EventProperties.UserProperties(**user_properties_args)),
            project_id=self.project_id,
        )
        self._collect(identify_user_event)

    def create_message(self, session_id: str, message_index: int, role: str, content: str) -> None:
        if message_index <= 0:
            self.logger.error(f"Invalid message index '{message_index}': Message index must be a positive integer")
            return
        if role not in [ROLE_USER, ROLE_ASSISTANT]:
            self.logger.error(f"Invalid message role '{role}': Message role must be either 'user' or 'assistant'")
            return

        create_message_event = Event(
            id=uuid.uuid4().hex,
            type=EventTypes.MESSAGE_CREATE,
            create_time=datetime_to_timestamp(pendulum.now()),
            properties=EventProperties(
                message_properties=EventProperties.MessageProperties(
                    session_id=session_id,
                    message_index_hint=message_index,
                    message_role=EventProperties.MessageProperties.Role.ROLE_ASSISTANT
                    if role == ROLE_ASSISTANT
                    else EventProperties.MessageProperties.Role.ROLE_USER,
                    message_content=content,
                )
            ),
            project_id=self.project_id,
        )
        self._collect(create_message_event)

    def flush(self, timeout_seconds: int = FLUSH_TIMEOUT_SECONDS) -> None:
        self.worker.flush(timeout_seconds)

    def close(self, timeout_seconds: int = FLUSH_TIMEOUT_SECONDS) -> None:
        self.worker.stop(timeout_seconds)

    def _collect(self, event: Event) -> None:
        try:
            self.buffer_storage.push(event)
        except Exception as e:
            self.logger.exception(e)
