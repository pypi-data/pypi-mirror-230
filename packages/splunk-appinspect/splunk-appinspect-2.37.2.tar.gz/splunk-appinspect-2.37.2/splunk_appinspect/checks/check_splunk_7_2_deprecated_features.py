# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 7.2

The following features should not be supported in Splunk 7.2 or later. For more, see [Deprecated features](http://docs.splunk.com/Documentation/Splunk/7.2.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](http://docs.splunk.com/Documentation/Splunk/latest/Installation/ChangesforSplunkappdevelopers).
"""

from splunk_appinspect.check_messages import FailMessage
from splunk_appinspect.checks import Check, CheckConfig


class CheckForDeprecatedLiteralsConf(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_for_deprecated_literals_conf",
                description="Check deprecated literals.conf existence.",
                depends_on_config=("literals",),
                cert_min_version="1.7.0",
                tags=(
                    "splunk_appinspect",
                    "splunk_7_2",
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
        if config["literals"]:
            yield FailMessage(
                "literals.conf has been deprecated in Splunk 7.2.",
                file_name=config["literals"].get_relative_path(),
                remediation="Please use messages.conf instead",
            )
