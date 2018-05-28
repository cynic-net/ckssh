ckssh Setup and Configuration
=============================

#### Contents

* Quickstart
* Configuration File
* The ckssh.py Command and Shell Functions


Quickstart
----------

1.  Create the configuration file `$HOME/.ssh/ckssh_config` and put
    the following in it, tweaking to taste:

        CK_Compartment main
            CK_Keyfile ~/.ssh/id_rsa

    The compartment name is usually named for the key (or set of
    related keys) you're using. The keyfile should be a path to an SSH
    private key file. Having the public key in a file of the same name
    but with `.pub` appended will avoid having to decrypt the private
    key file when ckssh needs to look up just the public key.

2.  Make sure that the `bin/ckssh.py` file from this repo is somewhere
    you can run it and marked executable (`chmod +x`). It doesn't have
    to be in your `PATH`, though it may be more convenient if it is.

3.  In the Bash shell where you want to use ckssh, execute:

        eval $(ckssh.py bash-init)

    (If it's not in your `PATH` you'll want to specify a path along
    with `ckssh.py`.) Putting this in your `~/.bashrc` is convenient.

4.  To set your current compartment to `main` (or whatever other name
    you chose) and add your key to it, execute:

        ckset -a main


Configuration File
------------------

The configuration file is found in `$HOME/.ssh/ckssh_config`. It is
parsed in the same way as `ssh_config`:

* Initial whitespace on a line is ignored.
* Empty lines are ignored.
* Lines starting with `#` are comments, and ignored. A `#` preceeded
  by anything other than whitespace is not a comment.
* Configuration directives are of the form `<key><whitespace><value>`.

### Configuration Parsing Bugs

The current parsing code is not completely compatible with `ssh_config`.

* We do not accept a list of patterns on the `CK_Host` line, just a
  single name that is matched exactly.
* We take parameters only from the first matched `CK_Host` section,
  and ignore all sections after that.

### Configuration Directives

The `CK_Compartment` and `CK_Host` directives start separate
sections of the configuration file; after one of these, subsequent
configuration directives are read as part of that section up until
the next `CK_Compartment` or `CK_Host` directive.

#### Compartment Configuration

`CK_Compartment` defines a compartment (ssh-agent process) to
hold keys.

The ssh-agent socket will be named `$XDG_RUNTIME_DIR/ckssh/socket/$name`
where `$name` is the parameter provided to `CK_Compartment`.
`$XDG_RUNTIME_DIR` is expected to be set up as per the [FreeDesktop.org
basedir spec][basedir]; the program currently fails if it's not set as
it's unable to properly set up a runtime dir itself.

A `CK_Compartment` section may contain one or more `CK_Keyfile`
directives, each of which specifies the full path to an SSH private
key file to be loaded in to the agent with `ssh-add`. Shell variables
and tildes in the path are interpolated by the shell.

Any other configuration directives are treated as configuration
options to be passed on to `ssh`. These are passed on after (and so
will be overridden by) directives in the `CK_Host` section.

[basedir]: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

#### Host Configuration

The `CK_Host` directive is similar to ssh_config's `Host` directive,
and starts a host configuration section.

A `CK_CompartmentName` directive specifies the compartment to be used;
it must be one defined by a `CK_Compartment` directive.

Any other configuration directives are treated as configuration
options to be passed on to SSH.


The ckssh.py Command and Shell Functions
----------------------------------------

ckssh sets the compartment by setting the `SSH_AUTH_SOCK` environment
variable. This cannot be done by a child process of the shell so for
Bash we use a shell function that calls `ckssh.py` and then executes
any environment variable settings that it requests.

(Shells other than Bash are not currently supported, but patches are
welcome.)
