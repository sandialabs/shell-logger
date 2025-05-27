# CHANGELOG



## v3.0.1 (2025-05-27)

### Continuous integration
* ci: Replace deprecated GitHub Action ([`0461131`](https://github.com/sandialabs/shell-logger/commit/0461131f3cf53fd26c12f23a11f3cd98589bc74d))

### Documentation
* docs: Switch to `project_copyright` ([`a296c1a`](https://github.com/sandialabs/shell-logger/commit/a296c1a56a8ab635c04c5db12f538e886ff57ae2))

  Using this alias means we're no longer overshadowing the `copyright`
  built-in, so we can remove the comment to ignore that Ruff linting rule.

### Patch
* patch: Omit auto-updates from CHANGELOG ([`c5ad075`](https://github.com/sandialabs/shell-logger/commit/c5ad075148d3551f34f3aec9c72e0e489b043b53))

### Refactoring
* refactor: Replace deprecated mktemp ([`65b9807`](https://github.com/sandialabs/shell-logger/commit/65b9807edd2ffefc9da19a851e492da3267f106e))

  With NamedTemporaryFile. See
  https://github.com/sandialabs/shell-logger/security/code-scanning/2.

## v3.0.0 (2025-01-14)

### Refactoring
* refactor!: Rename trace module ([`105318d`](https://github.com/sandialabs/shell-logger/commit/105318d81c88e510bd444e2dccd11b74e351f8f4))

  Ruff A005 detected that the `trace` module was shadowing a built-in. We
  should've noticed this years ago. This commit renames it and the
  classes therein so there's no confusion between what's provided by
  `shell-logger` vs the standard library. It also improves the parity
  between this module and `stats_collectors`, which improves readability
  and eases maintainability.

  Note that this is a (rather unfortunate) breaking change.
* refactor: Fix issue from ruff-pre-commit update ([`bd514f1`](https://github.com/sandialabs/shell-logger/commit/bd514f1fc629fc57a75bc375a80752987be3c5a8))

## v2.0.1 (2024-12-02)

### Patch
* patch: Support Python 3.13 ([`bb7f272`](https://github.com/sandialabs/shell-logger/commit/bb7f272149e2beadd7185f2ba4957d9fbc558eaf))

  Bump the patch version to update the README on PyPI.

## v2.0.0 (2024-12-02)

### Chores
* chore!: Drop support for Python 3.8 ([`e4eb77e`](https://github.com/sandialabs/shell-logger/commit/e4eb77ec1d55df9117a3f6eaf3e307a5fe9f7582))

  * Use type-hinting out of the box in 3.9.
  * Use new dictionary update syntax.
  * Update the CI and docs accordingly.
* chore: Group dependabot updates ([`b2514ba`](https://github.com/sandialabs/shell-logger/commit/b2514bad93518a767a85f4af467ca624b96663c3))

  Run dependabot updates weekly instead of daily, and group them together
  for the different providers (GitHub Actions and pip), to reduce the
  amount of noise in the repository history.
* chore(deps): No longer pin Sphinx version ([`ae35ebb`](https://github.com/sandialabs/shell-logger/commit/ae35ebb548308335baa620c01cefe9bb4406bf94))

  sphinx-rtd-theme has been updated to work with the latest Sphinx
  version.
* chore(deps): Update sphinx requirement from <8.0.0 to <9.0.0 ([`33e0f6f`](https://github.com/sandialabs/shell-logger/commit/33e0f6fd12ba05e6e352301c62010c14abe3388f))

  Updates the requirements on [sphinx](https://github.com/sphinx-doc/sphinx) to permit the latest version.
  - [Release notes](https://github.com/sphinx-doc/sphinx/releases)
  - [Changelog](https://github.com/sphinx-doc/sphinx/blob/master/CHANGES.rst)
  - [Commits](https://github.com/sphinx-doc/sphinx/compare/v0.1.61611...v8.1.0)

  ---
  updated-dependencies:
  - dependency-name: sphinx
    dependency-type: direct:production
  ...

  Signed-off-by: dependabot[bot] <support@github.com>
* chore: Don't have ruff fix PRs ([`16f4eed`](https://github.com/sandialabs/shell-logger/commit/16f4eed297afd49ff1dc4c4a3ed4c5d3c345866a))

  Require a maintainer to make the changes so they're more aware of them.

### Continuous integration
* ci: Harden GitHub Actions ([`156b2bb`](https://github.com/sandialabs/shell-logger/commit/156b2bb09e34a6f71cc30d29b63316806c0c2000))

  Signed-off-by: StepSecurity Bot <bot@stepsecurity.io>

### Documentation
* docs: Update type hint to match the docs/code ([`ee8fdcc`](https://github.com/sandialabs/shell-logger/commit/ee8fdcce4d36087b640f8303d5f303b62979cbf2))

  Sourcery caught that this should be a sequence of tuples, and not just a
  single one.
* docs: Pin Sphinx version ([`6373150`](https://github.com/sandialabs/shell-logger/commit/63731500a53048209fb8faf49d90340e31730588))

  The Sphinx 8.0.0 release poses a problem for the sphinx-rtd-theme, so
  I'm pinning sphinx below 8.0 to get things back up and running.

### Refactoring
* refactor: Use exception instead of return value ([`f9ec075`](https://github.com/sandialabs/shell-logger/commit/f9ec075094fef5032987571d16a68c11917e3672))

  Sourcery suggested using an exception for this unreachable scenario.

### Testing
* test: Remove unnecessary parentheses ([`9fb0adf`](https://github.com/sandialabs/shell-logger/commit/9fb0adfec35156a1e8301369afdb2065f450ea41))

  To align with updated ruff rules.

## v1.0.4 (2024-07-11)

### Patch
* patch: Remove conda-forge badges ([`120b656`](https://github.com/sandialabs/shell-logger/commit/120b6561fdf8ed19c1603a120daeb020b3910988))

## v1.0.3 (2024-07-10)

### Chores
* chore: Remove build artifacts ([`98768ab`](https://github.com/sandialabs/shell-logger/commit/98768ab79253214e48d91dfc610afb6d7b1dc8a8))

  These were accidentally committed in
  0cbf0dfd410dd01e84eece340ac7f42c8cf24da9.

### Patch
* patch: Maintenance mode release ([`fcc6b4b`](https://github.com/sandialabs/shell-logger/commit/fcc6b4b08514af9d4351dd2eb7ff5e4908152ea3))

## v1.0.2 (2024-07-10)

### Bug fixes
* fix: Point to correct PyPI location ([`249a295`](https://github.com/sandialabs/shell-logger/commit/249a295b9cbc6abd5bd6c0f57956c227a82627f7))

  Should have been included in 0cbf0dfd410dd01e84eece340ac7f42c8cf24da9.

### Continuous integration
* ci: Add semantic release workflow & templates ([`f883a81`](https://github.com/sandialabs/shell-logger/commit/f883a81c03792e45b5a06ce01837444c332bc172))

## v1.0.1 (2024-07-10)

### Continuous integration
* ci: Change documentation coverage file name ([`8f62d45`](https://github.com/sandialabs/shell-logger/commit/8f62d4551aef3d2eb079a52e7861df9ed5d81bd1))

### Patch
* patch: Change package name for PyPI ([`0cbf0df`](https://github.com/sandialabs/shell-logger/commit/0cbf0dfd410dd01e84eece340ac7f42c8cf24da9))

  When trying to upload the initial release to PyPI, the upload failed
  with the following error:

  ERROR HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
           The name 'shell-logger' is too similar to an existing project.
           See https://pypi.org/help/#project-name for more information.

  I couldn't determine which existing package had a name that was too
  similar, so I'm hoping appending the owning GitHub organization to the
  end of the name differentiates it sufficiently.

## v1.0.0 (2024-07-10)

### Bug fixes
* fix: Don't call functions in default args ([`08e8830`](https://github.com/sandialabs/shell-logger/commit/08e8830f9492d8c184319357d6beb0948a7db8c0))

  https://docs.astral.sh/ruff/rules/function-call-in-default-argument/

### Chores
* chore: Create separate copyright file ([`984e1ee`](https://github.com/sandialabs/shell-logger/commit/984e1ee4d6868670cfee6365e275ef3a4d96d67c))

  Also correct copyright year.
* chore: Remove flake8 configuration ([`0713fe8`](https://github.com/sandialabs/shell-logger/commit/0713fe8a40c52b4e49271865272c0b86987c816f))
* chore: Indicate that the package is typed ([`ddea83a`](https://github.com/sandialabs/shell-logger/commit/ddea83a5c232f2d325514cd86174b82b0224ca69))
* chore: Indicate Python >= 3.8 supported ([`4d6e826`](https://github.com/sandialabs/shell-logger/commit/4d6e826cb863b1449eb41d0b1dd07e2b1a80ca0f))
* chore: Update .gitignore ([`a131745`](https://github.com/sandialabs/shell-logger/commit/a13174526e8acb1cf2be9c6bd9f8d8f50769ed9d))
* chore: Remove commitizen configuration ([`12649e1`](https://github.com/sandialabs/shell-logger/commit/12649e1e15765021c0a2d7d947cd32a6ac311665))
* chore: Remove commitizen pre-commit hook ([`012cb21`](https://github.com/sandialabs/shell-logger/commit/012cb2139b7716d5bb1f6df6eb309f538ce2e65c))

  In order to enable a faster development workflow, remove the commitizen
  pre-commit hook to allow commits messages that don't adhere to the
  Conventional Commits specification. Commit messages are still checked
  in the Continuous Integration workflow, though, so a branch will need to
  be clean before merging.
* chore: Disable pyupgrade ([`13a27b2`](https://github.com/sandialabs/shell-logger/commit/13a27b2833069143263cb75f803c3fee4ee56a0d))

  Until I have time to come back and deal with all the findings.
* chore: Disable Bandit security analysis ([`bdaac47`](https://github.com/sandialabs/shell-logger/commit/bdaac47ae525af3c98e93fc3413556b2c839f2b9))

  I'll need to revert this and deal with the findings when I have more
  time available.
* chore: Disable warning on mutable class default ([`b2eddf3`](https://github.com/sandialabs/shell-logger/commit/b2eddf38131d1976ba83ba008901ca899a9632d1))

  This is something I'll need to come back and re-evaluate when I have
  more time available.

  https://docs.astral.sh/ruff/rules/mutable-class-default/
* chore: Ignore magic number warnings in HTML utils ([`728874b`](https://github.com/sandialabs/shell-logger/commit/728874b47269a980f47e53cc1c609829dd8a7460))

  The HTML utilities module has a bunch of magic numbers in it for
  converting between SGR codes and HTML. Replacing the magic numbers with
  corresponding constants will be a significant refactoring, so for now,
  just ignore these warnings in this one file.
* chore: Disable certain Pylint findings ([`dd52a94`](https://github.com/sandialabs/shell-logger/commit/dd52a94280dc53b712cce04da3ac0a6509e2f3a6))

  Disable the warning regarding too many arguments or return statements,
  because I don't have time at the moment to refactor to address them.

  * https://docs.astral.sh/ruff/rules/too-many-arguments/
  * https://docs.astral.sh/ruff/rules/too-many-return-statements/
* chore: Allow boolean positional args in some cases ([`a81af8a`](https://github.com/sandialabs/shell-logger/commit/a81af8a806e101fd770d559ff20dd5af322882a5))

  The `os.set_inheritable()` doesn't allow keyword arguments, so we have
  to whitelist it.

  https://docs.astral.sh/ruff/rules/boolean-positional-value-in-call/
* chore: Remove unnecessary shebang line ([`ee138a7`](https://github.com/sandialabs/shell-logger/commit/ee138a72133d59714a3cced17a70356ceae4356e))

  https://docs.astral.sh/ruff/rules/shebang-not-executable/
* chore: Disable `datetime` checks ([`cef4d26`](https://github.com/sandialabs/shell-logger/commit/cef4d2696f72f4d84f5419d36215757707acc66c))

  I'll need to come back at some point and make all the `datetime` objects
  timezone-aware. Ruff produces the following findings:

  * DTZ005 `datetime.datetime.now()` called without a `tz` argument
  * DTZ006 `datetime.datetime.fromtimestamp()` called without a `tz`
    argument
  * DTZ007 Naive datetime constructed using `datetime.datetime.strptime()`
    without %z
* chore: Ignore complexity warning ([`b99056a`](https://github.com/sandialabs/shell-logger/commit/b99056aa92b31561089968dcba800c2871654e15))

  Reducing the complexity will have to be handled later.

  https://docs.astral.sh/ruff/rules/complex-structure/
* chore: Switch to Ruff for linting/formatting ([`b20890e`](https://github.com/sandialabs/shell-logger/commit/b20890e523231d69f0eebcebc6cadd7dced30855))
* chore: Remove YAPF disable flags ([`39fff4e`](https://github.com/sandialabs/shell-logger/commit/39fff4e33a5162bfad344d07ec9af0d9025fcd2a))

  We've transitioned fro YAPF to black for formatting.
* chore: Remove UNIX classifier ([`69927ce`](https://github.com/sandialabs/shell-logger/commit/69927ceddc5fbe65f46384fa42ab15f561428d33))

  For some reason, Pyroma thinks this is a non-standard classifier.
* chore: Enable pyroma pre-commit hook ([`0415cac`](https://github.com/sandialabs/shell-logger/commit/0415cacd5e72081e8adbeecec0159b4d5b864e29))
* chore: Enable pydocstyle pre-commit hook ([`472bfc4`](https://github.com/sandialabs/shell-logger/commit/472bfc4dd9f56abfe217c749c6168ec287aff0e7))
* chore: Enable isort pre-commit hook ([`09f0c46`](https://github.com/sandialabs/shell-logger/commit/09f0c46d8e8e9f86290200f01c2b267d1bb13c21))
* chore: Enable flake8 pre-commit hook ([`76ba088`](https://github.com/sandialabs/shell-logger/commit/76ba08876575fa2cca0a10ca72ceafeba6d0ce83))
* chore: Enable doc8 pre-commit hook ([`cf98d36`](https://github.com/sandialabs/shell-logger/commit/cf98d368342093ab6290504c81f5263832b6e001))
* chore: Enable pygrep pre-commit hooks ([`5aba441`](https://github.com/sandialabs/shell-logger/commit/5aba441cd514422cec015238a3c89a212865dfa6))
* chore: Enable black pre-commit hook ([`f1c5c86`](https://github.com/sandialabs/shell-logger/commit/f1c5c86fa7c3d78cadb8cd24d42292a350d2d1ce))
* chore: Add pre-commit configuration ([`98c4b48`](https://github.com/sandialabs/shell-logger/commit/98c4b484d98ff9632028826a28bc041cc71cd2ab))

  Only enable standard pre-commit hooks to begin with.
* chore: Add PR template ([`6c5e92c`](https://github.com/sandialabs/shell-logger/commit/6c5e92c738fd60529f4704c0e91877ea78503608))
* chore: Update hidden files ([`b6777bf`](https://github.com/sandialabs/shell-logger/commit/b6777bf398fd62c67676b3d959196c1ede5bb763))
* chore: Update `pyproject.toml` ([`837dddf`](https://github.com/sandialabs/shell-logger/commit/837dddf8a9c82acae7bfe3c8f6c7f9134f81da13))
* chore: Change directory structure ([`364d29b`](https://github.com/sandialabs/shell-logger/commit/364d29b20e7ec415366745e5b83ebe619d863e6c))

  Convert this older Python package structure to the one I currently
  prefer.
* chore: Switch GitLab to GitHub issue templates ([`a5febf8`](https://github.com/sandialabs/shell-logger/commit/a5febf8d56a5c827b4252269614e82761258539d))

### Code style
* style: Run `ruff format` on everything ([`49a3972`](https://github.com/sandialabs/shell-logger/commit/49a39728d6c6d713353cacc6abd274bdcfac1015))
* style: Remove unnecessary parentheses ([`8ab3a3a`](https://github.com/sandialabs/shell-logger/commit/8ab3a3ada4b7cdd4eaf7b5b71751808162e37430))

  https://docs.astral.sh/ruff/rules/unnecessary-paren-on-raise-exception/
* style: Improve pathlib usage ([`ae2e630`](https://github.com/sandialabs/shell-logger/commit/ae2e630ebe5da077f0b61d848fb0c1a8df9219b6))

  * https://docs.astral.sh/ruff/rules/os-getcwd/
  * https://docs.astral.sh/ruff/rules/builtin-open/
* style: Adhere to documentation style guide ([`3cb946d`](https://github.com/sandialabs/shell-logger/commit/3cb946d8f74b2e1b2baa5c7ffb14208392675274))
* style: Sort imports ([`a66c3cf`](https://github.com/sandialabs/shell-logger/commit/a66c3cffd8e34e74b6a8604262b6623e232b996c))
* style: Switch to idiomatic type check ([`f47e1bf`](https://github.com/sandialabs/shell-logger/commit/f47e1bfe3b8cbf5680432cd4e8bfff66aa441ae3))
* style: Update files to match black style ([`cd58f9c`](https://github.com/sandialabs/shell-logger/commit/cd58f9ce39b70a04bfaed0473195461e2c2d557b))
* style: Ensure files end with a single blank line ([`41735da`](https://github.com/sandialabs/shell-logger/commit/41735da02e2ae5537f822f901c445e3bbc472ff7))

### Continuous integration
* ci: Add security checks to pre-commit config ([`2350fa4`](https://github.com/sandialabs/shell-logger/commit/2350fa4014429c0bb7a44064b92f4137d57c9846))
* ci: Add Dependabot configuration ([`70ab5cc`](https://github.com/sandialabs/shell-logger/commit/70ab5cc8a527d2b351339e95027f864a20437885))
* ci: Add CodeQL workflow ([`88f1ffc`](https://github.com/sandialabs/shell-logger/commit/88f1ffce60f98d9259f59a572cec6e0ec9a9a6c3))
* ci: Harden workflows ([`c224cda`](https://github.com/sandialabs/shell-logger/commit/c224cda7b3da6d6094e192e133bdcccc824e0db2))
* ci: Turn on pytest ([`ef84007`](https://github.com/sandialabs/shell-logger/commit/ef840070400eb9983fb0ead98018bad1a08d2d63))
* ci: Test on Mac instead of Ubuntu ([`340c589`](https://github.com/sandialabs/shell-logger/commit/340c5890d723744bf368c6632f9270827fb7e41d))

  For some reason, creating a Shell object hangs on Ubuntu.
* ci: Don't check docs spelling ([`2a3d394`](https://github.com/sandialabs/shell-logger/commit/2a3d394d96a076094f147081f30ae326638b1f8d))

  The libenchant library needs to be installed and configured on a Mac,
  and I don't want to mess with that at the moment.
* ci: Test Python 3.12 as well ([`93a9b85`](https://github.com/sandialabs/shell-logger/commit/93a9b85c8c8e8953442a51e0fd8f45b3ac3132ca))
* ci: Add OpenSSF Scorecard workflow ([`68d3dfe`](https://github.com/sandialabs/shell-logger/commit/68d3dfefe8dbfdfdcdd8993c61fdf9f670d1096b))
* ci: Add continuous integration workflow ([`7c22cc7`](https://github.com/sandialabs/shell-logger/commit/7c22cc76c721afcaddb0cf3c0b4ceb91dea1e79b))

  Create two jobs:

  * commits: Ensure we're adhering to the Conventional Commits
    specification.

### Documentation
* docs: Update contributing guidelines ([`2598c88`](https://github.com/sandialabs/shell-logger/commit/2598c88480ee6072c3fc8e0156da55ef4f3f13d5))

  Also add a script to run all the examples.
* docs: Update OpenSSF Best Practices badge ([`c2e1776`](https://github.com/sandialabs/shell-logger/commit/c2e1776ee0a5eeb19420c9229d15adb84880afee))
* docs: Remove unused link ([`f3ed38e`](https://github.com/sandialabs/shell-logger/commit/f3ed38ed7ac14ca19e9e5f91883fe2e9b937fbee))
* docs: Rework Conventional Commits guidelines ([`6ef601f`](https://github.com/sandialabs/shell-logger/commit/6ef601f454ba18d785831177c7ed0c24c0cc9f39))
* docs: Update docstrings ([`f2685ce`](https://github.com/sandialabs/shell-logger/commit/f2685cef1ab13090184d86d7f5a177ae642f9912))

  * https://docs.astral.sh/ruff/rules/fits-on-one-line/
  * https://docs.astral.sh/ruff/rules/no-blank-line-after-function/
  * https://docs.astral.sh/ruff/rules/blank-line-after-summary/
  * https://docs.astral.sh/ruff/rules/ends-in-punctuation/
* docs: Ignore copyright warning ([`e4b421e`](https://github.com/sandialabs/shell-logger/commit/e4b421efa7738e47a88d9d5fc856f4a47ac4342c))

  https://docs.astral.sh/ruff/rules/builtin-variable-shadowing/
* docs: Update examples on main page ([`a09918f`](https://github.com/sandialabs/shell-logger/commit/a09918fb5817dee56ae6334362435090ee2bf001))

  Just change which lines are included. The lines at the top of the
  example files were changed at some point, but the include directives
  weren't updated to match.
* docs: Adopt Conventional Comments ([`6fa7aa7`](https://github.com/sandialabs/shell-logger/commit/6fa7aa7bbf35e5fab58aba7eb3dbf1ea0a79f719))

  Try to encourage effective communication.
* docs: Update badges ([`8651a9f`](https://github.com/sandialabs/shell-logger/commit/8651a9f3c5f2ef0fe6f3123e72fb13aae5ed8374))
* docs: Update link to latest GMS release ([`b08c464`](https://github.com/sandialabs/shell-logger/commit/b08c4648a89ac3ff51f9fdd3fa72359426c486c9))
* docs: Fix typo ([`af1cbf1`](https://github.com/sandialabs/shell-logger/commit/af1cbf180078e981f4bcb23a7424fb25d1a47758))
* docs: Ignore words when checking spelling ([`eaa6649`](https://github.com/sandialabs/shell-logger/commit/eaa6649591a5104b52650bc1527f717dd989eddc))
* docs: Remove todo page ([`343e0ea`](https://github.com/sandialabs/shell-logger/commit/343e0ea129e7cbc04dd6aae87959ecb718462076))
* docs: Warnings as errors ([`d195b9f`](https://github.com/sandialabs/shell-logger/commit/d195b9f6228efd84390d9a9a8c7ae0ecac9589eb))
* docs: Remove bandit badge ([`fb9c508`](https://github.com/sandialabs/shell-logger/commit/fb9c50832c778617c0a9623cbf98b4f3663cd07c))

  Until we turn the bandit pre-commit hook on and deal with all the issues
  found.
* docs: Partially revert 89d88fa5 ([`9051d6e`](https://github.com/sandialabs/shell-logger/commit/9051d6e13a5284006ba68bc20b653b19d77aac6e))

  With the copyright/license info no longer in the docstrings, we can undo
  these changes from 89d88fa5f3eca4c162bc9bf5aad920899b976099 and allow
  Sphinx to automatically document the `html_utilities` module.
* docs: Move copyright/license text to comments ([`33ff463`](https://github.com/sandialabs/shell-logger/commit/33ff4639c4daf75e858e4058e8b4e25f65219cd5))

  In all the source files, move the copyright and license text from the
  module docstring to comments immediately below it. This is to remove
  this text from automatic processing of docstrings when building the
  documentation.
* docs: Update links ([`89d88fa`](https://github.com/sandialabs/shell-logger/commit/89d88fa5f3eca4c162bc9bf5aad920899b976099))

  Update various links after moving `shell-logger` out onto GitHub.
* docs: Add contributor license agreement ([`03472ba`](https://github.com/sandialabs/shell-logger/commit/03472ba03cab619ad57d559bf135537d012d883b))
* docs: Update copyright text in source files ([`2cf4542`](https://github.com/sandialabs/shell-logger/commit/2cf45421282eec087fa28410cd218932e2bbf279))

  Per guidance from Sandia Technology Transfer, the recommended text from
  the Linux Foundation is insufficient for our purposes.
* docs: Add Scot Swan as past contributor ([`03c06d5`](https://github.com/sandialabs/shell-logger/commit/03c06d5e23ddd2015e872ae47f3c97c66870b79e))
* docs: Update ReadTheDocs config ([`60389c5`](https://github.com/sandialabs/shell-logger/commit/60389c57cef6e7df5acb630b78207b6237a54254))
* docs: Prepare for ReadTheDocs ([`a96e8ae`](https://github.com/sandialabs/shell-logger/commit/a96e8ae76cc2476762be77897e16eeb80e786afe))
* docs: Update Markdown files for the move to GitHub ([`f8cf0db`](https://github.com/sandialabs/shell-logger/commit/f8cf0dbe6bf3520d8397ec786b142745f402bb85))

### Refactoring
* refactor: Secure shell script ([`43462de`](https://github.com/sandialabs/shell-logger/commit/43462deb69c0d2dede25d731989c815c98f1c228))
* refactor: Tweak exceptions ([`967493b`](https://github.com/sandialabs/shell-logger/commit/967493b6511bd3ca4793c3ddccc267f9137db751))

  * https://docs.astral.sh/ruff/rules/type-check-without-type-error/
  * https://docs.astral.sh/ruff/rules/verbose-raise/
* refactor: Only import for type-checking ([`e06e26b`](https://github.com/sandialabs/shell-logger/commit/e06e26b7affb1d129532d8a76ff2105430a7c90e))

  https://docs.astral.sh/ruff/rules/typing-only-standard-library-import/
* refactor: Minor simplifications ([`b8533f7`](https://github.com/sandialabs/shell-logger/commit/b8533f7e8fe9b3ffbf5b40e9393312c622fe9273))

  * https://docs.astral.sh/ruff/rules/enumerate-for-loop/
  * https://docs.astral.sh/ruff/rules/if-expr-with-true-false/
  * https://docs.astral.sh/ruff/rules/if-else-block-instead-of-dict-get/
* refactor: Simplify return logic ([`298d05c`](https://github.com/sandialabs/shell-logger/commit/298d05c6a9da003179d1d5252600d6f15f047218))

  * Don't return `None` if it's the only thing returned
    https://docs.astral.sh/ruff/rules/unnecessary-return-none/
  * Don't implicitly return `None`
    https://docs.astral.sh/ruff/rules/implicit-return/
  * Don't assign to a variable immediately before returning it
    https://docs.astral.sh/ruff/rules/unnecessary-assign/
  * Remove unnecessary `else` clauses
    https://docs.astral.sh/ruff/rules/superfluous-else-return/
* refactor: Address magic numbers ([`6a0787c`](https://github.com/sandialabs/shell-logger/commit/6a0787c5d18ed5bc3402ac7490d8893a53327325))

  Create informative variables to replace the magic numbers.

  https://docs.astral.sh/ruff/rules/magic-value-comparison/
* refactor!: Switch some args to keyword-only ([`af677a1`](https://github.com/sandialabs/shell-logger/commit/af677a1156715c579f8b2c34dca105921093fb6d))

  Ruff discovered a number of instances in which boolean arguments were
  being used in functions:

  * https://docs.astral.sh/ruff/rules/boolean-type-hint-positional-argument/
  * https://docs.astral.sh/ruff/rules/boolean-default-value-positional-argument/

  The intent all along was that these (along with any others that had
  default values associated) be keyword-only arguments, but they were not
  denoted as such. This commit remedies that oversight.

  Note that this is a breaking change because it changes the call
  signatures of the `Shell` and `ShellLogger` public classes. To update
  your usage, simply switch from positional to keyword arguments for any
  arguments affected.
* refactor: Save exception messages as variables ([`cb3c78e`](https://github.com/sandialabs/shell-logger/commit/cb3c78e82c9a28b78ce28ef72ad4e8767fca4198))

  * https://docs.astral.sh/ruff/rules/raw-string-in-exception/
  * https://docs.astral.sh/ruff/rules/f-string-in-exception/
* refactor: Remove `setattr` ([`6424816`](https://github.com/sandialabs/shell-logger/commit/64248166446a8df22c356d6575e071e836fc8a4c))

  https://docs.astral.sh/ruff/rules/set-attr-with-constant/
* refactor: Improve exception chaining ([`93054b9`](https://github.com/sandialabs/shell-logger/commit/93054b9187e611d546bfc0261e07ab48ff778603))

  https://docs.astral.sh/ruff/rules/raise-without-from-inside-except/

### Testing
* test: Don't check disk statistics on RHEL ([`a3ff573`](https://github.com/sandialabs/shell-logger/commit/a3ff5734386c15379663b276f94a8dec8dc37005))

  For some reason, the `DiskStatsCollector` appears to not be collecting
  disk statistics at the specified interval on RHEL. Disable these checks
  until there's time to debug the issue.
* test: Use keyword argument in constructor ([`f9bf643`](https://github.com/sandialabs/shell-logger/commit/f9bf64347222c4e4e250302d5f09ef5ad2963e5f))

  Should have been included in af677a1156715c579f8b2c34dca105921093fb6d.
* test: Rename fixture ([`fde870e`](https://github.com/sandialabs/shell-logger/commit/fde870e4388a67a60cdb68cf9c229e4ed9b97c80))

  Prepend the `use_tmpdir` fixture with a leading underscore to indicate
  that it doesn't return anything.

  https://docs.astral.sh/ruff/rules/pytest-missing-fixture-name-underscore/
* test: Currently this job ([`7c22cc7`](https://github.com/sandialabs/shell-logger/commit/7c22cc76c721afcaddb0cf3c0b4ceb91dea1e79b))

  * Checks out the commit
  * Sets up a Python environment
  * Installs the requirements
  * Installs the package
  * Checks documentation spelling and coverage
  * Uninstalls the package

  Note that the unit test suite is not running yet, because it's not
  completely passing. That will be handled soon.

### Unknown
* Add copyright/license info to all source files ([`76a00b5`](https://github.com/sandialabs/shell-logger/commit/76a00b5e09254e15440aeeb57acf87cd1e8a6c4f))
* Add LICENSE.md ([`e49ffbd`](https://github.com/sandialabs/shell-logger/commit/e49ffbd9213afd0dfde4facd56e567a54451506f))
* Add CHANGELOG.md ([`652c9b5`](https://github.com/sandialabs/shell-logger/commit/652c9b55ac15bdcabf45e2f3a54d9528323fb39b))
* Require Conventional Commits ([`02d8773`](https://github.com/sandialabs/shell-logger/commit/02d87736c893e5ffdc25f46969af29a5053c5d4d))
* Fix typo ([`e683a64`](https://github.com/sandialabs/shell-logger/commit/e683a64275d9aef359bad04dc992f530bb8c6593))
* Add CODE_OF_CONDUCT ([`fd08693`](https://github.com/sandialabs/shell-logger/commit/fd086934fb284f2e5838f5293f02289b1ddf6490))
* Add SECURITY.md ([`0d3efc9`](https://github.com/sandialabs/shell-logger/commit/0d3efc99281c901281de579745a9d6a191a616df))
* Add Security issue template ([`3075485`](https://github.com/sandialabs/shell-logger/commit/30754853257f5355464f1b483b833f6f3af100c3))
* Update .gitlab-ci.yml file ([`f1bf887`](https://github.com/sandialabs/shell-logger/commit/f1bf887e662953db53d3160c8d30d8a570dd920d))

  Adjust coverage report syntax for upgrade to GitLab 15.
* Update CONTRIBUTING.md ([`eccab54`](https://github.com/sandialabs/shell-logger/commit/eccab54050a90b93b64d5e75eb6fe0c2815a555a))
* Correct typo in CONTRIBUTING.md ([`33ae7da`](https://github.com/sandialabs/shell-logger/commit/33ae7da45fe70220bd7d3f421f7d839f04508118))
* Fix broken tests ([`31e16b3`](https://github.com/sandialabs/shell-logger/commit/31e16b36ddf1471980d1d924a38fbb870436eafa))
* Fix broken test ([`4f160ac`](https://github.com/sandialabs/shell-logger/commit/4f160ac4b1fba72e813dc881f75dad89357c5e9c))
* Fix style issues ([`11f1dc3`](https://github.com/sandialabs/shell-logger/commit/11f1dc3586182aa426f0007d9836e118ee1bfc34))
* Update YAPF error message ([`55dd0e1`](https://github.com/sandialabs/shell-logger/commit/55dd0e187030e95250841d493c088d0bd06a7fde))
* Alphabetize jobs ([`cf77528`](https://github.com/sandialabs/shell-logger/commit/cf7752862ff604346fac78aee15eddebc8c423a2))
* Alphabetize job specs ([`e298c35`](https://github.com/sandialabs/shell-logger/commit/e298c35ae8acd4a6cafa8bd7689f19371a5afd9d))
* Archive yapf.diff.txt ([`ca6b5ae`](https://github.com/sandialabs/shell-logger/commit/ca6b5ae21536432c47c14b068359b1daef390837))
* Debugging ([`c478aa5`](https://github.com/sandialabs/shell-logger/commit/c478aa5078dbdbdeba08d18836c1474772cdf6cf))
* Tweak ([`156a3e3`](https://github.com/sandialabs/shell-logger/commit/156a3e39c7fde670b51c4249ad1f3caeebbe6528))
* Debugging ([`63a89f6`](https://github.com/sandialabs/shell-logger/commit/63a89f6dbf16d58c9e3094fda2da177e154885a8))
* Add YAPF job ([`c9523d9`](https://github.com/sandialabs/shell-logger/commit/c9523d93422ae1dd8dfa9889d7e4b83538c2fc8e))
* Remove Windows support ([`8a5e08f`](https://github.com/sandialabs/shell-logger/commit/8a5e08f1932e547c86a25e11c6237c78092caef8))

  Follow-on to #12. These changes should have been included
  in e034d0b6c8c1a10616d8d07ea5cae687fc70d263, but were
  accidentally omitted.
* Change file naming scheme (#31) ([`e6ecedd`](https://github.com/sandialabs/shell-logger/commit/e6ecedd47bfad0e9c1ef78001c487e4374b662df))
* Remove Windows support (#12) ([`e034d0b`](https://github.com/sandialabs/shell-logger/commit/e034d0b6c8c1a10616d8d07ea5cae687fc70d263))
* Remove snapshot script ([`ff92fbd`](https://github.com/sandialabs/shell-logger/commit/ff92fbdbe330e0aec83dd761aba6288cb005e448))
* Add notes to script ([`5898817`](https://github.com/sandialabs/shell-logger/commit/5898817bf6463a156684f988f5579da0f87553b3))
* Add instructions to README ([`ee7d56d`](https://github.com/sandialabs/shell-logger/commit/ee7d56de917724a29152df1ba1f4eac47948af59))
* Tweaks to docs ([`7f44ff0`](https://github.com/sandialabs/shell-logger/commit/7f44ff06a1f123aad26c1cedb83cc9618b57ebd5))
* Fix typo in last commit ([`4c343ba`](https://github.com/sandialabs/shell-logger/commit/4c343bafbd48c523d49da66c3099b1847fc4ed83))
* Fix typo in last commit ([`ea707e9`](https://github.com/sandialabs/shell-logger/commit/ea707e90dc1320037f34e42056af5704992453bb))
* Switch `util.py` to `HTMLUtilities.py` ([`4d962a9`](https://github.com/sandialabs/shell-logger/commit/4d962a94781f559a3dfd9abd866241aa0bad4973))
* Switch `classes` to `AbstractMethod` ([`3dc312d`](https://github.com/sandialabs/shell-logger/commit/3dc312d0ada6dd16df663d63d13b77346fc0e748))
* Move `Trace` classes to new file ([`fbe9919`](https://github.com/sandialabs/shell-logger/commit/fbe9919294c8585a33ad1281c8bccd340060aabf))
* Move `StatsCollector` classes to new file ([`2b781a4`](https://github.com/sandialabs/shell-logger/commit/2b781a4b7739c3801650c39e56c2f7ede7bd05a8))
* Move encoder/decoder to bottom of file ([`1557a94`](https://github.com/sandialabs/shell-logger/commit/1557a940f3f57f03f7196c3549a24ff40a62654b))
* Adjust required coverage ([`5eacf33`](https://github.com/sandialabs/shell-logger/commit/5eacf338d6c239ffe66c509ad9ba33a04b8a8e2f))
* Adjust docs for `Shell` movement ([`94da4b1`](https://github.com/sandialabs/shell-logger/commit/94da4b1fba28619961bfe3ef4efc3d94e4b94689))
* Move `Shell` to its own file ([`e84ceca`](https://github.com/sandialabs/shell-logger/commit/e84ceca26e0b0e0b6307da8368666bb96c942986))
* Update README.md ([`6169426`](https://github.com/sandialabs/shell-logger/commit/6169426b8ca148238d985fe0471ea91a6af9e832))
* Preserve newlines and spacing (#27) ([`cee1d80`](https://github.com/sandialabs/shell-logger/commit/cee1d80d3fa62fa6b187aaf503ce0350db3d077d))
* Update javascript after removal of no-break ([`4a4f298`](https://github.com/sandialabs/shell-logger/commit/4a4f2985cea3e9cf2a4aa731607cc6dfc542628f))

  We no longer need to have the javascript search function take out the
  no-break characters since we no longer use them in the first place.
* Remove no-break character (#26) ([`0484662`](https://github.com/sandialabs/shell-logger/commit/0484662dfbf2438e4cfedfacf060ce14ba4ca302))
* Add issue templates (#10) ([`02e69a7`](https://github.com/sandialabs/shell-logger/commit/02e69a76863f6f8af1dead50d17af02a285ae589))
* Add `login_shell` toggle ([`a2d10c9`](https://github.com/sandialabs/shell-logger/commit/a2d10c907673b4b217449a33672965401894ca09))

  Add the ability to optionally spawn a login `Shell` when
  creating a `ShellLogger`. Defaults to `False` to preserve
  existing functionality.
* Downgrade to Python 3.7 ([`040f505`](https://github.com/sandialabs/shell-logger/commit/040f505368ae279199fe3f9f8d117414dd160225))
* Add contributing guidelines (#9) ([`bfd73b2`](https://github.com/sandialabs/shell-logger/commit/bfd73b2fac7214c0ca3dc013adba9f1d9174095f))
* Fill out README.md (#7) ([`ea21b89`](https://github.com/sandialabs/shell-logger/commit/ea21b8965f80521aa8ec99fc620a05608a4995b2))
* Publish example log files via Pages (#17) ([`0206797`](https://github.com/sandialabs/shell-logger/commit/0206797be203f3fcd53036a93f7393f75376209f))

  * Switch from global cache to artifacts for the extras
    getting published via pages
  * Copy example log files to appropriate directory
  * Link to example log files from docs index
* Remove `needs` ([`297d0dc`](https://github.com/sandialabs/shell-logger/commit/297d0dc887acf94d0b611dba196b8bbc8544a836))

  Allow jobs to run serially stage by stage instead.
* `conda list` after uninstall ([`b378543`](https://github.com/sandialabs/shell-logger/commit/b37854326dbdd19cd811c8a7c7ee3817ee14b5b2))
* Fix env name ([`d51c77b`](https://github.com/sandialabs/shell-logger/commit/d51c77b9ad18b63eb03e1ef1f5ca438086b53f25))
* Specify Python 3.8 when creating the environment ([`8bee9d5`](https://github.com/sandialabs/shell-logger/commit/8bee9d5aae65ea8624b2a70794ac011b2c286485))
* Switch from venv to conda ([`650d7f9`](https://github.com/sandialabs/shell-logger/commit/650d7f9482d6a784554b3da1a7569cdd4b82c21f))
* Remove unnecessary uninstall ([`3828ee1`](https://github.com/sandialabs/shell-logger/commit/3828ee1bb8b17faee49b6975217c635d95364b62))
* Change virtual environment name ([`0ac6cb0`](https://github.com/sandialabs/shell-logger/commit/0ac6cb0e13b18789bc6574aa05e1d788877b2dee))
* Rename jobs ([`41b4627`](https://github.com/sandialabs/shell-logger/commit/41b462713364c934d14e4d44255185faab73f90c))
* List the contents of the virtual environment when it's loaded ([`9ee4d7e`](https://github.com/sandialabs/shell-logger/commit/9ee4d7ea4860dbb90f4dfc5f2575f5182d8b09ca))
* Revert "Replace cache with artifacts" ([`28c747c`](https://github.com/sandialabs/shell-logger/commit/28c747cb06f4fcc764217317cb48ff81b93ee72e))

  This reverts commit ca232364599c56c766967f4cad3532d5208248d0.
* Add bash versions of the examples (#19) ([`f666c44`](https://github.com/sandialabs/shell-logger/commit/f666c44c0d8fd6685c7999e14c44e70152efb543))

  * Add bash scripts equivalent to `hello_world_html.py` and
    `build_flex.py`.
  * Include them in the documentation home page for comparison
    purposes.
  * Rework example write-up into bulleted list.
* Replace cache with artifacts ([`ca23236`](https://github.com/sandialabs/shell-logger/commit/ca232364599c56c766967f4cad3532d5208248d0))

  It seems storing the virtual environment in the cache was causing
  non-deterministic problems with `shelllogger` sometimes not existing
  in the environment after it was installed. Hopefully using
  artifacts instead of the cache will solve the problem.
* Create examples (#15) ([`c478b3c`](https://github.com/sandialabs/shell-logger/commit/c478b3c8e24800d7ab5e78dd64e39848b6417d3f))

  * Add example scripts demonstrating the usage of
    `ShellLogger`.
  * Add the examples to the documentation, along with
    screenshots of the generated log file.
  * Run the examples in the pipeline to ensure they always
    work.
* Fix CI Stages ([`d36ee93`](https://github.com/sandialabs/shell-logger/commit/d36ee938731843198d321ad9113cdf98f2f08774))

  Make the `pages` job happen in the `deploy` stage (just the way
  GitLab expects it to be), and rename the `deploy` stage `install`.
* Fix Pages Deployment ([`cca72b7`](https://github.com/sandialabs/shell-logger/commit/cca72b78711af2b5d31b4653c6f066b431835d45))

  Lowercase all CI job names. It sounds like the CI job name needs
  to be `pages` (case-sensitive) to tell the GitLab Runner to deploy
  the `public` directory via GitLab Pages.
* Add Sphinx Documentation (#6) ([`1e41edc`](https://github.com/sandialabs/shell-logger/commit/1e41edca6455ca8c12b8b5f6c545ce24ee9e7bd7))

  * Create the infrastructure for generating the Sphinx
    documentation.
  * Add a job to the CI pipeline to build the documentation.
  * Add a documentation badge to the README.md.
  * Fix Sphinx warnings/errors.
* Exclude virtual environment from flake8 ([`dbd41eb`](https://github.com/sandialabs/shell-logger/commit/dbd41eb6864854e74721deefd252292a5fec6da1))
* Add flake8 to testing requirements ([`aded66c`](https://github.com/sandialabs/shell-logger/commit/aded66c5bee9816af3952255f43dcc1d757d80ba))
* Add flake8 CI job ([`b4e97d5`](https://github.com/sandialabs/shell-logger/commit/b4e97d565d3770a0a044c6c93b49a220a29725ea))
* Get flake8 passing ([`a3fd6ba`](https://github.com/sandialabs/shell-logger/commit/a3fd6baef676e7f26a61f88618802d64cfcf3c77))
* Add pytest (#4) ([`6a80d00`](https://github.com/sandialabs/shell-logger/commit/6a80d00cb140ab549e588aae363a732bf945f8ac))

  * Create a GitLab CI pipeline to run pytest
  * Rework the requirements files
  * Loosen tolerances on trace tests
  * Include coverage testing, distribution creation,
    and un/installation
* Fix CaptureFixture type hinting ([`06c7381`](https://github.com/sandialabs/shell-logger/commit/06c7381648ba82e287ed711c0f2bca3fa76b5460))
* Update the test suite; finish work on branch ([`daa36bc`](https://github.com/sandialabs/shell-logger/commit/daa36bc55d907c9dfbc7885bcdf592cccbf7652a))
* Finish updating everything but the test suite ([`2eb3f79`](https://github.com/sandialabs/shell-logger/commit/2eb3f795efec8f1cd3d479ca0bc0da4905ba52e7))
* Finish util.py ([`385860e`](https://github.com/sandialabs/shell-logger/commit/385860e5716c92fc8339046d3b101d7eb3bc88a4))
* Still more util.py WIP ([`d3f4972`](https://github.com/sandialabs/shell-logger/commit/d3f4972bf4aa5bda851b314b76f70328503f026f))
* More util.py WIP ([`1c2f623`](https://github.com/sandialabs/shell-logger/commit/1c2f623018df773935e4e5b5ce611d8e19f1eef6))
* util.py WIP ([`bb4d8e3`](https://github.com/sandialabs/shell-logger/commit/bb4d8e3db69425aff7f1b10e4dd12f4748282e0e))
* Document Trace and StatsCollector subclasses ([`c5cd8ee`](https://github.com/sandialabs/shell-logger/commit/c5cd8eec9567f9e3d9fa2d1a4763e66ae7a58e15))
* Almost done with `classes.py` ([`095acab`](https://github.com/sandialabs/shell-logger/commit/095acabcdb9d962f6d83400271ecdc4b4e90c6aa))
* And some more ([`51d0943`](https://github.com/sandialabs/shell-logger/commit/51d09433131aeed1d0b62e2b8b2d2f2b53bb95c7))
* More WIP ([`2ea5edf`](https://github.com/sandialabs/shell-logger/commit/2ea5edff1acfa7a825c53694aad8f10d278afacc))
* WIP COMMIT ([`709247e`](https://github.com/sandialabs/shell-logger/commit/709247e694e87f95d494e1dc4676877995ed2aad))
* Reformat classes.py ([`41273c9`](https://github.com/sandialabs/shell-logger/commit/41273c9c0e5a5119643f84503c8fc5ef7f22a496))

  * Mostly type hinting and docstrings.
  * The occasional reorganization of a function.
* Reformat ShellLogger.py ([`20d80cc`](https://github.com/sandialabs/shell-logger/commit/20d80ccc03a1850c47f74526f5445be6375220c3))

  * Mostly type hinting and docstrings.
  * The occasional reorganization of a function.
* Add installation files ([`0ec0ce4`](https://github.com/sandialabs/shell-logger/commit/0ec0ce48ce83d5bb27a9501955a5ac8b9f02d0e6))
* Remove unused imports ([`04d5b91`](https://github.com/sandialabs/shell-logger/commit/04d5b91ca3afe6d10ff6fb131afa798ee439f8b0))
* Skip trace test for Darwin ([`4204630`](https://github.com/sandialabs/shell-logger/commit/420463028400ab5705c18570ab41c3164a8df27a))
* Switch from Process().start() and .join() to simple logger.log()s ([`9b641d1`](https://github.com/sandialabs/shell-logger/commit/9b641d1ae42991496bfe4e6637e4a57fa068e575))

  I'm not sure of the motivation for the former method. It was
  causing `TypeError: cannot pickle '_thread.lock' object` errors on
  the `start()`s, but I couldn't figure out why or how to fix it.
* Add `sleep`s to allow time to collect memory/CPU stats ([`b8012ff`](https://github.com/sandialabs/shell-logger/commit/b8012ff038c935e8d08510236e0202bf5feda9ea))
* Use tmpdir for all tests ([`ae1c49e`](https://github.com/sandialabs/shell-logger/commit/ae1c49e867b1676302b0b1528fdebdf36f43e881))
* Adjust `test_stats` ([`8166bdf`](https://github.com/sandialabs/shell-logger/commit/8166bdfba63f6509c1e6943a17522dcc55f0cd8e))
* Skip `ltrace` test on Darwin ([`a2a06ad`](https://github.com/sandialabs/shell-logger/commit/a2a06ad2e36f286d2483163410826876ac0f3331))
* Revert "WIP: Trying to get next test working" ([`760d754`](https://github.com/sandialabs/shell-logger/commit/760d7549bae313da32022c19888c585455826371))

  This reverts commit 89bade69948d10c442328a80ef961b648316fb0a.
* WIP: Trying to get next test working ([`89bade6`](https://github.com/sandialabs/shell-logger/commit/89bade69948d10c442328a80ef961b648316fb0a))

  `test_finalize_creates_html_with_correct_information` is
  failing because the memory and CPU usage aren't getting
  written to the HTML log file, and I can't figure out why.
* Turn on more tests that use the fixture ([`cd52351`](https://github.com/sandialabs/shell-logger/commit/cd52351cd0127acc079dedf44aeac58a46e6cfaf))
* Get first failing test passing ([`72992e5`](https://github.com/sandialabs/shell-logger/commit/72992e5a54a7f5b2b195b8d45e4c7fbd8338cedf))
* Add `shell_logger` fixture ([`45f3d86`](https://github.com/sandialabs/shell-logger/commit/45f3d864615968d231677e50793bad85d64e9f24))

  Accidentally forgot this when I filtered the `ShellLogger`
  history out of the `BuildScripts` repository.
* Add .gitignore ([`65e9c7c`](https://github.com/sandialabs/shell-logger/commit/65e9c7cb49ef886a08842fa18283ed63ca6055bc))
* Skip failing tests for now ([`357783e`](https://github.com/sandialabs/shell-logger/commit/357783e68cdc564250f9035128aac62261c731cd))

  Will re-enable them one at a time and get them passing.
* Rename test with duplicate name ([`b536bab`](https://github.com/sandialabs/shell-logger/commit/b536bab0bdab14c415b5ee59fe492837fb1291d6))
* Lowercase variable names ([`16c81c8`](https://github.com/sandialabs/shell-logger/commit/16c81c822704ae92186f006b7e0c906b37e365ee))
* PEP8 pass ([`3402ed0`](https://github.com/sandialabs/shell-logger/commit/3402ed020ca5752e68ee43482fc2f2f4b61ea0ec))
* Lowercase function names ([`d1a2b87`](https://github.com/sandialabs/shell-logger/commit/d1a2b87beebb32be45709156ca6e11b8ab80ebed))
* Rename class: Logger -> ShellLogger ([`3faf70f`](https://github.com/sandialabs/shell-logger/commit/3faf70f18892a6df5894b49d3dafe39f8234a823))
* Rename directory: logger -> shelllogger ([`be2a76b`](https://github.com/sandialabs/shell-logger/commit/be2a76b7a06fd63b75ebeeead7ee5ac713d039da))
* Add Pycharm configuration ([`196cd41`](https://github.com/sandialabs/shell-logger/commit/196cd41a91298788f487af27830928907ccda4f4))
* Restructure Logger files for conversion to ShellLogger repo ([`60f9c00`](https://github.com/sandialabs/shell-logger/commit/60f9c00354aba86bb276ac6455407cb65450d32c))
* Use fonts in logger whose word joiner is zero width ([`0d71dc8`](https://github.com/sandialabs/shell-logger/commit/0d71dc8fbfe55e4cefcafbfd827d1ac9e51ca1ed))
* Small HTML message tweak ([`3939cde`](https://github.com/sandialabs/shell-logger/commit/3939cde840105fd961d01bb12ea5556aef5610e5))
* Improve logger layout a bit ([`e60a10a`](https://github.com/sandialabs/shell-logger/commit/e60a10afd65be770ab0ac2bb2fdc459a07e02f62))

  * Less blank space
  * Put command at top level
  * Put return code at top level
* Fixed errors in deciding invalid characters from bytes in logger ([`69ad45b`](https://github.com/sandialabs/shell-logger/commit/69ad45bc0779fd9bedd8b0a775b5c0f75ef4bb3f))
* Fixed a bug in logger when commands are provided as arrays. ([`acd2f8b`](https://github.com/sandialabs/shell-logger/commit/acd2f8bc2c9c3d722700a8e1de313aa57266e9a6))

  For example, logger.log("test", ["echo", "'"]) would not work before this
  commit.

  Added a unit test to ensure this works.
* Fixed a logger exception message (missing space) ([`7ac0714`](https://github.com/sandialabs/shell-logger/commit/7ac07148a5b938a6414b29494919aebb8ba52a43))
* Ensure the logger cannot continue running commands after a syntax error. ([`9aea9ef`](https://github.com/sandialabs/shell-logger/commit/9aea9efa05bb26c6348ba9b27f77cf5b6cae2eb4))

  In an interactive python session, we don't want someone reusing the
  logger in the event of a syntax error since the shell is dead.
* Added a guard for syntax errors in logger. ([`1b3758a`](https://github.com/sandialabs/shell-logger/commit/1b3758a13a4b7890b908072e9caa532110a0094c))

  Previously, the logger would hang if there was a syntax error in
  the command provided. Now, logger will just exit, printing an error
  message that the command could not complete.

  Note: if we ever wanted to, we could change the behavior to restart the
  crashed shell by changing the handler for the KeyboardInterrupt exception
  to see if it came from the child thread teeing the shell's stdout/stderr
  or from the user hitting Ctrl+C, restarting the shell in the former case
  and exiting in the later case.
* Quick fix for logger when $SHELL is not in os.environ ([`946e05c`](https://github.com/sandialabs/shell-logger/commit/946e05c60d4cc7d78e6d59ced7fd48be0c312d37))

  There's no requirement for a shell to define the SHELL environment
  variable (see https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_05_03) so we shouldn't rely on that.
* Modified logger HTML creation behavior ([`211077d`](https://github.com/sandialabs/shell-logger/commit/211077d4807e4d82d315ac0126236caeb1f36c7f))

  Logger will no longer destroy the HTML file when appending until finalize()
  is called.
* Added an append mode to the logger to append to previous loggers ([`56b4323`](https://github.com/sandialabs/shell-logger/commit/56b4323a58116c5aa69aef492bcecf852a4a0cf2))
* Adjust search opacity in logger ([`cbfe9a8`](https://github.com/sandialabs/shell-logger/commit/cbfe9a862a86b9ba6093dd91fdc1466bd0a17fde))
* Improved search ([`eec0844`](https://github.com/sandialabs/shell-logger/commit/eec0844c4c6d747154e511e206926c3c6de56233))

  * Added a search button (interactive search-as-you-type is too slow
    for large inputs)
  * Added a "show nearby" option to show lines near a matching line.
* Changed logger output back to table (previously tried grid). ([`4bdda39`](https://github.com/sandialabs/shell-logger/commit/4bdda39edb1c35ad41f7e1447de9604df65287d2))

  The problem with grid layouts is that Chrome only supports a maximum
  of 1000 rows. Since we have one row per line of output, we might
  exceed that number and cause some very strange behavior from Chrome
  and other browsers based off of it (e.g. Edge).

  See:
  https://stackoverflow.com/q/53236054
  https://www.w3.org/TR/css-grid-1/#overlarge-grids
* Prevent logger from trying to use psutil when it isn't installed (e.g. on certain machines) ([`9782e89`](https://github.com/sandialabs/shell-logger/commit/9782e8955807e8304c7ba5402f0b62402e479b85))
* Actually push new files (oops) ([`4a13021`](https://github.com/sandialabs/shell-logger/commit/4a13021e075fd26f191035473d6be717e349883a))
* Put search behind a magnifying glass. ([`77cd05d`](https://github.com/sandialabs/shell-logger/commit/77cd05d16f320f39319c4ad9054823bc48efc797))
* Forgot to add new template file ([`a14b541`](https://github.com/sandialabs/shell-logger/commit/a14b5410dba06d9925bc2edbc0bb087dbd71cc9e))
* Added an html_print to print messages only to the log ([`4ca88d7`](https://github.com/sandialabs/shell-logger/commit/4ca88d7240e0f42c89cfd86c776c72c4cf304667))
* Changed output blocks so that they wrap in logger HTML ([`fd54ec7`](https://github.com/sandialabs/shell-logger/commit/fd54ec79e49cfb0c5d8366e88bea0096566c9f7e))
* Improved templates in logger (indent is specified in the template now) ([`bd12152`](https://github.com/sandialabs/shell-logger/commit/bd1215209acefdd1fdaa59875c916d2dd37e2a4f))
* Stripped out SVG generation from logger. ([`c75fe33`](https://github.com/sandialabs/shell-logger/commit/c75fe336ce919e56791b189874bd15ef5ce81902))
* Refactor sgr_to_html in logger ([`eb8e2c8`](https://github.com/sandialabs/shell-logger/commit/eb8e2c899e505274b5bb9d79bfef994147dfe7be))
* Search now isnored html tags in output boxes ([`45d5b2a`](https://github.com/sandialabs/shell-logger/commit/45d5b2ae25521c51647f17295b9b4807db449667))
* Added SGR (select graphics rendition) to HTML. ([`c60beee`](https://github.com/sandialabs/shell-logger/commit/c60beee317768060693c8ec2dddc86d3cf3d1a1b))

  Some commands like to output color. Unfortunately, this means that
  they use ANSI escape codes to do so which makes things hard to read
  in the HTML output (e.g. you see something like ^[[38;5;196mhello^[[0m
  where you would normally see just "hello" in red).

  TODO: ensure this doesn't break search.
* Re-added redirecting stdin to /dev/null (also made this the default behavior again) ([`f890c63`](https://github.com/sandialabs/shell-logger/commit/f890c63ab9594957977dc9a01bbcde1a952e936d))
* Re-added removal of uninteresting disks in disk stats in logger ([`07fe253`](https://github.com/sandialabs/shell-logger/commit/07fe2530a4ab54c42d549f846a3ca591f429a658))
* Minor tweak to logger HTML ([`5490776`](https://github.com/sandialabs/shell-logger/commit/5490776dd51d9596eaf748a25817dddd75327368))
* More adjustment to the HTML ([`1260b55`](https://github.com/sandialabs/shell-logger/commit/1260b55975f3b31f63fc31ff0a0ef3a2007069e1))
* Templatized logger HTML almost entirely ([`f036b56`](https://github.com/sandialabs/shell-logger/commit/f036b562c4bece350ff77e8e1f3137dfb28dc8b0))
* Templatized child logger log entries in logger ([`4509e96`](https://github.com/sandialabs/shell-logger/commit/4509e96e3aabbe504981f31a1b5e3772bf266aef))
* More templatization in the logger ([`3840138`](https://github.com/sandialabs/shell-logger/commit/3840138fa7528c83660f2405df20b543409bd437))
* Tweak chart in logger ([`26d9ca2`](https://github.com/sandialabs/shell-logger/commit/26d9ca27022c459188b23cfa3af49321bbca2b5e))
* Templatize chart output in logger ([`1afa26b`](https://github.com/sandialabs/shell-logger/commit/1afa26b775322f7687b81e9d15940a12619cecfe))
* Templatize some of the HTML in logger ([`a1629be`](https://github.com/sandialabs/shell-logger/commit/a1629bed322aec1a47f7c628e645a3f70cede4a7))
* Moved extra CSS to resource files ([`512cab0`](https://github.com/sandialabs/shell-logger/commit/512cab0d4e2a4962f9adc0bafc4970aaf6175ab7))
* Migrate from importlib.resources to pkgutil. ([`667c08f`](https://github.com/sandialabs/shell-logger/commit/667c08fece96629c4d46aec4cc58204f9ff13244))

  Python < 3.7 does not support importlib.resources.
* Fixed an issue where TMPDIR can break multiprocessing.Manager in logger. ([`7b4a3db`](https://github.com/sandialabs/shell-logger/commit/7b4a3db7650bf0bfea15b71a66be10e25fa622b9))

  There doesn't seem to be a reliable way to test this with py test.
* Make regex search case-insensitive ([`35fd993`](https://github.com/sandialabs/shell-logger/commit/35fd993fc192df64ae9207060a8f9bb459888ffc))
* Added a feature to test a single stat only (with trace), tests for bug fixed in previous commit ([`dfb696f`](https://github.com/sandialabs/shell-logger/commit/dfb696f321b1bcf9cab6c11225e6cab762f8d790))
* Fixed a bug when we collect only a subset of stats (cpu, disk, memory) ([`5048779`](https://github.com/sandialabs/shell-logger/commit/50487794864f02738f4e9bff81932823dbca0ca3))
* Attempt to speed up trace; bugfix in search ([`f62029f`](https://github.com/sandialabs/shell-logger/commit/f62029f1917382d69aceefb493abe75e0fdbf0e3))
* Minor HTML tweak (push line numbers to the left) ([`1800ebd`](https://github.com/sandialabs/shell-logger/commit/1800ebd7ae6609003fe4f95f989ad6f02c2d6fe8))
* Added line numbers to improve search experience ([`4d91b37`](https://github.com/sandialabs/shell-logger/commit/4d91b3789909762bcde28541fee928057c5f775c))
* Forgot to add search JS ([`05d24c0`](https://github.com/sandialabs/shell-logger/commit/05d24c0600918492f85fb8597bf81fddf317b6ca))
* Added a search feature for stdout/stderr/trace/ulimit/env ([`df6f3f4`](https://github.com/sandialabs/shell-logger/commit/df6f3f4f8cefa3238ebd6b0fba0477ef50fe3a75))

  Also added a disabled unit test. Not sure if we want to fix the
  behavior it identifies.

  TODO: maybe only enable this search under certain circumstances (e.g.
  line count is super long or something).
* Make sure /tmp is always included in disk stats ([`08ec0ea`](https://github.com/sandialabs/shell-logger/commit/08ec0ea54513580b0202556c73eb42d9f7a6b9a6))
* Minor tweak to HTML (no tooltips) ([`e8d13be`](https://github.com/sandialabs/shell-logger/commit/e8d13be0d614a6bd7eb5cd864719d719bc6c8801))
* Minor tweak to HTML (remove points on graph) ([`6530773`](https://github.com/sandialabs/shell-logger/commit/6530773340ee46c6f0a9f52376ac7815e91e3d7d))
* Fixed bug by giving resource usage charts a unique id. ([`9085e45`](https://github.com/sandialabs/shell-logger/commit/9085e457acb7dfa02108a8f894559d744bec9e46))
* Now I'm fairly happy with the HTML. ([`5a1aeff`](https://github.com/sandialabs/shell-logger/commit/5a1aeffbd6ae9a7be7df7e0ef1e9761ed517de35))

  Will remove SVG stuff soon.
* Updates to HTML generation. ([`37e9186`](https://github.com/sandialabs/shell-logger/commit/37e91864cb613dd2db42fc32a1940b76c9ea16b8))

    included the bundle which contained some dependencies).
  * Added hostname to the command details
  * Rearranged the stats graphs in the generated HTML.
* More updated to HTML output ([`be68d40`](https://github.com/sandialabs/shell-logger/commit/be68d40fd9fe40f3cb542fea0b279fe73fff8190))

  * Now using Chart.js instead of SVGs for CPU/Memory/Disk usage
  * Code is even uglier (TODO: fix that)
  * TODO: remove SVG functionality entirely.
* More HTML tweaks ([`a259446`](https://github.com/sandialabs/shell-logger/commit/a259446b0e79d9c2990d76d216ddf0be0c99d9e3))
* Bug fix ([`25a75e4`](https://github.com/sandialabs/shell-logger/commit/25a75e425cf257979a4fe1a3c057ed1c7794ebb0))
* More refactoring of HTML output ([`f7c976b`](https://github.com/sandialabs/shell-logger/commit/f7c976ba3d3360aeab327024b9c5ddb92eec31b1))
* More refactoring of HTML generation ([`843fe1f`](https://github.com/sandialabs/shell-logger/commit/843fe1f56f718f84ac3d1784c87370db54adeab2))
* Refactor some of the HTML generation ([`47cf3f9`](https://github.com/sandialabs/shell-logger/commit/47cf3f9feaf2a44f110e18542d7591b3ec357b5f))
* Embed bootstrap and Chart.js into generated HTML files for furute HTML enhancements ([`15b6fbf`](https://github.com/sandialabs/shell-logger/commit/15b6fbff516ec4f27b3b4a97e6186b4826e4cf37))
* Don't print an extra newline at the end of each line in HTML stderr/stdout ([`3204ba1`](https://github.com/sandialabs/shell-logger/commit/3204ba1c695bfaa61b7095764ae41b7c89671009))
* Changed stdout and stderr in HTML to monospaced font ([`3a7323e`](https://github.com/sandialabs/shell-logger/commit/3a7323e42f4c3b9d0eb0cf0fcca6b1633039cee8))
* Fixed a bug in logger where commands with heredocs would hang ([`579096a`](https://github.com/sandialabs/shell-logger/commit/579096a3e2b15451c65519a5cc91bbdbbd90317d))
* Removed stray debug print ([`885777a`](https://github.com/sandialabs/shell-logger/commit/885777a3caeaffdc4226b5983f338d6fc9674754))
* Fixed a few bugs in Logger. ([`5ca52d9`](https://github.com/sandialabs/shell-logger/commit/5ca52d9cbf7ad0fb55a746a34a62cd5c5b3932eb))

  * CWD is now correct in HTML
  * Commands which spawn subshells like newgrp don't raise an error when
    logger tries to look at the return code.
* Changed the logger to run all commands in a single shell. ([`69496f2`](https://github.com/sandialabs/shell-logger/commit/69496f21c1d82413c541f54477bdacdc7082bf92))

  Previously, a new shell was spawned for every command run in the logger.
  Now it is the case that the logger will run all commands in one shell.
  So running something like logger.log("Switch groups", "newgrp my-group")
  followed by logger.log("Print group", "id -gn") would have the same effect
  as running "newgrp my-group" and "id -gn" in your terminal: the output
  should be "my-group".
* Refactor ([`25ca040`](https://github.com/sandialabs/shell-logger/commit/25ca040fdfd387299d06327e38a493b8bdf6635d))
* Fixed a bug in logger. Moved trace to file instead of str by default. ([`c5447a9`](https://github.com/sandialabs/shell-logger/commit/c5447a953feae06033f6dd64d9d036c54786b000))

  Accidentally removed stdout/stderr output in html.
* Logger aux data added to HTML. ([`a0fdea8`](https://github.com/sandialabs/shell-logger/commit/a0fdea84a5d3a9ca364c8c9c0558b5fd4a94ebac))

  Also actually committed memory test for logger saving memory by
  not keeping stdout/stderr in a string.
* Added a unit test to ensure that the logger conserves memory. ([`25799b8`](https://github.com/sandialabs/shell-logger/commit/25799b85965aaf261cfd31ecb46fbd2c56b9a6a6))

  Also fixed the logger so that it actually conserves memory. The
  newly added test exposed that the logger wasn't conserving memory
  as it should when it doesn't save stdout/stderr to a string.

  Added a unit test test_logger_does_not_store_stdout_string_by_default
  which reads 256 MB from /dev/urandom to stdout and ensures that memory
  usage never exceeds 64 MB; conversely, the test will also ensure that
  it takes more than 128 MB of memory to store stdout into a string.

  Caveat: if it takes too long to read 128MB from /dev/urandom on
  a system running pytest tests/test_logger.py, memory usage may
  seem to small and cause an assertion failure. This doesn't
  necessarily mean that the test is wrong, it might mean you'll need
  to modify the test to sleep longer before capturing memory usage.
* Updated logger stdin/stdout storage (disk vs memory). ([`c198083`](https://github.com/sandialabs/shell-logger/commit/c19808309bef591dbad8e4e4ee0acc5eba5a6d62))

  * Removed console (combined stdin/stdout)
  * Readded streaming to file (instead of storing stdin/stdout in memory).
* Rearranged imports. ([`a078fa9`](https://github.com/sandialabs/shell-logger/commit/a078fa97f9dc395115cf34bd49d80ac27e3c56d2))

  Switch (non-internal) imports from "from ... import ..." for
  everything except for types and annotations.
* Updated the logger. ([`a50d2dc`](https://github.com/sandialabs/shell-logger/commit/a50d2dc69afc8cfa4bca5b03fe932a478a2b0758))

  * Moved the logger into a directory with its own package
  * Fixed the pytests for logger so that pytest tests/test_logger.py
    is error-free and warning-free
  * Added support for trace collection (strace, ltrace)
  * Added support for CPU, memory, and disk usage collection (TODO:
    make everything nice in the HTML)
  * Added partial support for aux data (TODO: add aux data to HTML)
    aux data includes environment, user, group, umask, ulimit, shell
* Update documentation on stdin_redirect ([`d3b191e`](https://github.com/sandialabs/shell-logger/commit/d3b191ebf8c72fbe0e00e8ad0b2feca64e9d4cba))
* Resolve "Allow override of stdin=/dev/null for logger jobs" ([`2dc1424`](https://github.com/sandialabs/shell-logger/commit/2dc14245dc30ceee4ca9faa0c667ae8941b3e3c4))

  Closes #477

  See merge request EM-Plasma/BuildScripts!415
* Deal with Paths in command lists ([`866f11c`](https://github.com/sandialabs/shell-logger/commit/866f11cd9ce06bf16a5180b41005fce2932539ce))
* DEBUGGING ([`8f4cd85`](https://github.com/sandialabs/shell-logger/commit/8f4cd851f6bf5b2e6b636c149f08a48a46e59f4e))
* test_logger ([`048735e`](https://github.com/sandialabs/shell-logger/commit/048735ebdc7aaecc101b30c137aba557cc4fc06d))
* logger updates ([`ec18db4`](https://github.com/sandialabs/shell-logger/commit/ec18db41a57743ab4ef67b08568d4b9d632aa7bc))
* Updates to common_functions.py ([`addee2c`](https://github.com/sandialabs/shell-logger/commit/addee2cc3dfa0dee5d3fbb5b8cb2a59ba2d9519d))
* Fixed a syntax error in logger.py ([`3eb39be`](https://github.com/sandialabs/shell-logger/commit/3eb39be8b22cce622f6643e85ee13ef57e191466))
* Added JSON (de)serialization support for pathlib.Path in logger.py ([`eb82e9a`](https://github.com/sandialabs/shell-logger/commit/eb82e9a359ee56d9ae12262b895c2627b0abbb6e))
* Import pathlib in logger.py ([`ad31c29`](https://github.com/sandialabs/shell-logger/commit/ad31c2974ba1dfd516986edff54615be4129638f))
* more syntax error fixing in python scripts ([`cd123a6`](https://github.com/sandialabs/shell-logger/commit/cd123a6cf2da4b5f992f441aee1ec34c19fd097a))
* Refactor BuildScripts to use pathlib ([`9ebb300`](https://github.com/sandialabs/shell-logger/commit/9ebb300fcaeb7b79d0be66bd34467186fb37aec1))
* Use mkdtemp to create strm_dir in logger.py ([`4054aa4`](https://github.com/sandialabs/shell-logger/commit/4054aa4dea1ae60b117f7a2759e5fab67a2f8bf3))
* Fixed some duration logic and added a test. ([`5ce4f30`](https://github.com/sandialabs/shell-logger/commit/5ce4f3040f395b15ee3ab1ca38ff72f42a0312b5))
* All current logger tests passing in <1s ([`390b482`](https://github.com/sandialabs/shell-logger/commit/390b482b65e04aba81e713e09e24438438e354ca))
* Create HTML Log File in Stream Directory ([`dbb5161`](https://github.com/sandialabs/shell-logger/commit/dbb5161a9fd13715f9d782c83e523bdb709d1994))

  Create it in the stream directory and let all the work happen there,
  then create a symlink in the log directory pointing to it. This is to
  avoid multiple Loggers in the same workspace overwriting one another's
  HTML log file.
* Simultaneous Loggers in Same Workspace (#236) ([`28338f4`](https://github.com/sandialabs/shell-logger/commit/28338f4d5b4c2ffdd961d382144380ecfa16a754))

  Append microseconds to logger directory names to deconflict
  "simultaneous" directory creation.
* Remove files for recreated HTML logs. ([`e91b8b7`](https://github.com/sandialabs/shell-logger/commit/e91b8b74a991e08430ef40aa9e5e74d683fcd6ac))
* Don't append '_latest_run' to the HTML file name. ([`5946a57`](https://github.com/sandialabs/shell-logger/commit/5946a57721a1ba9358597e80bd43fa7c02c76979))
* Updated logger to symlink main HTML to newest run HTML. Have not run the test. ([`2bc9aea`](https://github.com/sandialabs/shell-logger/commit/2bc9aea7aed697c773a183504b30d9062cd5a7b6))
* Shifted log method higher in the file since it is a more-used method ([`68a0ef3`](https://github.com/sandialabs/shell-logger/commit/68a0ef3dcc404b8ac096a5f7fcd439b830c16979))
* Integrate update_trilinos_fork.py into... (#162) ([`8f33f28`](https://github.com/sandialabs/shell-logger/commit/8f33f28e43198d0dad694f7f3ac0869fbd7c8981))

  In the Trilinos sync pipeline, swap out the old bash updateTrilinosFork
  script for the new update_trilinos_fork.py Python one.
* logger now does pretty printing of json ([`6a51733`](https://github.com/sandialabs/shell-logger/commit/6a517336d65960727d9210bbd9a18760a73ec02e))
* Fixed build_empire.py when not called in BuildScripts ([`418e9cb`](https://github.com/sandialabs/shell-logger/commit/418e9cb0847d0ad765c003ff69008ee8e8ff8298))

  also sorted the Trilinos options when using --interactive.
* Added logger test suite changes from 156-create-one-build-trilinos-script-to-rule-them-all 6e40af4 ([`d5948ce`](https://github.com/sandialabs/shell-logger/commit/d5948ce026ad7799593387ed934f55dd7003d32d))
* Changed run_cmd_generator to be much simpler ([`66e8704`](https://github.com/sandialabs/shell-logger/commit/66e8704a770a7a32f9714a20e8dfde58dcc87188))
* Made '--compiler' only required flag for Trilinos script ([`3efa3ff`](https://github.com/sandialabs/shell-logger/commit/3efa3ff3ab91233aa1a0b3380b901e01f9ffed57))
* Fixed a few things with logger ([`8833cc1`](https://github.com/sandialabs/shell-logger/commit/8833cc1ea18b4a2bd11f42135a3c3341719f03bf))
* Fixed name conflict in Logger ([`57f2a03`](https://github.com/sandialabs/shell-logger/commit/57f2a0366902592d5e6be32fdc57df882b77ef3a))
* Added easy script to recreate HTML from JSON ([`10ae0a5`](https://github.com/sandialabs/shell-logger/commit/10ae0a5ccf836eefebdbffceecdba65c0a350a88))
* Changed logger tmp_dir and stdout/stderr files to have timestamps ([`2a38baf`](https://github.com/sandialabs/shell-logger/commit/2a38baf994006ec40ba6660b775c07b4fd9256b6))
* Removed top_dict from Logger and dependent files. ([`5d678a8`](https://github.com/sandialabs/shell-logger/commit/5d678a81e72883dbfbe47656d0480e92e68c06c4))
* Flush stdout/stderr more frequently in common_functions and logger ([`e43ff4b`](https://github.com/sandialabs/shell-logger/commit/e43ff4b8a4b605349b0f10ff85410d8941ef1c39))
* Small change to logger.py. Print command before executing. ([`d8dbe5f`](https://github.com/sandialabs/shell-logger/commit/d8dbe5f901f930698a2623e5c901ed8360c90140))
* Added some suggestions from Scot. ([`9714fb0`](https://github.com/sandialabs/shell-logger/commit/9714fb0629eff53c60c17d0a4df90e82499c8d03))
* Added a CCI directory structure test. ([`a8056cc`](https://github.com/sandialabs/shell-logger/commit/a8056cc34528e62f6651e085b1f3acebc93db33c))
* Updated more documentation, mostly for tests. ([`f7f841a`](https://github.com/sandialabs/shell-logger/commit/f7f841a2d46aed5e35915f0bea2cf8c8d39238ae))
* Added build_empire CCI wrapper. Fixed some CCI prefix issues. ([`caf17db`](https://github.com/sandialabs/shell-logger/commit/caf17db91d2747e3073e0ef7689e9c5e1f32be9d))
* Add 156-create-one-build-trilinos-script-to-rule-them-all commits to this branch. ([`94114e1`](https://github.com/sandialabs/shell-logger/commit/94114e1b30285ac5f7dbbf4f96f17da189a9cd5d))

  Transfer common_functions and logger updates from
  152-create-one-build-empire-script-to-rule-them-all 0846d9cd

  Added update_trilinos_fork first draft.

  Updated some documentation in update_trilinos_fork

  Updated documentation to work better with Sphinx.

  Updated more documentation.

  Added files for easy documentation generation.

  Changed documentation title.

  Add 156-create-one-build-trilinos-script-to-rule-them-all commits to
  this branch.
* Transfer install_trilinos development work from ([`3bc132f`](https://github.com/sandialabs/shell-logger/commit/3bc132f4a04990aef963a30a7973841c50e4847c))
