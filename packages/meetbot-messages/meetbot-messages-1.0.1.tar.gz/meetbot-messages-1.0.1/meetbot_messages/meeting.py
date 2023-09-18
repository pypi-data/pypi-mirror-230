# SPDX-FileCopyrightText: 2023 Contributors to the Fedora Project
#
# SPDX-License-Identifier: LGPL-3.0-or-later

from fedora_messaging import message

SCHEMA_URL = "http://fedoraproject.org/message-schema/"


class meetbotMessage(message.Message):
    @property
    def app_name(self):
        return "meetbot"

    @property
    def app_icon(self):
        return "https://apps.fedoraproject.org/img/icons/meetbot.png"

    @property
    def url(self):
        try:
            return self.body["url"]
        except KeyError:
            return None

    @property
    def groups(self):
        return []

    @property
    def packages(self):
        return []

    @property
    def containers(self):
        return []

    @property
    def modules(self):
        return []

    @property
    def flatpaks(self):
        return []


class MeetingStartV1(meetbotMessage):
    topic = "meetbot.meeting.start"

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a meeting is started",
        "type": "object",
        "properties": {
            "start_time": {"type": "string", "format": "date-time"},  # when the meeting was started
            "start_user": {"type": "string"},  # the user who started the meeting
            "location": {"type": "string"},  # the room or channel the meeting is in
            "meeting_name": {"type": "string"},  # the name of the meeting when the meeting started
        },
        "required": ["start_time", "start_user", "location", "meeting_name"],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        return (
            f"{self.agent_name} started meeting '{self.body['meeting_name']}' "
            f"in {self.body['location']} at {self.body['start_time']}"
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return f"Meeting '{self.body['meeting_name']}' started in {self.body['location']}"

    @property
    def agent_name(self):
        """The username of the user who started the meeting"""
        return self.body.get("start_user")

    @property
    def usernames(self):
        """will only ever know the meeting starter user here, so thats all we have"""
        return [self.agent_name]


class MeetingCompleteV1(meetbotMessage):
    topic = "meetbot.meeting.complete"

    ATTENDEE = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "lines_said": {"type": "integer"},
        },
        "required": ["name", "lines_said"],
    }

    LOG = {
        "type": "object",
        "properties": {
            "log_type": {"type": "string"},
            "log_url": {"type": "string", "format": "uri"},
        },
        "required": ["log_type", "log_url"],
    }

    body_schema = {
        "id": SCHEMA_URL + topic,
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for messages sent when a meeting is ended",
        "type": "object",
        "properties": {
            "start_time": {"type": "string", "format": "date-time"},  # when the meeting was started
            "start_user": {"type": "string"},  # the user who started the meeting
            "end_time": {"type": "string", "format": "date-time"},  # when the meeting was ended
            "end_user": {"type": "string"},  # the user who ended the meeting
            "location": {"type": "string"},  # the room or channel the meeting is in
            "meeting_name": {"type": "string"},
            "attendees": {"type": "array", "contains": ATTENDEE},
            "chairs": {"type": "array", "contains": {"type": "string"}},
            "url": {"type": "string", "format": "uri"},
            "logs": {"type": "array", "contains": LOG},
        },
        "required": [
            "start_time",
            "start_user",
            "end_time",
            "end_user",
            "location",
            "meeting_name",
            "url",
            "logs",
            "chairs",
            "attendees",
        ],
    }

    def __str__(self):
        """Return a complete human-readable representation of the message."""
        logs = ""
        for log in self.body["logs"]:
            logs = f"{logs}* [{log['log_type']}]({log['log_url']})\n"

        attendees = ""
        for attendee in self.body["attendees"]:
            attendees = f"{attendees}* {attendee['name']}: {attendee['lines_said']} lines said\n"
        return (
            f"{self.agent_name} ended meeting '{self.body['meeting_name']}' "
            f"in {self.body['location']} at {self.body['end_time']}\n\n"
            f"# Attendees\n\n"
            f"{attendees}"
            f"\n# Logs\n\n"
            f"{logs}"
        )

    @property
    def summary(self):
        """Return a summary of the message."""
        return f"Meeting '{self.body['meeting_name']}' in {self.body['location']} finished"

    @property
    def agent_name(self):
        """The username of the user who ended the meeting"""
        return self.body.get("end_user")

    @property
    def usernames(self):
        attendees = [a["name"] for a in self.body["attendees"]]
        names = self.body["chairs"] + [self.agent_name] + attendees
        return sorted(list(set(names)))
