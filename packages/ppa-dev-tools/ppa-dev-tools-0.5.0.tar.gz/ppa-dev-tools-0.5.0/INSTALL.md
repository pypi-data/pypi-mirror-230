## Installation ##

The prerequisites for ppa-dev-tools can be satisified either through
PIP, or on Ubuntu 20.04-ish via the packaging system.

These modules are required:

  * appdirs
  * apt_pkg
  * debian.deb822
  * distro_info
  * launchpadlib
  * lazr.restfulclient
  * setuptools
  * software-properties
  * yaml or ruamel.yaml


### DEB ###

A PPA with .deb packages are available for Ubuntu.

  $ sudo add-apt-repository --yes --enable-source ppa:bryce/ppa-dev-tools
  $ sudo apt-get install ppa-dev-tools


### PIP ###

Alternatively, the package and its dependencies can be satisfied via PIP
for a user installation:

  $ pip install .
  $ ppa --version
  ppa 0.5.0


### SNAP ###

  $ sudo snap install ppa-dev-tools
  $ sudo snap alias ppa-dev-tools.ppa ppa
  $ ppa --version
  ppa 0.5.0


### SOURCE ###

On Ubuntu 20.04 and similar systems, prerequisites can be satisfied from
the apt repository:

  $ sudo apt-get install \
      python3-appdirs \
      python3-debian \
      python3-distro-info \
      python3-launchpadlib \
      python3-lazr.restfulclient \
      python3-setuptools \
      python3-software-properties \
      python3-yaml

Installation follows the usual python conventions:

  $ python3 ./setup.py check
  $ python3 ./setup.py build
  $ sudo python3 ./setup.py install
  $ ppa --version
  ppa 0.5.0
