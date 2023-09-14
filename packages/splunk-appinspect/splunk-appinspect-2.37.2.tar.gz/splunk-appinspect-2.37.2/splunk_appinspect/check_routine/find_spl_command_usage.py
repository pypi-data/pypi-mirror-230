"""
Helper module to find splunk search command usage in app
"""

import os
import re

from . import util

# A mapping of conf file names to options within that file which might contain SPL
SPL_COMMAND_CHECKED_CONFS = {
    "savedsearches": ["search"],
    "commands": ["streaming_preop"],
    "macros": ["definition"],
    "searchbnf": ["syntax"],
    "transactiontypes": ["search"],
    "eventtypes": ["search"],
}


def find_spl_command_usage(app, command, config=None, file_view=None):
    """
    Search for the SPL command usage in the following files:

    savedsearches.conf, commands.conf, macros.conf, searchbnf.conf,
    transactiontypes.conf, default/*/*.xml

    Takes either `config` or `file_view` as passed to the `check_config` or `check_data` methods
    in class-based checks.

    yields (<filepath>, <lineno>) ...
    """

    if not (config or file_view):
        config = app.default_config

        if app.default_file_view and "data" in app.default_file_view:
            file_view = app.default_file_view["data"]

    command = r"(^|\W)" + command + r"(\W|$)"

    if config:
        for conf_filename, options in SPL_COMMAND_CHECKED_CONFS.items():
            if conf_filename not in config:
                continue
            yield from _find_spl_command_usage_in_conf_file(command, config[conf_filename], options)

    if file_view:
        yield from _find_spl_command_usage_in_simple_xml(command, file_view)


def _find_spl_command_usage_in_simple_xml(command, file_view):
    xml_files = list(file_view.get_filepaths_of_files(types=[".xml"]))
    nodes = [util.xml_node("query"), util.xml_node("searchString")]
    query_nodes = util.find_xml_nodes_usages(xml_files, nodes)
    for query_node, relative_filepath in query_nodes:
        query_string = query_node.text
        match = re.search(command, query_string)
        if match:
            yield (relative_filepath, None)


def _find_spl_command_usage_in_conf_file(command, conf_file, option_names):
    for section_name in conf_file.section_names():
        for option_name in option_names:
            if not conf_file.has_option(section_name, option_name):
                continue
            option = conf_file[section_name].get_option(option_name)
            match = re.search(command, option.value)
            if match:
                yield (option.get_relative_path(), option.get_line_number())
