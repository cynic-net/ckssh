ckssh - SSH Agents with Compartmentalized Keys
==============================================

Forwarding of authentication agent connections over ssh is very
convenient, but also dangerous when forwarding to hosts where others
do or may have root access. Anybody who can gain access to the Unix
domain socket on which the local sshd is listening can send
authentication requsts to your agent and thus effectively has use of
all the keys in your agent.

One way of mitigating this problem is to ask the agent to confirm all
requests for signatures from particular keys (e.g., by using the `-c`
option on `ssh-add(1)`). However this is not only inconvenient, but
not all agents support this.

Ckssh helps mitigate the problem by allowing you to easily use
separate keys stored in separate agents for connections to different
hosts. A typical use case would be to set up a separate key and agent
for work so that a compromised work server (or malicious admin) would
gain access only to hosts accessible via that key, and not personal
hosts or those belonging to other companies.


Usage
-----

If this is your first time using this, see the [SETUP](SETUP.md) file
to set up your initial configuration.

Basic setting commands are:

    ckssh cjs@cynic.net         # Set the current container
    ckssh -a                    # Add default keys to the current container
    ckssh -a cjs@cynic.net      # Do both in one action

In startup scripts for, e.g., your desktop environment you will
probably want just to set the container without adding keys since at
that point you might not yet have a way to prompt for the
passphrase(s).

### Command Details

* `ckset [-v]`

  If `SSH_AUTH_SOCK` is unset, 'No compartment.' is printed to stderr.
  If it's set, but not to a compartment known from the configuration
  file, 'Unknown compartment.' is printed to stderr. Otherwise the
  compartment name is printed to stdtout.

  For known compartments, additional warnings are printed to stderr
  when the compartment is not running (i.e., no agent is responding on
  that socket) and when a key defined for the compartment (with a
  `CK_Keyfile` directive) is not currently loaded.

  Adding `-v` will print to stdout all the compartment's configured
  keyfiles, noting which ones are present and absent in the agent.

  This returns 0 if `SSH_AUTH_SOCK` is pointing to an agent for a
  running compartment (regardless of what keys are loaded), or 1
  otherwise.

* `ckset -l [-v]`

  List all compartments (configured with `CK_Compartment` directives)
  and their status (running or not). With `-v`, also show the keyfiles
  configured for each compartment and whether or not they are loaded.

* `ckset -a`

  Add all configured but unloaded keys to the current compartment.
  This will prompt for passphrases where necessary.

* `ckset [-a] COMPARTMENT-NAME`

  Ensure that the given compartment is running (starting an agent if
  necessary) and switch to it. (Command-line completion should be
  provided for the name.) With `-a` also attempt to add all keys
  configured for the compartment that are not already loaded.

  This may be interactive if `-a` is specified (prompting for
  passphrases), but otherwise is not, allowing setup of compartments
  in startup scripts such as `xinitrc`.

  Return values:
  - 0: Changing to the given compartment was successful.
  - 1: The requested compartment name does not exist.
  - 2: The compartment could not be started (`ssh-agent` failed to start).
  - 3: The compartment was started, but not keys could be added (`-a` only).

* `ckset -A KEYFILE [-A KEYFILE] [COMPARTMENT-NAME]`

  As above, but add keys specified by the KEYFILE arguments to the
  `-A` option(s), setting the compartment first if the optional
  COMPARTMENT-NAME is given. If COMPARTMENT-NAME is not given this
  will add keys to the current compartment (SSH agent) even if it is
  unknown.


Copyright and License
---------------------

ckssh is copyright 2016, 2018 by Curt J. Sampson <cjs@cynic.net>

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
