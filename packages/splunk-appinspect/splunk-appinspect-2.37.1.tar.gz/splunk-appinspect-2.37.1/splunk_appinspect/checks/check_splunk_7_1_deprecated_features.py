# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 7.1

The following features should not be supported in Splunk 7.1 or later. For more, see [Deprecated features](http://docs.splunk.com/Documentation/Splunk/7.1.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](http://docs.splunk.com/Documentation/Splunk/latest/Installation/ChangesforSplunkappdevelopers).
"""

from splunk_appinspect.check_messages import FailMessage
from splunk_appinspect.check_routine import SPL_COMMAND_CHECKED_CONFS, find_spl_command_usage
from splunk_appinspect.checks import Check, CheckConfig


class CheckForInputCommandUsage(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_for_input_command_usage",
                description="Check for use of `input` SPL command in .conf files and SimpleXML.",
                cert_min_version="1.7.1",
                depends_on_config=SPL_COMMAND_CHECKED_CONFS,
                depends_on_data=("ui",),
                tags=(
                    "splunk_appinspect",
                    "splunk_7_1",
                    "deprecated_feature",
                    "splunk_7_3",
                    "removed_feature",
                    "cloud",
                    "private_app",
                    "private_victoria",
                    "migration_victoria",
                    "private_classic",
                ),
            )
        )

    def check_config(self, app, config):
        for file_name, line_number in find_spl_command_usage(app, r"input(\s*)(add|remove)", config=config):
            yield FailMessage(
                "`input` command is not permitted in Splunk Cloud as it was deprecated in Splunk "
                "7.1 and removed in Splunk 7.3.",
                file_name=file_name,
                line_number=line_number,
                remediation="Remove `input` from searches and configs",
            )

    def check_data(self, app, file_view):
        for file_name, _ in find_spl_command_usage(app, r"input(\s*)(add|remove)", file_view=file_view):
            yield FailMessage(
                "`input` command is not permitted in Splunk Cloud as it was deprecated in Splunk "
                "7.1 and removed in Splunk 7.3.",
                file_name=file_name,
                remediation="Remove `input` from searches and configs",
            )
