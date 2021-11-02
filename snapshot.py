#!/usr/bin/env python3
"""
Todo:
    * Snapshot the ``src/shelllogger`` directory into another
      repository.
    * Need ``--dest`` flag for new location for the ``shelllogger``
      directory.
    * Need ``--dry-run`` flag to show but not do.
    * Ensure the ``ShellLogger`` repo is clean first.
    * Ensure the destination repo is clean first.
    * Run ``rsync -cav --delete`` to copy the contents from one place to
      the other.
    * Run ``git add .`` in the new location to stage the new files in
      the new repo.
    * Get the git remote URL from the original repo and the git log for
      the latest commit.
    * Commit in the new repo with a message indicating where the
      snapshot came from.

See Also:
    * https://github.com/sandialabs/compadre/blob/master/scripts/snapshot_into_trilinos.py
    * https://github.com/TriBITSPub/TriBITS/blob/master/tribits/python_utils/SnapshotDir.py
"""
