# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk conf file abstraction base module"""
import re


class NoSectionError(Exception):
    """Exception raised when a specified section is not found."""


class NoOptionError(Exception):
    """Exception raised when a specified option is not found in the specified section."""


class DuplicateSectionError(Exception):
    """Exception raised if add_section() is called with the name of a section that is already present."""


class ConfigurationSetting(object):
    def __init__(self, name, value=str, header=None, lineno=None, relative_path=None):
        self.name = name
        self.value = value
        self.header = [] if header is None else header
        self.lineno = lineno
        self.relative_path = relative_path

    def get_relative_path(self):
        return self.relative_path

    def get_line_number(self):
        return self.lineno


class ConfigurationSection(object):
    def __init__(self, name, header=None, lineno=None, relative_path=None):
        self.name = name
        self.header = [] if header is None else header
        self.lineno = lineno
        self.options = dict()
        self.relative_path = relative_path

    def add_option(self, name, value, header=None, lineno=None):
        self.options[name] = ConfigurationSetting(
            name, value, header=header, lineno=lineno, relative_path=self.relative_path
        )

    def has_option(self, optname):
        return optname in self.options

    def has_setting_with_pattern(self, setting_key_regex_pattern):
        setting_key_regex_object = re.compile(setting_key_regex_pattern, re.IGNORECASE)
        for key, _ in iter(self.options.items()):
            if re.search(setting_key_regex_object, key):
                return True
        return False

    def get_option(self, optname):
        if optname in self.options:
            return self.options[optname]

        error_output = f"No option '{optname}' exists in section '{self.name}'"
        raise NoOptionError(error_output)

    def settings_names(self):
        yield from self.options.keys()

    def settings(self):
        yield from self.options.values()

    def settings_with_key_pattern(self, setting_key_regex_pattern):
        setting_key_regex_object = re.compile(setting_key_regex_pattern, re.IGNORECASE)
        for key, value in iter(self.options.items()):
            if re.search(setting_key_regex_object, key):
                yield value

    def items(self):
        return [
            (property_name, configuration_setting.value, configuration_setting.lineno)
            for (property_name, configuration_setting) in iter(self.options.items())
        ]

    def get_relative_path(self):
        return self.relative_path

    def get_line_number(self):
        return self.lineno

    def __getitem__(self, optname):
        return self.get_option(optname)


class MergedConfigurationSection(object):
    """Configuration section that proxies to one or more individual files

    Note:
        This class will apply precedence logic, but otherwise the methods
        here will proxy to the ConfigurationSections that back the instance.

    Args:
        *sections (:obj:`list` of :obj:`ConfigurationSection`): Actual config
            sections loaded from files, in order of precedence"""

    def __init__(self, *sections):
        self.sections = sections

    def add_option(self, name, value, header=None, lineno=None):
        raise NotImplementedError

    def has_option(self, optname):
        return any([section.has_option(optname) for section in self.sections])

    def has_setting_with_pattern(self, setting_key_regex_pattern):
        setting_key_regex_object = re.compile(setting_key_regex_pattern, re.IGNORECASE)
        for key in self.settings_names():
            if re.search(setting_key_regex_object, key):
                return True
        return False

    def get_option(self, optname):
        for section in self.sections:
            if section.has_option(optname):
                return section.get_option(optname)

        error_output = f"No option '{optname}' exists in section '{self.name}'"
        raise NoOptionError(error_output)

    def settings_names(self):
        touched = set()

        for section in self.sections:
            for setting_name in section.settings_names():
                if setting_name not in touched:
                    yield setting_name
                    touched.add(setting_name)

    def settings(self):
        for key in self.settings_names():
            yield self.get_option(key)

    def settings_with_key_pattern(self, setting_key_regex_pattern):
        setting_key_regex_object = re.compile(setting_key_regex_pattern, re.IGNORECASE)
        for key in iter(self.settings_names()):
            if re.search(setting_key_regex_object, key):
                yield self.get_option(key)

    @property
    def name(self):
        return self.sections[-1].name

    @property
    def lineno(self):
        return self.get_line_number()

    @property
    def options(self):
        return {optname: self.get_option(optname) for optname in self.settings_names()}

    def items(self):
        return [
            (property_name, configuration_setting.value, configuration_setting.lineno)
            for (property_name, configuration_setting) in iter(self.options.items())
        ]

    def get_relative_path(self):
        return self.sections[-1].get_relative_path()

    def get_line_number(self):
        return self.sections[-1].get_line_number()

    def __getitem__(self, optname):
        return self.get_option(optname)


