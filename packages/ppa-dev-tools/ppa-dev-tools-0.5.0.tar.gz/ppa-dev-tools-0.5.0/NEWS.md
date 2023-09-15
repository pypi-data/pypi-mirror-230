# Unreleased #

It is now possible to create PPAs under a different team's ownership via
the `--owner` option:

    $ ppa create --owner foobar my-ppa

As a convenience, this can also be specified in ppa address form, i.e.:

    $ ppa create ppa:foobar/my-ppa

Furthermore, most places that take a PPA address will also take a full
URL, including URLs ending with /+packages.  For example, all of these
are accepted as valid PPA specifiers:

    $ ppa wait my-ppa
    $ ppa wait myself/my-ppa
    $ ppa wait ppa:myself/my-ppa
    $ ppa wait https://launchpad.net/~myself/+archive/ubuntu/my-ppa
    $ ppa wait https://launchpad.net/~myself/+archive/ubuntu/my-ppa/
    $ ppa wait https://launchpad.net/~myself/+archive/ubuntu/my-ppa/+packages


Private PPA support is now available via the `--private/--public`
arguments, allowing toggling a PPA's privacy, if allowed by Launchpad.
For example:

    $ ppa create --private ppa:myself/my-private-ppa
    

It is now possible to save and load Launchpad OAuth credentials, to
permit use of ppa-dev-tools in situations where you can't use
launchpadlib's automatic authentication mechanics.  A new command is
added to dump the credentials from an authenticated session:

    $ ppa credentials
    Launchpad credentials written to credentials.oauth

You can then load them via a new `--credentials` global argument, for
example:

    $ ppa --credentials ./credentials.oauth create ppa:myteam/myppa

Credentials can also be supplied via an LP_CREDENTIALS environment
variable.  Thanks to Massimiliano Girardi for this feature.


The `ppa wait` behavior has changed to display just a screenful of
status while waiting on builds.  The old behavior, where status updates
are printed to stdout and scrolled, is still available via the --log
option.

Also, the `wait` command now supports a 'name' configuration parameter
that allows specifying a single source package to wait on.  The
'wait_max_age_hours' parameter makes it consider only uploads within the
given timeframe.  The 'exit_on_only_build_failure' parameter makes the
wait exit if the only jobs that it is monitoring are failed builds.
These options are aimed to facilitate CI/CD integration, but can also
improve performance of the waiting operation on larger PPAs.


This release provides an important bugfix, enabling the `ppa tests`
command to properly parse and handle newer format autopkgtests.  The log
files for tests run on Ubuntu lunar and newer are prefixed with a
timestamp that caused `ppa tests` to misread the subtest name.  The
timestamps are now recognized and subtest names parsed properly.
(LP: #2025484)

Other bugfixes have focused on improvements to input and error handling
for a variety of conditions that have come up in practice.  This
includes some more robust handling of errors generated during Launchpad
outages or other glitches (LP: #1997122).


# 0.4.0 #

Reverse dependencies, build dependencies, and installation dependencies
can be identified for a given source package using cached APT
information.  This list of packages will be used to generate lists of
autopkgtest triggers, which when run should help identify issues that
could get flagged in Britney2 runs.  While similar to functionality
provided by Bileto+Britney2, it is a lighterweight facsimile which
doesn't handle special cases so should not be considered an equivalent,
just as a preliminary screen to catch basic issues.

For now, users will need to create and maintain this cache by hand
(automatic caching is planned for 0.5).  See the README for a suggested
rsync command to do this.

In addition, The `ppa set` command now supports a number of new command
line options.  `--ppa-dependencies` allows you to specify that your PPA
can use the contents of one or more other PPAs to satisfy build
dependencies.  The `--architectures` option now has some related options
`--all-architectures` and `--default-architectures` for "Give me
everything" and "Just the usual", respectively.  The `--enable` and
`--disable` arguments control whether packages can be uploaded to the
PPA to build.

All of the options supported by `ppa set` can also be specified to `ppa
create` to allow specifying them at creation time.

Beyond these two features, notable bugfixes address problems with Ubuntu
release specification, improvements to the `ppa tests` output, and
various idiosyncrasies with command line arguments.


# 0.3.0 Release #

Autopkgtest trigger action URLs are printed for packages in the PPA when
running the `ppa tests` command.  Both plain and 'all-proposed' style
triggers are displayed.  These can be loaded in a web browser by someone
with core-dev permissions to start the test runs.  `ppa tests` can then
be re-run to check on the tests status and results.

Most commands now accept the PPA identifier as a URL, as well as a
formal PPA address, or just the basic name of the PPA, which will be
assumed to be in the user's namespace.

New options are now available for a few commands.  The option parsing
and handling has been significantly reworked to allow per-command arg
shortcuts, so for instance -r can mean one thing for the 'create'
command and something completely different for the 'wait' command.


# 0.2.1 Release #

This corrects some packaging issues when generating .deb and .snap
packages:  Some missing build-dependencies are added, and some path
adjustments included to ensure the script is able to import the
installed python modules when installed in a snap environment.


# 0.2.0 Release #

This release adds a new 'tests' command that lists any pending or
waiting test runs against the PPA at autopackage.canonical.com.  This
functionality is integrated from Christian Ehrhardt's `lp-test-ppa`
tool[1], coupled with new test cases, code documentation, and
pylint/flake style improvements.  The new command is run like this:

    $ ppa tests ppa:my-name/my-ppa

The second major focus for this release was to refine and solidify the
packaging and installation process.  In addition to PyPI, this will be
packaged as a snap and as a debian package via PPA (of course!)

1: https://git.launchpad.net/~ubuntu-server/+git/ubuntu-helpers/tree/cpaelzer/lp-test-ppa



# 0.1.0 Release #

A core set of commands including create, destroy, wait, list, and show
are implemented, along with basic help and package docs.  The
intent of this release is to get registered with PyPI and scope out the
release process.

Here's an example set of commands one might use:

   $ ppa create my-ppa
   $ dput ppa:my-name/my-ppa some-package.changes
   $ ppa wait my-ppa
   $ cat some-package/README | ppa desc ppa:my-name/my-ppa
   $ ppa destroy my-ppa

This creates a PPA and uploads a package to it.  Then it waits for the
package to complete building and then updates the PPA's description with
some user-provided information.  At this point the PPA might be shared
with users or used for testing purposes.  Finally, when no longer needed
it is removed.
