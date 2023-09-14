# Copyright 2019 Splunk Inc. All rights reserved.

"""Checks contains both the group class and the check class. These classes
serve as the basic scaffolding to connect the implied structure of validation
checks. One group consists of many checks. Implementation wise, each file in
the folder of splunk_appinspect/checks/ is a group. Inside each on of those
files are checks.
"""
import functools
import imp
import inspect
import itertools
import logging
import operator
import os
import re
import sys
from builtins import str as text
from collections import defaultdict
from dataclasses import dataclass
from typing import Sequence

import bs4
import markdown
import semver

import splunk_appinspect
import splunk_appinspect.infra
from splunk_appinspect.check_messages import FailMessage, NotApplicableMessage
from splunk_appinspect.configuration_parser import InvalidSectionError

logger = logging.getLogger(__name__)

DEFAULT_CHECKS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "checks")


class ResourceUnavailableException(Exception):
    """An exception to throw when the Check class cannot find a resource needed
    for dependency injection.
    """


class ResourceCrashException(Exception):
    """An exception to throw when the Check class cannot setup a resource
    for dependency injection.
    """


def get_module_name_from_path(base, path):
    """Given a full path to a file, pull out the base filename."""
    name, _ = os.path.splitext(os.path.relpath(path, base))
    return name.replace(os.sep, ".")


def import_group_modules(directory_paths):
    """Returns a list of python modules from a set of directory paths

    Returns:
        List of Python Module objects

    Arguments:
        directory_paths (List of Strings): A list of directory paths
    """
    group_modules_to_return = []

    for check_dir in directory_paths:
        file_pattern_regex = re.compile("check_.+.py$", re.IGNORECASE)
        for directory_path, _, file_names in os.walk(check_dir):
            logger.debug("Beginning group generation on directory: %s", check_dir)
            for file in [file_name for file_name in file_names if re.match(file_pattern_regex, file_name)]:
                filepath = os.path.join(directory_path, file)
                group_module_name = get_module_name_from_path(check_dir, filepath)
                group_module = imp.load_source(group_module_name, filepath)
                group_modules_to_return.append(group_module)

    return group_modules_to_return


def generate_checks(module):
    """A helper function to create a list of Check objects from a provided
    module.

    Returns:
        List of Check objects: A list of check objects that represent each
            function in the module.

    Arguments:
    """
    check_objects = []
    for obj_name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and obj_name.startswith("check_"):
            # Legacy style check
            check = Check.from_legacy_function(obj_name, obj)
        elif inspect.isclass(obj) and issubclass(obj, Check) and obj != Check:
            # New style check
            check = obj()
        else:
            continue

        check_objects.append(check)
    return check_objects


def generate_group(
    group_module,
    included_tags=None,
    excluded_tags=None,
    version=None,
    splunk_version="latest",
    custom_group=False,
):
    """A helper function to create a group object based on a modules that is
    provided.

    Returns:
        Group object: Returns a Group object. The Group object should represent
            the respective module that was provided.

    Arguments:
        group_module (List of Python Module objects): A list of python module
            objects
        included_tags (List of Strings) - Tags to select checks with
        excluded_tags (List of Strings) - Tags to deselect checks with
        version (String) - The version of Splunk AppInspect being targeted
        splunk_version (semver.VersionInfo) - The version of Splunk being targeted
        custom_group (Boolean) - If the group being created is a custom group
    """
    if included_tags is None:
        included_tags = []
    if excluded_tags is None:
        excluded_tags = []
    if version is None:
        version = semver.VersionInfo.parse(splunk_appinspect.version.__version__)

    # Group Generation
    logger.debug("Beginning check generation on group name: %s", group_module.__name__)

    # Check Generation
    check_list = generate_checks(group_module)

    filtered_checks = [
        check
        for check in check_list
        if (check.matches_tags(included_tags, excluded_tags) and check.matches_version(version))
    ]

    # Debuging output for check filtering
    logger.debug("Included Tags: %s", ",".join(included_tags))
    logger.debug("Excluded Tags: %s", ",".join(excluded_tags))
    logger.debug("Version: %s", version)
    logger.debug("Splunk Version: %s", splunk_version)
    logger.debug("Is Custom Group: %s", custom_group)
    logger.debug("--- All Checks ---")
    for check in check_list:
        logger_output = (
            f"check_name:{check.name},"
            f"matches_tags:{check.matches_tags(included_tags, excluded_tags)},"
            f"matches_version:{check.matches_version(version)}"
        )
        logger.debug(logger_output)

    logger.debug("--- Filtered Checks ---")
    for check in filtered_checks:
        logger_output = (
            f"check_name:{check.name},"
            f"matches_tags:{check.matches_tags(included_tags, excluded_tags)},"
            f"matches_version:{check.matches_version(version)}"
        )
        logger.debug(logger_output)

    new_group = Group(group_module, checks=filtered_checks, custom_group=custom_group)

    return new_group


def groups(
    check_dirs=None,
    custom_checks_dir=None,
    included_tags=None,
    excluded_tags=None,
    version=None,
    splunk_version="latest",
):
    """Return a list of Group objects.

    Generates a list of Group objects by iterating through specified directories
    and concatenates them together into a single list.

    :param check_dirs (List of strings) - A list of strings that are paths to
        directories that contain group files. Inside the group file check
        functions exist.
    :param custom_checks_dir (String) - A string that is a path to a custom
        check directory.
    """
    if check_dirs is None:
        check_dirs = [DEFAULT_CHECKS_DIR]
    if included_tags is None:
        included_tags = []
    if excluded_tags is None:
        excluded_tags = []
    if version is None:
        version = semver.VersionInfo.parse(splunk_appinspect.version.__version__)

    groups_to_return = []
    check_group_modules = import_group_modules(check_dirs)
    for group_module in check_group_modules:
        check_group = generate_group(
            group_module,
            included_tags=included_tags,
            excluded_tags=excluded_tags,
            version=version,
            splunk_version=splunk_version,
            custom_group=False,
        )
        # Don't return a group that does not have checks
        if list(check_group.checks()):
            groups_to_return.append(check_group)

    # TODO: Convert to support mutiple custom checks directory
    #       Do not forget to convert command line to support multiple directories
    # TODO: tests needed
    if custom_checks_dir:
        custom_group_modules = import_group_modules([custom_checks_dir])
        for group_module in custom_group_modules:
            custom_check_group = generate_group(
                group_module,
                included_tags=included_tags,
                excluded_tags=excluded_tags,
                version=version,
                splunk_version=splunk_version,
                custom_group=True,
            )

            # Don't return a group that does not have checks
            if list(custom_check_group.checks()):
                groups_to_return.append(custom_check_group)

    groups_ordered_by_report_display_order = sorted(groups_to_return, key=operator.attrgetter("report_display_order"))
    return groups_ordered_by_report_display_order


