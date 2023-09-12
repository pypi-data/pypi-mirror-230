# Copyright 2020 Splunk Inc. All rights reserved.
"""Splunk telemetry.conf abstraction module"""
from . import configuration_file, splunk


class TelemetryConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [telemetry.conf](https://docs.splunk.com/Documentation/Splunk/8.0.3/Admin/Telemetryconf) file."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
        self._allow_list = splunk.telemetry_allow_list

    def check_allow_list(self, app):
        return app.name in self._allow_list
