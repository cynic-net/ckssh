ckssh - SSH Agents with Compartmentalized Keys
==============================================

Forwarding of authentication agent connections over ssh is very
convenient, but also dangerous on hosts where others do or may have root
access. Anybody who can gain access to the Unix domain socket on which
the local sshd is listening can send authentication requsts to your
agent and thus effectively has use of all the keys in your agent.

One way of mitigating this problem is to ask the agent to confirm all
requests for signatures from particular keys (e.g., by using the `-c`
option on `ssh-add(1)`). However, this is sometimes inconvenient, and
not all agents support this.

Ckssh helps mitigate the problem by allowing you to easily use separate
keys stored in separate agents for connections to different hosts. A
typical use case would be to set up a separate key for work or a client
so that client a compromised client server (or malicious admin) would
gain access only to hosts accessible via that key, and not personal
hosts or those belonging to other clients.


Configuration File
------------------

The configuration file is found in `$HOME/.ssh/ckssh_config`. It is
parsed in the same way as `ssh_config`:

* Initial whitespace on a line is ignored.
* Empty lines are ignored.
* Lines starting with `#` are comments, and ignored. A `#` preceeded
  by anything other than whitespace is not a comment.
* Configuration directives are of the form "<key><whitespace><value>".

### Configuration Parsing Bugs

The current parsing code is not completely compatible with
ssh_config.

* We do not accept a list of patterns on the `CK_Host` line, just a
  single name that is matched exactly.
* We take parameters only from the first matched `CK_Host` section,
  and ignore all sections after that.

### Configuration Directives

The `CK_DefineCompartment` and `CK_Host` directives start separate
sections of the configuration file; after one of these, subsequent
configuration directives are read as part of that section up until
the next `CK_DefineCompartment` or `CK_Host` directive.

#### Compartment Configuration

`CK_DefineCompartment` defines a compartment (ssh-agent process) to
hold keys.

The ssh-agent socket will be named `$XDG_RUNTIME_DIR/ckssh/socket/$name`
where `$name` is the parameter provided to `CK_DefineCompartment`.
`$XDG_RUNTIME_DIR` is expected to be set up as per the [FreeDesktop.org
basedir spec][basedir]; the program currently fails if it's not set as
it's unable to properly set up a runtime dir itself.

A `CK_DefineCompartment` section may contain one or more `CK_Keyfile`
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

A `CK_Compartment` directive specifies the compartment to be used;
it must be one defined by a `CK_DefineCompartment` directive.

Any other configuration directives are treated as configuration
options to be passed on to SSH.


Copyright and License
---------------------

Ckssh is copyright 2016 by Curt J. Sampson <cjs@cynic.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