class ConfigurationFile(object):
    def __init__(self, name=None, relative_path=None):
        self.headers = []
        self.sects = dict()
        self.errors = []
        self.name = name
        self.relative_path = relative_path

    def set_main_headers(self, header):
        self.headers = header

    def add_error(self, error, lineno, section):
        self.errors.append((error, lineno, section))

    def get(self, sectionname, key):
        if self.has_section(sectionname):
            option = self.sects[sectionname].get_option(key)
            if isinstance(option, ConfigurationSetting):
                return option.value

            error_output = (
                "The option does not exist in the section " f" searched. Section: {key}" f" Option: '{sectionname}'"
            )
            raise NoOptionError(error_output)
        else:
            raise NoSectionError(f"No section '{sectionname}' exists")

    def add_section(self, sectionname, header=None, lineno=None):
        section = ConfigurationSection(sectionname, header=header, lineno=lineno, relative_path=self.relative_path)
        self.sects[sectionname] = section
        return section

    def has_option(self, sectionname, key):
        return self.has_section(sectionname) and self.get_section(sectionname).has_option(key)

    def get_option(self, sectionname, key):
        return self.get_section(sectionname).get_option(key)

    def has_section(self, sectionname):
        return sectionname in self.sects

    def get_section(self, sectionname):
        if sectionname in self.sects:
            return self.sects[sectionname]

        raise NoSectionError(f"No such section: {sectionname}")

    def section_names(self):
        return self.sects.keys()

    def sections(self):
        for _, value in iter(self.sects.items()):
            yield value

    # Returns only sections that have a property that matches a regex pattern
    def sections_with_setting_key_pattern(self, setting_key_regex_pattern, case_sensitive=False):
        flag = 0 if case_sensitive else re.IGNORECASE
        setting_key_regex_object = re.compile(setting_key_regex_pattern, flags=(flag))
        for _, value in iter(self.sects.items()):
            for setting in value.settings():
                if re.search(setting_key_regex_object, setting.name):
                    yield value

    def items(self, sectionname):
        return self.get_section(sectionname).items()

    def build_lookup(self):
        """Build a dictionary from a config file where { sect => [options ...] }."""
        return {sect: [option for option in self.sects[sect].options] for sect in self.sects}

    def get_relative_path(self):
        return self.relative_path

    def __getitem__(self, sectionname):
        return self.get_section(sectionname)

    def __contains__(self, sectionname):
        return self.has_section(sectionname)


