# Copyright 2019 Splunk Inc. All rights reserved.

"""Splunk app.conf abstraction module"""

from . import configuration_file


class AppConfigurationFile(configuration_file.ConfigurationFile):
    """Represents an [app.conf](http://docs.splunk.com/Documentation/Splunk/6.4.2/admin/Appconf)
    file.
    """

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)


def _is_check_app_config_file(app, reporter, status="not_applicable"):
    if not app.package.does_working_artifact_contain_default_app_conf():
        reporter_output = (
            "Splunk App packages should contain a"
            " `default/app.conf file`."
            f" No `default/app.conf` was found in `{app.package.origin_artifact_name}`."
        )

        if status == "fail":
            reporter.fail(reporter_output)
        elif status == "warn":
            reporter.warn(reporter_output)
        elif status == "skip":
            reporter.skip(reporter_output)
        else:
            reporter.not_applicable(reporter_output)

        return True