def checks(check_dirs=[DEFAULT_CHECKS_DIR], custom_checks_dir=None):
    """Return a generator object that yields a Check object.

    Iterate through all checks.

    :param check_dirs (List of Strings) - A list of strings that are paths
        pointing to directories containing group files.
    :param custom_checks_dir (String) - A strings that is the path pointing to
        a custom directory containing group files.
    """
    for group in groups(check_dirs=check_dirs):
        for check in group.checks(check_dirs, custom_checks_dir):
            yield check


class Group(object):
    """A group represents a group of checks- namely, all those contained within
    a single file. The documentation for the group is extracted from the Python
    module docstring.
    """

    def __init__(self, module, checks=None, report_display_order=None, custom_group=False):
        """Constructor function."""
        self.name = module.__name__
        self.module = module

        # Checks
        # If checks aren't provided then, they are generated from the module
        if checks is None:
            self._checks = splunk_appinspect.checks.generate_checks(module)
        else:
            self._checks = checks

        # Report Display Order
        if report_display_order is None:
            report_order = getattr(module, "report_display_order", 1000)
            if custom_group:
                # Order custom checks to be last.
                report_order += 10000
        else:
            report_order = report_display_order
        self.report_display_order = report_order

        # Custom Group
        self.custom_group = custom_group

    def doc(self):
        """Returns the docstring for the module, or if not defined the name."""
        return self.doc_text()

    def doc_raw(self):
        """Returns the raw doc string."""
        docstring = self.module.__doc__
        if docstring:
            return docstring

        return self.name

    def doc_text(self):
        """Returns the plain text version of the doc string."""
        doc = self.doc_raw()
        soup = bs4.BeautifulSoup(markdown.markdown(doc), "lxml")
        text = "".join(soup.findAll(text=True))
        if self.custom_group:
            text = text + " (CUSTOM CHECK GROUP)"
        return text

    def doc_name_human_readable(self):
        """Returns the contents of the Markdown h3 element from the top of the
        group's docstring."""
        html = markdown.markdown(self.doc_raw(), extensions=["markdown.extensions.fenced_code"])
        bs_html = bs4.BeautifulSoup(html, "html.parser", store_line_numbers=False)
        if bs_html.h3 is not None and bs_html.h3.contents:
            return text(bs_html.h3.contents[0]).strip()
        return ""

    def doc_html(self):
        """Returns the docstring (provided in markdown) as a html element."""
        html = markdown.markdown(self.doc_raw(), extensions=["markdown.extensions.fenced_code"])
        bs_html = bs4.BeautifulSoup(html, "html.parser", store_line_numbers=False)
        # Create a <a name="check_group_name"></a> to optionally be used for TOC
        new_tag = bs_html.new_tag("a")
        new_tag["name"] = self.name
        bs_html.h3.contents.insert(0, new_tag)
        return text(bs_html)

    def has_checks(self, **kwargs):
        """Checks to see whether the group has checks or not.

        NOTE: that filters are applied, so if a tags or version is specified,
        this may return 0 even if there are checks defined.
        """
        # TODO: tests needed
        return len([check for check in self.checks(**kwargs)]) > 0

    def count_total_static_checks(
        self,
        included_tags=None,
        excluded_tags=None,
        version=None,
        splunk_version="latest",
    ):
        """A helper function to return the count of static checks.

        Returns:
            Integer: A number representing the amount of checks that are dynamic
            checks.

        Arguments:
            included_tags (List of Strings) - Tags to select checks with
            excluded_tags (List of Strings) - Tags to deselect checks with
            version (String) - The version of Splunk AppInspect being targeted
            splunk_version (String) - The version of Splunk being targeted
        """
        # TODO: tests needed
        if included_tags is None:
            included_tags = []
        if excluded_tags is None:
            excluded_tags = []
        if version is None:
            version = splunk_appinspect.version.__version__

        total_static = len(
            [
                check
                for check in self.checks(
                    included_tags=included_tags,
                    excluded_tags=excluded_tags,
                    version=version,
                    splunk_version=splunk_version,
                )
            ]
        )
        return total_static

    def add_check(self, check_to_add):
        """A helper function for adding Check objects to the Group.

        Returns:
            None

        Arguments:
            check_to_add (Check object): A check object that will be added to
                the group's list of checks.
        """
        # TODO: tests needed
        self._checks.append(check_to_add)

    def remove_check(self, check_to_remove):
        """A helper function for removiong Check objects from the Group.

        Returns:
            None

        Arguments:
            check_to_remove (Check object): A check object that will be removed
                from the group's list of checks.
        """
        # TODO: tests needed
        self._checks.remove(check_to_remove)

    def checks(
        self,
        included_tags=None,
        excluded_tags=None,
        version=None,
        splunk_version="latest",
    ):
        """A function to return the checks that the group owns.

        Returns:
            An iterator of Check objects: A list of check objects representing
                the checks owned by the group, that were filtered accordingly.

        Arguments:
            included_tags (List of Strings) - Tags to select checks with
            excluded_tags (List of Strings) - Tags to deselect checks with
            version (String) - The version of Splunk AppInspect being targeted
            splunk_version (String) - The version of Splunk being targeted
        """
        if included_tags is None:
            included_tags = []
        if excluded_tags is None:
            excluded_tags = []
        if version is None:
            version = splunk_appinspect.version.__version__

        check_list = self._checks

        ordered_checks = sorted(check_list, key=operator.attrgetter("report_display_order"))

        for check in ordered_checks:
            should_check_be_returned = check.matches_tags(included_tags, excluded_tags) and check.matches_version(
                version
            )
            logger_output = (
                f"check_name:{check.name},"
                f"matches_tags:{check.matches_tags(included_tags, excluded_tags)},"
                f"matches_version:{check.matches_version(version)},"
                f"should_check_be_returned:{should_check_be_returned}"
            )
            logger.debug(logger_output)

            if should_check_be_returned:
                yield check

    def check_count(self):
        """A helper function to return the number of checks that exist.

        Returns:
            Integer: the total number of checks that exist.
        """
        # TODO: tests needed
        return len(list(self.checks()))

    def has_check(self, check):
        """A helper function to determine if the check exists.

        Returns:
            Boolean: Checks exists.
        """
        return any(chk.name == check.name for chk in self._checks)

    def tags(self):
        """Helper function to generate the set of tags that for all the checks
        in the group.

        Returns:
            List of strings: A list of tags found in the checks. Only unique
                tags will be returned. (No tags will be duplicated)
        """
        tags_to_return = []
        for check in self._checks:
            for tag in check.tags:
                if tag not in tags_to_return:
                    tags_to_return.append(tag)

        return tags_to_return


