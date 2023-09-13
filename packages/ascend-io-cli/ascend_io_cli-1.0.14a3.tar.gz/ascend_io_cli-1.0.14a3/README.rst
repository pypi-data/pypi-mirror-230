=====================
Ascend.io CLI
=====================

This package contains the `Ascend CLI <https://developer.ascend.io/docs/python-sdk>`_. The
CLI is designed to make working with the Ascend.io platform simple and easy. This CLI
wraps the `Ascend Python SDK <https://developer.ascend.io/docs/python-sdk>`_.

Get help by passing ``--help`` into any command for a rundown of the syntax for each command.::

 ascend --help

Make sure you are running the most current version and see what version of the *ascend-io-sdk* and platform you are using::

 ascend version

The CLI can save default values for certain parameters. For example, to set a default hostname::

 ascend config set hostname my-ascendhost.company.io

Removing a default is as simple as::

 ascend config unset hostname

---------------
Authentication
---------------
You will want to download your API key from the Ascend UI. `Here is some documentation <https://developer.ascend.io/docs/python-sdk#getting-started>`_
that shows you how to get your key. Please keep your key secure!


---------------
Read the Docs
---------------
* `Ascend.io Python SDK Documentation <https://developer.ascend.io/docs/python-sdk>`_
* `Ascend Developer Hub <https://developer.ascend.io>`_
* `Ascend.io <https://www.ascend.io>`_
