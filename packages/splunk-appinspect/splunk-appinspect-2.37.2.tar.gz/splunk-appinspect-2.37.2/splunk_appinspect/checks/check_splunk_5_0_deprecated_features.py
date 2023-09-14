# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 5.0

The following features should not be supported in Splunk 5.0 or later.
"""
import os

import splunk_appinspect
from splunk_appinspect.check_messages import FailMessage
from splunk_appinspect.check_routine import SPL_COMMAND_CHECKED_CONFS, find_spl_command_usage
from splunk_appinspect.checks import Check, CheckConfig


class CheckForSavedsearchesUsedInEventtypesConf(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_for_savedsearches_used_in_eventtypes_conf",
                description="""Check that saved searches are not used within event types.
                        https://docs.splunk.com/Documentation/Splunk/5.0/ReleaseNotes/Deprecatedfeatures
                        https://docs.splunk.com/Documentation/Splunk/7.2.5/Knowledge/Abouteventtypes
                        """,
                cert_min_version="1.7.0",
                depends_on_config=(("eventtypes",)),
                tags=(
                    "splunk_appinspect",
                    "splunk_5_0",
                    "deprecated_feature",
                    "cloud",
                    "private_app",
                    "private_victoria",
                    "migration_victoria",
                    "private_classic",
                ),
            )
        )

    def check_config(self, app, config):
        eventtypes_conf = config["eventtypes"]
        for section in eventtypes_conf.sections():
            for setting in section.settings():
                if setting.name == "search" and "| savedsearch " in setting.value:
                    yield FailMessage(
                        "Detect saved search used within event types. "
                        "Saved search in event types is deprecated in Splunk 5.0. "
                        "Pleas specify search terms for the event type.",
                        file_name=config["eventtypes"].get_relative_path(),
                        line_number=setting.lineno,
                    )


class CheckDeprecatedEventtypeAutodiscovering(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_deprecated_eventtype_autodiscovering",
                description="Check for use of `findtypes` SPL command in .conf files and SimpleXML.",
                cert_min_version="1.7.0",
                depends_on_config=SPL_COMMAND_CHECKED_CONFS,
                depends_on_data=("ui",),
                tags=(
                    "splunk_appinspect",
                    "splunk_5_0",
                    "deprecated_feature",
                    "cloud",
                    "private_app",
                    "private_victoria",
                    "migration_victoria",
                    "private_classic",
                ),
            )
        )

    def check_config(self, app, config):
        for file_name, line_number in find_spl_command_usage(app, "findtypes", config=config):
            yield FailMessage(
                "`findtypes` command is not permitted in Splunk Cloud as it was deprecated in Splunk 5.0.",
                file_name=file_name,
                line_number=line_number,
                remediation="Remove `findtypes` from searches and configs",
            )

    def check_data(self, app, file_view):
        for file_name, _ in find_spl_command_usage(app, "findtypes", file_view=file_view):
            yield FailMessage(
                "`findtypes` command is not permitted in Splunk Cloud as it was deprecated in Splunk 5.0.",
                file_name=file_name,
                remediation="Remove `findtypes` from dashboards",
            )
