# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Check for git conflict releated issue
"""
import logging

import splunk_appinspect
from splunk_appinspect.regex_matcher import RegexBundle, RegexMatcher

logger = logging.getLogger(__name__)


class GitMergeConflictRegexInAllFilesMatcher(RegexMatcher):
    def __init__(self):
        secret_patterns = [RegexBundle(r"<<<<<<<\s*\n([\s\S]*)=======\n([\s\S]*?)>>>>>>>")]
        super(GitMergeConflictRegexInAllFilesMatcher, self).__init__(secret_patterns)


@splunk_appinspect.tags(
    "splunk_appinspect", "cloud", "private_app", "private_victoria", "private_classic", "migration_victoria"
)
@splunk_appinspect.cert_version(min="2.37.0")
def check_for_git_merge_conflict_in_app(app, reporter):
    """Check no git merge conflict is present"""

    matcher = GitMergeConflictRegexInAllFilesMatcher()
    for result, file_path, lineno in matcher.match_results_iterator(
        app.app_dir, app.iterate_files(), match_whole_file=True
    ):
        reporter_output = (
            "The following line will be inspected during code review. "
            "A possible git merge conflict found."
            f" Match: {result}"
            f" File: {file_path}"
            f" Line: {lineno}"
        )
        reporter.warn(reporter_output, file_path)