class MergedConfigurationFile:
    """Configuration file that proxies to one or more individual files

    Note:
        This class will apply precedence logic, but otherwise the methods
        here will proxy to the ConfigurationFiles that back the instance.

    Args:
        *sections (:obj:`list` of :obj:`ConfigurationFile`): Actual config
            loaded from files, in order of precedence"""

    def __init__(self, *configs):
        self.configs = configs

    def set_main_headers(self, header):
        raise NotImplementedError

    def add_error(self, error, lineno, section):
        raise NotImplementedError

    def get(self, sectionname, key):
        if not self.has_section(sectionname):
            raise NoSectionError(f"No section '{sectionname}' exists")

        for config in self.configs:
            if config.has_option(sectionname, key):
                option = config.get_option(sectionname, key)
                if isinstance(option, ConfigurationSetting):
                    return option.value

        error_output = (
            "The option does not exist in the section " f" searched. Section: {key}" f" Option: '{sectionname}'"
        )
        raise NoOptionError(error_output)

    def add_section(self, sectionname, header=None, lineno=None):
        raise NotImplementedError

    def has_option(self, sectionname, key):
        return any([config.has_option(sectionname, key) for config in self.configs])

    def has_section(self, sectionname):
        return any([config.has_section(sectionname) for config in self.configs])

    def get_section(self, sectionname):
        section_configs = []

        for config in self.configs:
            if config.has_section(sectionname):
                section_configs.append(config[sectionname])

        if len(section_configs) == 0:
            raise NoSectionError(f"No such section: {sectionname}")
        elif len(section_configs) == 1:
            return section_configs[0]

        return MergedConfigurationSection(*section_configs)

    def get_option(self, sectionname, option):
        for config in self.configs:
            if config.has_option(sectionname, option):
                return config.get_option(sectionname, option)

        error_output = f"No option '{option}' exists in section '{sectionname}'"
        raise NoOptionError(error_output)

    def section_names(self):
        touched = []

        for config in self.configs:
            for section_name in config.section_names():
                if section_name not in touched:
                    yield section_name
                    touched.append(section_name)

    def sections(self):
        for sectionname in self.section_names():
            yield self.get_section(sectionname)

    # Returns only sections that have a property that matches a regex pattern
    def sections_with_setting_key_pattern(self, setting_key_regex_pattern, case_sensitive=False):
        flag = 0 if case_sensitive else re.IGNORECASE
        setting_key_regex_object = re.compile(setting_key_regex_pattern, flags=(flag))
        for value in self.sections():
            for setting in value.settings():
                if re.search(setting_key_regex_object, setting.name):
                    yield value

    def items(self, sectionname):
        return self.get_section(sectionname).items()

    def build_lookup(self):
        raise NotImplementedError

    def get_relative_path(self):
        return self.configs[0].get_relative_path()

    def __getitem__(self, sectionname):
        return self.get_section(sectionname)

    def __bool__(self):
        """
        Return False when there are no underlying configs, to make logic like this work:

        conf_file = app.merged_config["server"]
        if not (conf_file and conf_file.has_section("foo")):
            return
        """

        return len(self.configs) > 0


class ConfigurationProxy:
    """A lazy-loader for in-app configuration files

    Args:
        app (App): the app from where configs will be loaded
        basedir (str): a path within the app from where configs will be loaded"""

    def __init__(self, app, basedir):
        self.app = app
        self.basedir = basedir
        self.configs = {}

    def __getitem__(self, conf_file_name):
        """Get a configuration file, loading it from the app if needed.

        Returns:
            ConfigurationFile instance or None if it does not exist"""
        if not self.__contains__(conf_file_name):
            return None

        if not conf_file_name.endswith(".conf"):
            conf_file_name = f"{conf_file_name}.conf"

        if conf_file_name not in self.configs:
            self.configs[conf_file_name] = self.app.get_config(conf_file_name, self.basedir)
        return self.configs[conf_file_name]

    def __contains__(self, conf_file_name):
        """Check for existance of a configuration file in the app

        Returns:
            True if the configuration file exists, False otherwise"""

        if not conf_file_name.endswith(".conf"):
            conf_file_name = f"{conf_file_name}.conf"
        return self.app.file_exists(self.basedir, conf_file_name)


class MergedConfigurationProxy:
    """A lazy-loader for merging configuration files

    Args:
        proxies (:obj:`list` of :obj:`ConfigurationProxy`): a list of ConfigurationProxy
            instances from which configs will be merged"""

    def __init__(self, *proxies):
        self.proxies = proxies

    def __getitem__(self, conf_file_name):
        """Get a merged configuration file using all applicable proxies

        Returns:
            MergedConfigurationFile instance"""
        configs = [proxy[conf_file_name] for proxy in self.proxies if conf_file_name in proxy]
        return MergedConfigurationFile(*configs)

    def __contains__(self, conf_file_name):
        """Check for existance of a configuration file in any of the backing proxies

        Returns:
            True if the configuration file exists in any proxy, False otherwise"""
        return any([conf_file_name in proxy for proxy in self.proxies])
