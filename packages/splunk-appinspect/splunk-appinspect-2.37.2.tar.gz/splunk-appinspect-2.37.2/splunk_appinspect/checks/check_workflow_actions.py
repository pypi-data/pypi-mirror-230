# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Custom workflow actions structure and standards

Custom workflow actions are defined in a **workflow_actions.conf** file in the **/default** directory of the app. For more, see [About lookups](http://docs.splunk.com/Documentation/Splunk/latest/Knowledge/Aboutlookupsandfieldactions) and [workflow_actions.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Workflow_actionsconf).
"""
import logging
import os

import splunk_appinspect
from splunk_appinspect.check_messages import FailMessage
from splunk_appinspect.checks import Check, CheckConfig

logger = logging.getLogger(__name__)

report_display_order = 20


class CheckWorkflowActionsHaveRequiredProperties(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_workflow_actions_have_required_properties",
                description="Check that stanzas in `workflow_actions.conf.spec` have the required "
                "fields, type, and label.",
                depends_on_config=("workflow_actions",),
                cert_min_version="1.1.7",
                tags=(
                    "splunk_appinspect",
                    "custom_workflow_actions",
                ),
            )
        )

    def check_config(self, app, config):
        for section in config["workflow_actions"].sections():
            if not section.has_option("type"):
                yield FailMessage(
                    f"The stanza [{section.name}] does not specify 'type'.",
                    file_name=section.get_relative_path(),
                    line_number=section.get_line_number(),
                )

            if not section.has_option("label"):
                yield FailMessage(
                    f"The stanza [{section.name}] does not specify 'label'.",
                    file_name=section.get_relative_path(),
                    line_number=section.get_line_number(),
                )


class CheckWorkflowActionsLinkUriDoesNotUseHttpProtocol(Check):
    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_workflow_actions_link_uri_does_not_use_http_protocol",
                description="Check that for each workflow action in `workflow_actions.conf` the "
                "link.uri property uses the https protocol for external links. Unencrypted "
                "http is permitted for internal links.",
                depends_on_config=("workflow_actions",),
                cert_min_version="1.1.20",
                tags=(
                    "splunk_appinspect",
                    "cloud",
                    "private_app",
                    "private_victoria",
                    "migration_victoria",
                    "private_classic",
                ),
            )
        )

    def check_config(self, app, config):
        for section in config["workflow_actions"].sections():
            if not section.has_option("link.uri"):
                continue

            setting = section.get_option("link.uri")
            link_uri = setting.value.strip()

            if link_uri.startswith(
                (
                    "/",
                    "http://localhost",
                    "http://127.0.0.1",
                    "localhost",
                    "127.0.0.1",
                    "https://",
                )
            ):
                continue

            yield FailMessage(
                f"The workflow action [{section.name}] `link.uri` property appears to be an "
                "external link that is unencrypted.",
                file_name=setting.get_relative_path(),
                line_number=setting.get_line_number(),
                remediation="Change the `link.uri` property to use https",
            )
