# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 6.0

The following features should not be supported in Splunk 6.0 or later.
"""

from splunk_appinspect.check_messages import FailMessage
from splunk_appinspect.checks import Check, CheckConfig


class CheckForViewStatesConf(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_for_viewstates_conf",
                description="Check that `viewstates.conf` does not exist at `local/viewstates.conf`"
                "or at `default/viewstates.conf`. in the app."
                "(http://docs.splunk.com/Documentation/Splunk/6.0/AdvancedDev/Migration#Viewstates_are_no_longer_supported_in_simple_XML)",
                depends_on_config=("viewstates",),
                cert_min_version="1.6.1",
                tags=(
                    "splunk_appinspect",
                    "splunk_6_0",
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
        yield FailMessage(
            "There exists a viewstates.confwhich is deprecated from Splunk 6.0.",
            file_name=config["viewstates"].get_relative_path(),
        )


class CheckCrawlConfDenyList(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_crawl_conf_deny_list",
                description="Check that app does not contain crawl.conf as it was deprecated & removed in Splunk.",
                depends_on_config=("crawl",),
                cert_min_version="1.7.1",
                tags=(
                    "splunk_appinspect",
                    "splunk_6_0",
                    "deprecated_feature",
                    "splunk_7_0",
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
        yield FailMessage(
            "crawl.conf allows Splunk to introspect the file system, which is"
            " removed in Splunk 7.0 and not permitted.",
            file_name=config["crawl"].get_relative_path(),
        )
