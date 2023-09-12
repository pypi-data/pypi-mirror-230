# -*- coding: utf-8 -*-
"""Interfaces for accessing files in a consistent manner

The ``FileView`` class provides an interface for interacting with an app or
one of its subdirectories at the file level. The ``MergedFileView`` class
provides the same interface, but will merge two subdirectories in order of
precedence. ``MergedFileView`` can be used, for example, to interact with
the default/data and local/data directories together, the way Splunk would
apply merging precedence.
"""

import os


class FileView:
    """View of a single app or one of its subdirectories

    Args:
        app (App): the app for which a view is provided
        basedir (str, optional): a subdirectory within the app to limit
            scope"""

    def __init__(self, app, basedir=None):
        self.app = app
        if basedir:
            self.basedir = os.path.join(basedir, "")
        else:
            self.basedir = ""

    @property
    def app_dir(self):
        """str: The root directory of the underlying app"""
        if hasattr(self.app, "app_dir"):
            return self.app.app_dir
        return self.app

    def __getitem__(self, name):
        path_in_app = os.path.join(self.basedir, name)
        if name not in self:
            raise KeyError(name)
        if os.path.isdir(os.path.join(self.app_dir, path_in_app)):
            return FileView(self.app, path_in_app)
        return path_in_app

    def has_matching_files(
        self,
        basedir="",
        excluded_dirs=None,
        types=None,
        excluded_types=None,
        excluded_bases=None,
        recurse_depth=float("inf"),
        base_depth=None,
    ):
        """Checks for files in the app / directory, optionally filtered by file
        extension.

        Example:

        if not file_view.has_matching_files(types=['.gif', '.jpg']):
            reporter.not_applicable(...)

        See FileView.iterate_files for param meaning
        """
        matching_files = self.iterate_files(
            basedir=basedir,
            excluded_dirs=excluded_dirs,
            types=types,
            excluded_types=excluded_types,
            excluded_bases=excluded_bases,
            recurse_depth=recurse_depth,
            base_depth=base_depth,
        )
        if next(matching_files, None):
            return False
        return True

    def iterate_files(
        self,
        basedir="",
        excluded_dirs=None,
        types=None,
        excluded_types=None,
        excluded_bases=None,
        recurse_depth=float("inf"),
        base_depth=None,
    ):
        """Iterates through each of the files in the app, optionally filtered
        by file extension.

        Example:

        for file in file_view.iterate_files(types=['.gif', '.jpg']):
            pass

        This should be considered to only be a top down traversal/iteration.
        This is because the filtering of directories, and logic used to track
        depth are based on the os.walk functionality using the argument of
        `topdown=True` as a default value. If bottom up traversal is desired
        then a separate function will need to be created.

        :param basedir The directory or list of directories to start in
        :param excluded_dirs These are directories to exclude when iterating.
            Exclusion is done by directory name matching only. This means if you
            exclude the directory 'examples' it would exclude both `examples/`
            and `default/examples`, as well as any path containing a directory
            called `examples`.
        :param types An array of types that the filename should match
        :param excluded_types An array of file extensions that should be
            skipped.
        :param excluded_bases An array of file names (without extensions)
            that should be skipped.
        :param recurse_depth This is used to indicate how deep you want
            traversal to go. 0 means do no recurse, but return the files at the
            directory specified.
        :param base_depth For recursion, indicates the starting depth
        """

        if not os.path.exists(os.path.join(self.app_dir, self.basedir, basedir)):
            return

        base_depth = base_depth or self.basedir.count(os.path.sep)

        subviews = []

        for name in os.listdir(os.path.join(self.app_dir, self.basedir, basedir)):
            path_in_app = os.path.join(self.basedir, basedir, name)
            full_path = os.path.join(self.app_dir, path_in_app)
            current_depth = os.path.join(path_in_app, "").count(os.path.sep) - base_depth
            if os.path.isdir(full_path):
                if excluded_dirs and name in excluded_dirs:
                    continue
                if current_depth > recurse_depth:
                    continue
                subview = FileView(self.app, path_in_app)
                subviews.append(subview)
            else:
                (filebase, ext) = os.path.splitext(name)
                if types and ext not in types:
                    continue
                if excluded_types and ext != "" and ext in excluded_types:
                    continue
                if excluded_bases and filebase.lower() in excluded_bases:
                    continue
                yield os.path.join(os.path.dirname(path_in_app), ""), name, ext

        for subview in subviews:
            yield from subview.iterate_files(
                basedir="",
                excluded_dirs=excluded_dirs,
                types=types,
                excluded_types=excluded_types,
                excluded_bases=excluded_bases,
                recurse_depth=recurse_depth,
                base_depth=base_depth,
            )

    def get_filepaths_of_files(self, basedir="", excluded_dirs=None, filenames=None, types=None):
        excluded_dirs = excluded_dirs or []
        filenames = filenames or []
        types = types or []

        for directory, file, _ in self.iterate_files(
            basedir=basedir, excluded_dirs=excluded_dirs, types=types, excluded_types=[]
        ):
            current_file_full_path = os.path.join(self.app_dir, directory, file)
            current_file_relative_path = os.path.join(directory, file)
            split_filename = os.path.splitext(file)
            filename = split_filename[0]
            check_filenames = len(filenames) > 0

            filename_is_in_filenames = filename not in filenames
            if check_filenames and filename_is_in_filenames:
                pass
            else:
                yield (current_file_relative_path, current_file_full_path)

    def __contains__(self, other):
        return os.path.exists(os.path.join(self.app_dir, self.basedir, other))


