# Copyright 2022 Splunk Inc. All rights reserved.

""" The Reporter class is intended to be used as a general interface to send
errors detected during validation to.

This is done in order to avoid raising errors for logging, and instead
provide a mechanism to store and retrieve report records such that a completed
validation check can be performed and provide detailed feedback for the errors
encountered.
"""
import inspect


class CheckMessage:
    """Base class for messages that may be yielded by Checks"""

    result = None

    def __init__(
        self,
        message,
        file_name=None,
        line_number=None,
        remediation=None,
    ):
        self._message = message
        self._file_name = file_name
        self._line_number = line_number
        self._remediation = remediation
        self.frame = inspect.currentframe()

    def __hash__(self):
        return hash((self._message, self._file_name, self._line_number, self._remediation))

    @property
    def message(self):
        message = self._message
        if self.remediation:
            message = f"{message} {self.remediation}"
        if self.file_name and self.line_number:
            message = f"{message} File: {self.file_name}, Line: {self.line_number}."
        elif self.file_name:
            message = f"{message} File: {self.file_name}"
        return message

    @property
    def file_name(self):
        return self._file_name

    @property
    def line_number(self):
        return self._line_number

    @property
    def remediation(self):
        return self._remediation

    def report(self, reporter):
        reporter.report(self)


class WarningMessage(CheckMessage):
    """Message indicating warning, usually a best practice or informational note to the developer"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = "warning"


class FailMessage(CheckMessage):
    """Message indicating a failure"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = "failure"


class ManualCheckMessage(CheckMessage):
    """Message indicating manual check is required"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = "manual_check"


class NotApplicableMessage(CheckMessage):
    """Message indicating a check was not applicable"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = "not_applicable"


class SkipMessage(CheckMessage):
    """Message indicating a check was skipped"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = "skipped"