class Check(object):
    """Wraps a check function and allows for controlled execution."""

    def __init__(self, config, fun=None):
        """Constructor Initialization

        Arguments:
            config (CheckConfig): configuration for the check such as name,
                tags, description, etc.
            fun (Function): A callable that will be executed when the check is
                run. If not provided, the `check` method will be called.
        """
        self._config = config
        self.fun = fun

    @classmethod
    def from_legacy_function(cls, name, fun):
        """Helper method to instantiate a Check instance from a legacy check function

        Args:
            name (String): a short name to identify the check. By default the
                name of the python function
            fun (Function): A callable that will be executed when the check is
                run.

        Returns:
            Check: an instance of Check that wraps `fun`
        """

        config = CheckConfig(
            name=name,
            description=getattr(fun, "__doc__", None) or name,
            tags=getattr(fun, "tags", None) or tuple(),
            cert_min_version=getattr(fun, "min_version", None),
            cert_max_version=getattr(fun, "max_version", None),
            report_display_order=getattr(fun, "report_display_order", None),
        )
        return cls(config, fun)

    def __repr__(self):
        """A function overload for getting the string representation of an
        object.

        Returns:
            String - representing the object's debug info.
        """
        return "<splunk_appinspect.check:" + (self.name or "unknown") + ">"

    def has_tag(self, tags):
        """A helper function identifiyng if the check has tags.

        Returns:
            Boolean - True if the check has tags, False if it is does NOT have
                tags
        """
        for tag in tags:
            if tag in self.tags:
                return True
        return False

    def matches_version(self, version_to_match):
        """Returns true if version is greater than the min_version set on the
        function (if one is set) and version is less than max_version on the
        function (if set).  If no min_version is set return true.

        :param version_to_match: the version to match on
        """
        if version_to_match is None:
            return True

        if self._config.cert_min_version:
            return version_to_match >= self._config.cert_min_version and (
                self._config.cert_max_version is None or version_to_match <= self._config.cert_max_version
            )

        return True

    def doc(self, include_version=False):
        """Returns the docstring provided with the underlying function, or the
        name if not provided.

        :param include_version - Bool - defaults to false. specifies if the
            check version should be included in the documentation.
        """
        # TODO: tests needed
        doc_text = self.doc_text()
        if include_version:
            doc_text = f"{doc_text} {self.version_doc()}"

        return doc_text

    def doc_html(self, include_version=False):
        """Returns the docstring (provided in markdown) as a html element."""
        # TODO: tests needed
        html = markdown.markdown(self.doc_raw(), extensions=["markdown.extensions.fenced_code"])

        if include_version:
            html = f"{html} {self.version_doc()}"

        return html

    def doc_text(self):
        """Returns the plain text version of the doc string."""
        # Normalize spacing (as found in code), keep line breaks
        # TODO: tests needed
        p = re.compile(r"([ \t])+")
        doc = p.sub(r"\1", self.doc_raw().strip())

        soup = bs4.BeautifulSoup(markdown.markdown(doc), "lxml")
        text = "".join(soup.findAll(text=True))
        return text

    def doc_raw(self):
        """Returns the raw stripped doc string."""
        # TODO: tests needed
        return self._config.description or self._config.name

    def version_doc(self):
        """Returns the version range of the check."""
        # TODO: tests needed
        ver_doc = f"({self.min_version_doc}-{self.max_version_doc})"
        return ver_doc

    @property
    def name(self):
        """Returns the check name as defined in the CheckConfig class

        Note:
            If the CheckConfig class doesn't have a check name, we attempt to
            calculate one by un-CamelCase-ing the class name. For example
            `CheckForAddonBuilderVersion` becomes `check_for_addon_builder_version`"""
        return self._config.name or re.sub("([A-Z])", r"_\1", self.__class__.__name__).strip("_").lower()

    @property
    def report_display_order(self):
        """Return an integer.

        Returns a report display order number. This indicates the order to
        display report elements in.
        """
        return self._config.report_display_order or 1000

    @property
    def min_version_doc(self):
        """Returns the min version specified against the check."""
        # TODO: tests needed
        return self._config.cert_min_version or "1.0"

    @property
    def max_version_doc(self):
        """Returns the max version specified against the check."""
        # TODO: tests needed
        return self._config.cert_max_version or "1.0"

    @property
    def tags(self):
        """Returns the tags of the checks if they exist  or returns an empty
        tuple.
        """
        return self._config.tags or tuple()

    def matches_tags(self, included_tags, excluded_tags):
        """Returns a boolean.

        Returns a boolean indicating if the check object's tags match the
        included or excluded tags.

        If included tags has values and excluded tags has values the included
        tags take precendence and will match.

        If only included tags has values then all tags are allow list matched
        against included tags.

        If only excluded tags has values, then all tags are deny list matched
        against excluded tags.

        If neither included_tags and excluded_tags has values then it will
        always return True as a match.

        :param included_tags (A list of Strings) - Include only checks with the
            defined tags.
        :param excluded_tags (A list of Strings) - Exclude checks with these tags
        """
        check_tags_set = set(self.tags)
        included_tags_set, excluded_tags_set = splunk_appinspect.infra.refine_tag_set(included_tags, excluded_tags)
        if not included_tags_set and not excluded_tags_set:
            return True

        if included_tags_set and not excluded_tags_set:
            return not check_tags_set.isdisjoint(included_tags_set)

        if not included_tags_set and excluded_tags_set:
            return check_tags_set.isdisjoint(excluded_tags_set)

        if included_tags_set and excluded_tags_set:
            return not check_tags_set.isdisjoint(included_tags_set) and check_tags_set.isdisjoint(excluded_tags_set)

        return True

    def run(self, app, resource_manager_context=None):
        """This is in a way the central method of this library.  A check can be
        run, and it returns a 'reporter' object.  Whatever the result- success,
        failure, exception, etc, it will be encoded in that reporter
        object.

        :param app The app to run this check against.
        :param resource_manager_context Some instances require a running Splunk
          instance.  This dictionary provides references to those instances by
          name, and they are matched on the parameter name for the underlying
          function.  For example, a clamav instance is created for use by the
          tests, creating a check function with the signature

          def check_something(reporter, clamav):
            pass

          will get the clamav instance passed as the second parameter,
          provided clamav is defined when ResourceManager(clamav=...) is
          initialized.  This is extended so that if the value is callable, it
          will be called and the result will be passed in as that parameter.
        """
        if not resource_manager_context:
            resource_manager_context = {}
        reporter = splunk_appinspect.reporter.Reporter()
        reporter.start()
        try:
            logging.debug("Executing %s", self.name)
            # This is a bit of magic, the idea for which was taken from pytest.
            # Basically checks will need some variety of app, reporter, and/or
            # access to a splunk instance (or instances).  Instead of having a
            # crazy set of parameters, use the name of the parameters to map to
            # what we pass.  As a result, the signature of a check can be:
            #   def check_something(app, reporter)        -> app directory and reporter
            #   def check_something(app)                  -> we are going to use assert
            #   def check_something(clamav, reporter)     -> we are going to use clamav and reporter
            #   def check_something(clamav)               -> using the clamav and just assert
            #   def check_something(foobarbaz)            -> throws a TypeError.
            # Any splunk instance passed in using the splunk_instances named
            # parameter becomes an available argument to the checks.

            if callable(self.fun):
                available_args = dict()

                available_args["app"] = app
                available_args["reporter"] = reporter

                args = []
                function_arguments = inspect.getfullargspec(self.fun).args
                for arg in function_arguments:
                    if arg in available_args:
                        val = available_args[arg]
                        if callable(val):
                            args.append(val())
                        else:
                            args.append(val)
                    elif arg in resource_manager_context:
                        # TODO: tests needed
                        logging.debug("Getting resource: '%s' for %s", arg, self.fun.__name__)

                        rm_ctx = resource_manager_context[arg]
                        if hasattr(rm_ctx, "state") and rm_ctx.state != 0:
                            error_string = (
                                f"{self.fun.__name__} has been skipped because the specified"
                                f" resource {rm_ctx.__class__.__name__} provided could not be setup correctly."
                            )

                            logger.debug(
                                "Resource %s has an invalid state %s",
                                rm_ctx.__class__.__name__,
                                rm_ctx.state,
                            )
                            raise ResourceUnavailableException(error_string)

                        args.append(rm_ctx)
                    elif hasattr(resource_manager_context, "context") and arg in resource_manager_context.context:
                        logging.debug("Getting argument: '%s' for %s", arg, self.fun.__name__)

                        args.append(resource_manager_context.context[arg])
                    else:
                        # TODO: tests needed
                        error_string = (
                            f"{self.fun.__name__} has been skipped because the specified"
                            " instances provided did not match the"
                            " required instance types."
                            f" Instances provided: {resource_manager_context.keys()}."
                            ""
                        )
                        raise ResourceUnavailableException(error_string)

                self.fun(*args)
            else:
                # Current behavior is to report everything. There are a few checks however
                # that modify their behavior based on the presence of the `cloud` tag. The
                # only use of this at time of implementation is `if "cloud" in included_tags`.
                # This is where a message could have conditional reporting logic to only report
                # for certain tags, e.g. `for_tags=("cloud",)`. However, instead we will attempt
                # to split checks that have tag-dependent results.
                seen = set()
                for message in self.check(app):
                    if hash(message) not in seen:
                        message.report(reporter)
                        seen.add(hash(message))
        except NotImplementedError:
            e = sys.exc_info()
            reporter.exception(e, "failure")
        except ResourceUnavailableException:
            e = sys.exc_info()
            reporter.exception(e, "skipped")
        except ResourceCrashException as e:
            reporter.fail(str(e))
        except InvalidSectionError as e:
            reporter.fail(
                f"{e.file_name} is malformed. Details: {str(e)}",
                e.file_name,
                e.line_no,
            )
        except Exception:
            e = sys.exc_info()
            logging.exception(e)
            reporter.exception(e)
        logging.debug("check %s %s", self.name, reporter.state())

        reporter.complete()
        return reporter

    def _implemented(self, method_name):
        """Returns True and the method if this method_name was implemented by the
        child class, (False, None) otherwise.

        Args:
            method_name (str): method name to interrogate

        Returns:
            (bool, function): (True, method) if the method has been implemented,
            (False, None) otherwise
        """
        # Get the method, this may or may not be the parent method
        method = getattr(self, method_name, None)
        if method is None:
            return False, None
        # Get the parent method
        parent_method = getattr(super(type(self), self), method_name, None)
        # If the child method is a different function then it has been implemented
        if parent_method is None:
            return False, None
        impl = method != parent_method
        return impl, method if impl else None

    # Methods for new-style checks
    def check(self, app):
        """This method is called once per app with a reference to the app itself.

        Note:
            By default this method will call the other narrowed check_* methods.
            If none of those apply, this method can be overridden instead.

        Args:
            app (App): the app to be checked

        Yields:
            Subclass of CheckMessage depending on the result"""
        should_check = {}
        did_check = defaultdict(lambda: False)

        config_check_methods = (
            "check_config",
            "check_default_config",
            "check_merged_config",
            "check_local_config",
        )
        should_check["config"] = any([self._implemented(method_name)[0] for method_name in config_check_methods])

        if should_check["config"]:
            depends_on_config = self._config.depends_on_config or []
            configs_to_check = []
            for location in ("default", "local", "merged"):
                config = getattr(app, f"{location}_config", {})
                if not config:
                    continue
                if not any([conf_file_depends in config for conf_file_depends in depends_on_config]):
                    continue
                if location in ("default", "merged"):
                    # Do not run check_config for local
                    configs_to_check.append(config)
                check_method_name = f"check_{location}_config"
                impl, check_method = self._implemented(check_method_name)
                if impl and callable(check_method):
                    did_check["config"] = True
                    yield from check_method(app, config) or []

            if self._implemented("check_config")[0] and configs_to_check:
                did_check["config"] = True
                for config in configs_to_check:
                    yield from self.check_config(app, config) or []

        data_check_methods = (
            "check_data",
            "check_default_data",
            "check_merged_data",
            "check_local_data",
        )
        should_check["data"] = any([self._implemented(method_name)[0] for method_name in data_check_methods])
        if should_check["data"]:
            depends_on_data = self._config.depends_on_data or []
            file_views_to_check = []
            for location in ("default", "local", "merged"):
                loc_file_view = getattr(app, f"{location}_file_view", {})
                if not (loc_file_view and "data" in loc_file_view):
                    continue
                if not any([data_depends in loc_file_view["data"] for data_depends in depends_on_data]):
                    continue
                file_views_to_check.append(loc_file_view["data"])
                check_method_name = f"check_{location}_data"
                impl, check_method = self._implemented(check_method_name)
                if impl and callable(check_method):
                    did_check["data"] = True
                    yield from check_method(app, loc_file_view["data"]) or []

            if self._implemented("check_data")[0] and file_views_to_check:
                did_check["data"] = True
                for loc_file_view in file_views_to_check:
                    yield from self.check_data(app, loc_file_view) or []

        # If app has lookups, run lookup checks
        for location in ("lookups", "metadata", "static"):
            if location.endswith("s"):
                check_all_method_name = f"check_{location}"
                check_one_method_name = f"check_{location[:-1]}_file"
            else:
                check_all_method_name = f"check_{location}_files"
                check_one_method_name = f"check_{location}_file"

            all_impl, check_all_method = self._implemented(check_all_method_name)
            one_impl, check_one_method = self._implemented(check_one_method_name)

            should_check[location] = all_impl or one_impl

            if not app.directory_exists(location):
                continue

            file_view = app.get_file_view(location)
            if all_impl and callable(check_all_method):
                did_check[location] = True
                yield from check_all_method(app, file_view) or []

            if one_impl and callable(check_one_method):
                did_check[location] = True
                for directory, filename, _ in file_view.iterate_files():
                    yield from check_one_method(app, os.path.join(directory, filename)) or []

        other_check_methods = [
            value
            for (_, value) in inspect.getmembers(
                self,
                predicate=lambda member: callable(member) and getattr(member, "is_check_method", False),
            )
        ]

        for check_method in other_check_methods:
            should_check[check_method.__name__] = True

            did_check[check_method.__name__], check_results = check_method(app)

            if not did_check[check_method.__name__]:
                continue

            yield from check_results or []

        if not any([did_check[loc] for loc in should_check]):
            if should_check["config"]:
                for conf_file_depends in depends_on_config:
                    yield NotApplicableMessage(f"{conf_file_depends}.conf does not exist")

            if should_check["data"]:
                for data_depends in depends_on_data:
                    yield NotApplicableMessage(f"{os.path.join('data', data_depends)} does not exist")

            for location in ("lookups", "metadata", "static"):
                if should_check[location]:
                    yield NotApplicableMessage(f"The `{location}` directory does not exist.")

            for check_method in other_check_methods:
                if check_method.not_applicable_message is None:
                    continue
                yield NotApplicableMessage(check_method.not_applicable_message)

    def check_config(self, app, config):
        """Use this method to check configs across default and the merged view using the same logic
        for each.
        This is called at most twice:
          1) With the `config` argument equal to a `ConfigurationProxy` representing the default
             configuration if `depends_on_config` is specified AND at least one of the configs in
             `depends_on_config` exists within `<app>/default/<config>.conf`
          2) With the `config` argument equal to a `MergedConfigurationProxy` representing the merged
             configuration of local and default if `depends_on_config` is specified AND at least one
             of the configs in `depends_on_config` exists within `<app>/[default|local]/<config>.conf`

        Args:
            app (App): the app to be checked
            config (ConfigurationProxy|MergedConfigurationProxy): a set of configuration to be checked

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_config` has not been implemented")

    def check_data(self, app, file_view):
        """Use this method to check files across default and the merged view using the same logic
           for each.
           This is called at most twice:
             1) With the `file_view` argument equal to a `FileView` representing the files within
                `<app>/default/data` if `depends_on_data` is specified AND at least one of the files
                or directory paths specified in `depends_on_config` exists within `<app>/default/data`
             2) With the `file_view` argument equal to a `MergedFileView` representing the merged
                view of files within `<app>/default/data` and `<app>/local/data` if `depends_on_data`
                is specified AND at least one of the files or directory paths specified in
                `depends_on_config` exists within `<app>/[default|local]/data`

        Args:
            app (App): the app to be checked
            file_view (FileView|MergedFileView): a set of files from the `data` directories to be checked

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_data` has not been implemented")

    def check_default_config(self, app, config):
        """Use this method to provide logic to check configs specific to
           the `<app>/default` directory. This is called at most once with
           the `config` argument equal to a `ConfigurationProxy` representing
           the default configuration if `depends_on_config` is specified AND
           at least one of the configs in `depends_on_config` exists within
           `<app>/default/<config>.conf`

        Args:
            app (App): the app to be checked
            config (ConfigurationProxy): configuration loaded from default/

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_default_config` has not been implemented")

    def check_default_data(self, app, file_view):
        """Use this method to provide logic to check file paths specific
           to the `<app>/default/data` directory.|This is called at most
           once with the `file_view` argument equal to a `FileView`
           representing the files within `<app>/default/data` if
           `depends_on_data` is specified AND at least one of the files
           or directory paths specified in `depends_on_config` exists
           within `<app>/default/data`

        Args:
            app (App): the app to be checked
            file_view (FileView): files located in default/data/

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_default_data` has not been implemented")

    def check_merged_config(self, app, config):
        """Use this method to provide logic to check configurations of the
           `<app>/default/<config>.conf` and `<app>/local/<config>.conf`.
           This is called at most once with the `config` argument equal to
           a `MergedConfigurationProxy` representing the merged configuration
           of local and default if `depends_on_config` is specified AND at least
           one of the configs in `depends_on_config` exists within
           `<app>/[default|local]/<config>.conf`

        Args:
            app (App): the app to be checked
            config (MergedConfigurationProxy): result of layering configurations from local
                over configurations from default

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_merged_config` has not been implemented")

    def check_merged_data(self, app, file_view):
        """Use this method to provide logic to check file views of the `<app>/default/data`
           and `<app>/local/data` directories.|This is called at most once with the
           `file_view` argument equal to a `MergedFileView` representing the merged view of
           files within `<app>/default/data` and `<app>/local/data` if `depends_on_data` is
           specified AND at least one of the files or directory paths specified in
           `depends_on_config` exists within `<app>/[default|local]/data`

        Args:
            app (App): the app to be checked
            file_view (MergedFileView): a set of files in {default,local}/data to be checked

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_merged_data` has not been implemented")

    def check_local_config(self, app, config):
        """Use this method to provide logic to check configs specific to
           the `<app>/local` directory.|This is called at most once with
           the `config` argument equal to a `ConfigurationProxy` representing
           the local configuration if `depends_on_config` is specified AND at
           least one of the configs in `depends_on_config` exists within
           `<app>/local/<config>.conf`

        Args:
            app (App): the app to be checked
            config (ConfigurationProxy): configuration loaded from local/

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_local_config` has not been implemented")

    def check_local_data(self, app, file_view):
        """Use this method to provide logic to check file paths specific to the
           `<app>/local/data` directory.|This is called at most once with the
           `file_view` argument equal to a `FileView` representing the files within
           `<app>/local/data` if `depends_on_data` is specified AND at least one of
           the files or directory paths specified in `depends_on_config` exists within
           `<app>/local/data`

        Args:
            app (App): the app to be checked
            file_view (FileView): files located in local/data/

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_local_data` has not been implemented")

    def check_lookups(self, app, file_view):
        """This method will be called once if ANY files exist in the lookups/ directory.
           If either `check_lookups` or `check_lookup_file` is defined but no `lookups/`
           directory is present within the app a NotApplicableMessage will automatically
           be `yield`ed

        Args:
            app (App): the app to be checked
            file_view (FileView): files located in lookups/

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_lookups` has not been implemented")

    def check_lookup_file(self, app, path_in_app):
        """This method will be called once for each lookup in the lookups/ directory.
           If either `check_lookups` or `check_lookup_file` is defined but no `lookups/`
           directory is present within the app a NotApplicableMessage will automatically
           be `yield`ed

        Args:
            app (App): the app to be checked
            path_in_app (str): a relative path to a lookup file to be checked

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_lookup_file` has not been implemented")

    def check_metadata_files(self, app, file_view):
        """This method will be called once if ANY files exist in the metadata/ directory.
           If either `check_metadata_files` or `check_metadata_file` is defined but no
           `metadata/` directory is present within the app a NotApplicableMessage will
           automatically be `yield`ed

        Args:
            app (App): the app to be checked
            file_view (FileView): files located in metadata/

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_metadata_files` has not been implemented")

    def check_metadata_file(self, app, path_in_app):
        """This method will be called once for each file in the metadata/ directory.
           If either `check_metadata_files` or `check_metadata_file` is defined but no
           `metadata/` directory is present within the app a NotApplicableMessage will
           automatically be `yield`ed

        Args:
            app (App): the app to be checked
            path_in_app (str): a relative path to a metadata file to be checked

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_metadata_file` has not been implemented")

    def check_static_files(self, app, file_view):
        """This method will be called once if ANY files exist in the static/ directory.
           If either `check_static_files` or `check_static_file` is defined but no
           `static/` directory is present within the app a NotApplicableMessage will
           automatically be `yield`ed

        Args:
            app (App): the app to be checked
            file_view (FileView): files located in static/

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_static_files` has not been implemented")

    def check_static_file(self, app, path_in_app):
        """This method will be called once for each file in the static/ directory.
           If either `check_static_files` or `check_static_file` is defined but no
           `static/` directory is present within the app a NotApplicableMessage will
           automatically be `yield`ed

        Args:
            app (App): the app to be checked
            path_in_app (str): a relative path to a static file to be checked

        Yields:
            Subclass of CheckMessage depending on the result"""
        raise NotImplementedError("Method `check_static_file` has not been implemented")

    @staticmethod
    def depends_on_files(
        basedir="",
        excluded_dirs=None,
        types=None,
        names=None,
        excluded_types=None,
        excluded_bases=None,
        recurse_depth=float("inf"),
        not_applicable_message=None,
    ):
        """This method is used to decorate custom check methods which are tied to the existence
        of arbitrary files.

        Args:
            not_applicable_message (str): the message used to generate a NotApplicableMessage if
                                          no matching files are found.

            See App.iterate_files for other args

        Returns:
            A decorator that will set attributes on the decorated method"""

        def decorator(func):
            @functools.wraps(func)
            def check_method(self, app):
                files = list(
                    app.iterate_files(
                        basedir=basedir,
                        excluded_dirs=excluded_dirs,
                        types=types,
                        names=names,
                        excluded_types=excluded_types,
                        excluded_bases=excluded_bases,
                        recurse_depth=recurse_depth,
                    )
                )
                if not files:
                    return False, []

                return True, itertools.chain(
                    *(func(self, app, os.path.join(directory, filename)) for (directory, filename, _) in files)
                )

            check_method.is_check_method = True
            check_method.not_applicable_message = not_applicable_message
            return check_method

        return decorator

    @staticmethod
    def depends_on_matching_files(
        patterns,
        basedir="",
        excluded_dirs=None,
        types=None,
        names=None,
        excluded_types=None,
        excluded_bases=None,
        recurse_depth=float("inf"),
        not_applicable_message=None,
    ):
        """This method is used to decorate custom check methods which are tied to the existence
        of arbitrary files that match one or more regular expressions.

        Args:
            not_applicable_message (str): the message used to generate a NotApplicableMessage if
                                          no matching files are found.

            See App.search_for_patterns for other args

        Returns:
            A decorator that will set attributes on the decorated method"""

        def match_to_check_method_args(match):
            (relative_file_ref_output, file_match) = match
            relative_filepath, line_number = relative_file_ref_output.rsplit(":", 1)
            return (relative_filepath, int(line_number), file_match)

        def decorator(func):
            @functools.wraps(func)
            def check_method(self, app):
                files = app.search_for_patterns(
                    patterns,
                    basedir=basedir,
                    excluded_dirs=excluded_dirs,
                    types=types,
                    names=names,
                    excluded_types=excluded_types,
                    excluded_bases=excluded_bases,
                    recurse_depth=recurse_depth,
                )
                if not files:
                    return False, []

                # search_for_patterns returns a tuple of (relative_file_ref_output, file_match)
                # - relative_file_ref_output is f"{relative_filepath}:{line_number}"
                # - file_match is the match object from re.finditer
                # we need to extract the file_path and line_number to pass into the check method
                # instead of making check methods do that themselves. that's what match_to_check_method_args
                # does.
                files = map(match_to_check_method_args, files)

                return True, itertools.chain(
                    *(
                        func(self, app, relative_filepath, line_number, file_match)
                        for (relative_filepath, line_number, file_match) in files
                    )
                )

                # for (relative_file_ref_output, file_match) in files:
                #     relative_filepath, line_number = relative_file_ref_output.rsplit(":", 1)
                #     yield from func(self, app, relative_filepath, line_number, file_match) or []

                # return True, itertools.chain(
                #     func(self, app, os.path.join(directory, filename)) for (directory, filename, _) in files
                # )

            check_method.is_check_method = True
            check_method.not_applicable_message = not_applicable_message
            return check_method

        return decorator

    @classmethod
    def disallowed_config_stanza_patterns(
        cls,
        conf_file,
        patterns,
        tags,
        check_name,
        check_description,
        reporter_action=FailMessage,
        message=None,
        reason=None,
        remediation=None,
        cert_min_version=None,
        cert_max_version=None,
        exceptions_predicate=None,
        module=None,
    ):
        """Helper method to produce Check classes that simply check for the presence of one of
        several forbidden stanzas in a given config file.

        Args:
            conf_file (str): name of configuration file (without `.conf`) where `stanzas` are
                prohibited
            stanzas (:obj:`list` of :obj:`re.Pattern`): list of regex patterns matching prohibited
                stanzas
            tags (:obj:`list` of :obj:`str`): tags where this check should apply
            check_name (str): name of the check as reported to consumers
            check_description (str): a description of what the check does
            reporter_action (:obj:`CheckMessage`): messages that may be yielded by Checks
            message (str): message given to CheckMessage
            reason (str): reason for notification to be passed to user if matching stanza exists
            remediation (str): remediation given to CheckMessage
            cert_min_version (:obj:`str`, optional): Minimum certification version where this
                check applies, parsed as a semantic version number. Defaults to None
            cert_max_version (:obj:`str`, optional): Maximum certification version where this
                check applies, parsed as a semantic version number. Defaults to None
            exceptions_predicate(:obj:`callable`): An optional function that takes one argument
                (the `app` object being inspected) and returns True/False. If it returns True, the
                check is considered a success. Defaults to None

        Returns:
            Subclass of Check (not an instance) that looks for prohibited configuration stanzas"""

        if message is None:
            message = "{file_name} contains a [{stanza}] stanza, which is not allowed in Splunk Cloud."

        if reason:
            message = f"{message} Details: {reason}"

        if remediation is None:
            remediation = "Remove the [{stanza}] stanza"

        class DisallowedConfigStanzaPatternCheck(Check):
            def __init__(self):
                super().__init__(
                    config=CheckConfig(
                        name=check_name,
                        description=check_description,
                        cert_min_version=cert_min_version,
                        cert_max_version=cert_max_version,
                        tags=tags,
                        depends_on_config=(conf_file,),
                    )
                )

            def check_config(self, app, config):
                if callable(exceptions_predicate) and exceptions_predicate(app):
                    return

                for stanza in config[conf_file].section_names():
                    if not any(pattern.match(stanza) for pattern in patterns):
                        continue

                    section = config[conf_file][stanza]
                    yield reporter_action(
                        message.format(
                            stanza=section.name,
                            file_name=section.get_relative_path(),
                            line_number=section.get_line_number(),
                        ),
                        file_name=section.get_relative_path(),
                        line_number=section.get_line_number(),
                        remediation=remediation.format(
                            stanza=section.name,
                            file_name=section.get_relative_path(),
                            line_number=section.get_line_number(),
                        ),
                    )

        # Get the module where this method was called, rather than using this module
        if module is None:
            module = inspect.getmodule(inspect.stack()[1][0])
        DisallowedConfigStanzaPatternCheck.__module__ = module

        return DisallowedConfigStanzaPatternCheck

    @classmethod
    def disallowed_config_stanza_pattern(
        cls,
        conf_file,
        pattern,
        tags,
        check_name,
        check_description,
        reporter_action=FailMessage,
        message=None,
        reason=None,
        remediation=None,
        cert_min_version=None,
        cert_max_version=None,
        exceptions_predicate=None,
    ):
        """Helper method to produce Check classes that simply check for the presence of one of
        several forbidden stanzas in a given config file. See Check.disallowed_config_stanza_patterns for arg
        names and descriptions.

        Returns:
            Subclass of Check (not an instance) that looks for a prohibited configuration stanza"""

        DisallowedConfigStanzaPatternCheck = cls.disallowed_config_stanza_patterns(
            conf_file,
            [pattern],
            tags,
            check_name=check_name,
            check_description=check_description,
            reporter_action=reporter_action,
            message=message,
            reason=reason,
            remediation=remediation,
            cert_min_version=cert_min_version,
            cert_max_version=cert_max_version,
            exceptions_predicate=exceptions_predicate,
            module=inspect.getmodule(inspect.stack()[1][0]),
        )

        return DisallowedConfigStanzaPatternCheck

    @classmethod
    def disallowed_config_stanzas(
        cls,
        conf_file,
        stanzas,
        tags,
        check_name,
        check_description=None,
        reporter_action=FailMessage,
        message=None,
        reason=None,
        remediation=None,
        cert_min_version=None,
        cert_max_version=None,
        exceptions_predicate=None,
        module=None,
    ):
        """Helper method to produce Check classes that simply check for the presence of one of
        several forbidden stanzas in a given config file.

        Args:
            conf_file (str): name of configuration file (without `.conf`) where `stanzas` are
                prohibited
            stanzas (:obj:`list` of :obj:`str`): list of configuration stanzas that are
                prohibited
            tags (:obj:`list` of :obj:`str`): tags where this check should apply
            check_name (str): name of the check as reported to consumers
            check_description (str): a description of what the check does
            reporter_action (:obj:`CheckMessage`): messages that may be yielded by Checks
            message (str): message given to CheckMessage
            reason (str): reason for notification to be passed to user if matching stanza exists
            remediation (str): remediation given to CheckMessage
            cert_min_version (:obj:`str`, optional): Minimum certification version where this
                check applies, parsed as a semantic version number. Defaults to None
            cert_max_version (:obj:`str`, optional): Maximum certification version where this
                check applies, parsed as a semantic version number. Defaults to None
            exceptions_predicate(:obj:`callable`): An optional function that takes one argument
                (the `app` object being inspected) and returns True/False. If it returns True, the
                check is considered a success. Defaults to None

        Returns:
            Subclass of Check (not an instance) that looks for prohibited configuration stanzas"""

        if check_description is None:
            check_description = f"Check for disallowed stanzas in {conf_file}.conf."

        if message is None:
            message = "{file_name} contains a [{stanza}] stanza, which is not allowed in Splunk Cloud."

        if reason:
            message = f"{message} Details: {reason}"

        if remediation is None:
            remediation = "Remove the [{stanza}] stanza"

        class DisallowedConfigStanzaCheck(Check):
            def __init__(self):
                super().__init__(
                    config=CheckConfig(
                        name=check_name,
                        description=check_description,
                        cert_min_version=cert_min_version,
                        cert_max_version=cert_max_version,
                        tags=tags,
                        depends_on_config=(conf_file,),
                    )
                )

            def check_config(self, app, config):
                if callable(exceptions_predicate) and exceptions_predicate(app):
                    return

                for stanza in stanzas:
                    if not config[conf_file].has_section(stanza):
                        continue

                    section = config[conf_file][stanza]
                    yield reporter_action(
                        message.format(
                            stanza=section.name,
                            file_name=section.get_relative_path(),
                            line_number=section.get_line_number(),
                        ),
                        file_name=section.get_relative_path(),
                        line_number=section.get_line_number(),
                        remediation=remediation.format(
                            stanza=section.name,
                            file_name=section.get_relative_path(),
                            line_number=section.get_line_number(),
                        ),
                    )

        # Get the module where this method was called, rather than using this module
        if module is None:
            module = inspect.getmodule(inspect.stack()[1][0])
        DisallowedConfigStanzaCheck.__module__ = module

        return DisallowedConfigStanzaCheck

    @classmethod
    def disallowed_config_stanza(
        cls,
        conf_file,
        stanza,
        tags,
        check_name=None,
        check_description=None,
        reporter_action=FailMessage,
        message=None,
        reason=None,
        remediation=None,
        cert_min_version=None,
        cert_max_version=None,
        exceptions_predicate=None,
    ):
        """Helper method to produce Check classes that simply check for the presence of a
        forbidden stanza in a given config file. See Check.disallowed_config_stanzas for arg
        names and descriptions.

        Returns:
            Subclass of Check (not an instance) that looks for a prohibited configuration stanza"""

        if check_name is None:
            check_name = f"check_for_disallowed_{stanza}_in_{conf_file}_conf"

        if check_description is None:
            check_description = f"Check that {conf_file}.conf does not contain a `[{stanza}]` stanza"

        DisallowedConfigStanzaCheck = cls.disallowed_config_stanzas(
            conf_file,
            [stanza],
            tags,
            check_name=check_name,
            check_description=check_description,
            reporter_action=reporter_action,
            message=message,
            reason=reason,
            remediation=remediation,
            cert_min_version=cert_min_version,
            cert_max_version=cert_max_version,
            exceptions_predicate=exceptions_predicate,
            module=inspect.getmodule(inspect.stack()[1][0]),
        )

        return DisallowedConfigStanzaCheck

    @classmethod
    def disallowed_config_file(
        cls,
        conf_file,
        tags,
        check_name=None,
        check_description=None,
        reporter_action=FailMessage,
        message=None,
        reason=None,
        remediation=None,
        cert_min_version=None,
        cert_max_version=None,
        exceptions_predicate=None,
        module=None,
    ):
        """Helper method to produce Check classes that simply check for the presence of a
         a given config file.

        Args:
            conf_file (str): name of configuration file (without `.conf`) where `stanza` is
                prohibited
            tags (:obj:`list` of :obj:`str`): tags where this check should apply
            check_name (str): name of the check as reported to consumers
            check_description (str): a description of what the check does
            reporter_action (:obj:`CheckMessage`): messages that may be yielded by Checks
            message (str):  messages formatting of reporter yielded
            reason (str): reason for notification to be passed to user if matching stanza exists
            remediation (str): remediation given to CheckMessage
            cert_min_version (:obj:`str`, optional): Minimum certification version where this
                check applies, parsed as a semantic version number. Defaults to None
            cert_max_version (:obj:`str`, optional): Maximum certification version where this
                check applies, parsed as a semantic version number. Defaults to None
            exceptions_predicate(:obj:`callable`): An optional function that takes one argument
                (the `app` object being inspected) and returns True/False. If it returns True, the
                check is considered a success. Defaults to None


        Returns:
            Subclass of Check (not an instance) that looks for prohibited configuration file"""

        if check_name is None:
            check_name = f"check_{conf_file}_conf_does_not_exist"

        if check_description is None:
            check_description = f"Check that the app does not create {conf_file}."

        if message is None:
            message = "App contains {file_name}, which is not allowed in Splunk Cloud."

        if reason:
            message = f"{message} Details: {reason}"

        if remediation is None:
            remediation = "Remove {file_name} from your app."

        class DisallowedConfigFileCheck(Check):
            def __init__(self):
                super().__init__(
                    config=CheckConfig(
                        name=check_name,
                        description=check_description,
                        cert_min_version=cert_min_version,
                        cert_max_version=cert_max_version,
                        tags=tags,
                        depends_on_config=(conf_file,),
                    )
                )

            def check_config(self, app, config):
                if callable(exceptions_predicate) and exceptions_predicate(app):
                    return

                if conf_file in config:
                    yield reporter_action(
                        message.format(file_name=config[conf_file].get_relative_path()),
                        file_name=config[conf_file].get_relative_path(),
                        remediation=remediation.format(file_name=config[conf_file].get_relative_path()),
                    )

        # Get the module where this method was called, rather than using this module
        if module is None:
            module = inspect.getmodule(inspect.stack()[1][0])
        DisallowedConfigFileCheck.__module__ = module

        return DisallowedConfigFileCheck


@dataclass
class CheckConfig:
    """Data class holding configuration for a given Check

    Attributes:
        name (str): Name of the check as reported to consumers
        description (str): A description of what the check does
        cert_min_version (str): Minimum certification version where this check applies,
            parsed as a semantic version number
        cert_max_version (str): Maximum certification version where this check applies,
            parsed as a semantic version number
        tags (:obj:`list` of :obj:`str`): List of tags where this check should apply
        report_display_order (int): Allows specifying an order for checks to appear within a group
        depends_on_config (:obj:`list` of :obj:`str`): A list of configuration file names (without
            `.conf`) that are required for certain check methods to apply. If none of the file names
            exist, the `Check.check*_config()` methods are not run and a `not_applicable` result is
            returned
        depends_on_data (:obj:`list` of :obj:`str`): A list of paths -- file names or directories --
            that are required to exist in one of the data directories for certain check methods to
            apply. If none of the paths exist, the `Check.check*_data` methods are not run and a
            `not_applicable` result is returned
    """

    name: str = None
    description: str = None
    cert_min_version: str = None
    cert_max_version: str = None
    tags: Sequence[str] = None
    report_display_order: int = None
    depends_on_config: Sequence[str] = None
    depends_on_data: Sequence[str] = None
