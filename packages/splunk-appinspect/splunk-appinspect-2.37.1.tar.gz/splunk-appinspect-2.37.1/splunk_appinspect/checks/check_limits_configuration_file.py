# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Limits.conf file standards

Ensure that **/default/limits.conf** or **local/limits.conf** file is omitted.

When included in the app, the **limits.conf** file changes the limits that are placed on the system for hardware use and memory consumption, which is a task that should be handled by Splunk administrators and not by Splunk app developers. For more, see [limits.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Limitsconf).
"""


from splunk_appinspect.check_messages import FailMessage
from splunk_appinspect.checks import Check, CheckConfig


class CheckLimitsConf(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_limits_conf",
                description="Check that `default/limits.conf` or `local/limits.conf` has not been included.",
                depends_on_config=("limits",),
                cert_min_version="1.0.0",
                report_display_order=6,
                tags=(
                    "splunk_appinspect",
                    "cloud",
                    "private_app",
                    "private_classic",
                    "private_victoria",
                    "migration_victoria",
                ),
            )
        )

    def check_config(self, app, config):
        if "limits" in config:
            yield FailMessage(
                "Changes to 'limits.conf' are not allowed.Memory limits should be left to Splunk Administrators.",
                file_name=config["limits"].get_relative_path(),
                remediation="Please remove this file.",
            )