class MergedFileView:
    """Merged view of one-or-more directories within an app

    Args:
        views (:obj:`list` of :obj:`FileView`): FileView instances in order of
            precedence"""

    def __init__(self, *views):
        self.views = views

    @property
    def app_dir(self):
        """str: The root directory of the underlying app, based on the first view
        in precedence. Returns None if there are no views"""
        if not self.views:
            return None
        return self.views[0].app_dir

    def __getitem__(self, name):
        views = [view[name] for view in self.views if name in view]
        if len(views) > 0:
            return MergedFileView(*views)
        raise KeyError(name)

    def has_matching_files(
        self,
        basedir="",
        excluded_dirs=None,
        types=None,
        excluded_types=None,
        excluded_bases=None,
        recurse_depth=float("inf"),
    ):
        """See FileView.has_matching_files"""
        matching_files = self.iterate_files(
            basedir=basedir,
            excluded_dirs=excluded_dirs,
            types=types,
            excluded_types=excluded_types,
            excluded_bases=excluded_bases,
            recurse_depth=recurse_depth,
        )
        if next(matching_files, None):
            return False
        return True

    def iterate_files(
        self,
        basedir="",
        excluded_dirs=None,
        types=None,
        excluded_types=None,
        excluded_bases=None,
        recurse_depth=float("inf"),
    ):
        """See FileView.iterate_files"""
        seen = []

        for view in self.views:
            for path, filename, ext in view.iterate_files(
                basedir=basedir,
                excluded_dirs=excluded_dirs,
                types=types,
                excluded_types=excluded_types,
                excluded_bases=excluded_bases,
                recurse_depth=recurse_depth,
            ):
                relpath = os.path.relpath(os.path.join(path, filename), view.basedir)
                if relpath in seen:
                    continue
                seen.append(relpath)
                yield (path, filename, ext)

    def get_filepaths_of_files(self, basedir="", excluded_dirs=None, filenames=None, types=None):
        """See FileView.get_filepaths_of_files"""
        seen = []

        for view in self.views:
            for relative_path, full_path in view.get_filepaths_of_files(
                basedir=basedir,
                excluded_dirs=excluded_dirs,
                filenames=filenames,
                types=types,
            ):
                relpath = os.path.relpath(relative_path, view.basedir)
                if relpath in seen:
                    continue
                seen.append(relpath)
                yield (relative_path, full_path)

    def __contains__(self, other):
        return any([other in view for view in self.views])
