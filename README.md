ckssh - SSH Agents with Compartmentalized Keys
==============================================

Forwarding of authentication agent connections over ssh is very
convenient, but also dangerous when forwarding to hosts where others
do or may have root access. Anybody who can gain access to the Unix
domain socket on which the local sshd is listening can send
authentication requests to your agent and thus effectively has use of
all the keys in your agent.

Asking the agent to confirm all requests for signatures (e.g., with
the `-c` option to `ssh-add`), if the agent supports this feature, can
help prevent unauthorized use of keys. But even so this is both
inconvenient and prone to error.

Ckssh helps mitigate the problem by allowing you easily to use
separate keys stored in separate agents for connections to different
hosts. A typical use case would be to set up a separate key and agent
for a company so that if one of their servers is compromised (or has a
malicious actor) the only key that's compromised is the one you use
for that company, keeping keys for other companies and personal keys
safe.


Usage
-----

If this is your first time using this, see the [SETUP](SETUP.md) file
to set up your initial configuration.

`ckset` without an argument prints the current container name and
ensures that it is started and has all keys loaded. `ckset` with a
container name argument switches to that container and does the same.
The `-n`/`--no-load` option will disable loading of keys (though not
affect any keys that are already loaded) and the `-f`/`--force` option
will take a container name to be valid even if it's not named in the
configuration file.

In your desktop environment startup script you will probably want just
to set the container without adding keys (`-n`/`--no-load`) since at
that point you might not yet have a way to prompt for the passphrase(s).

### Command Details

* `ckset [-f] [-n] [-v]`

  Show the current compartment, starting an agent if necessary and
  optionally adding configured keys that are not already added to the
  agent.

  If `SSH_AUTH_SOCK` is unset, `No compartment.` is printed to stderr
  and the exit code is 1.

  If `SSH_AUTH_SOCK` is set to a known compartment (i.e., one named in
  the configuration file):
  - The compartment name will be printed to stdout.
  - An agent will be started for the compartment if one is not already
    running. If an agent cannot be started ckset will exit with code `2`.
  - Unless `-n` or `--no-load` is given, any configured keys that are
    not currently loaded will be loaded. All unloaded keys will always
    be attempted; if any attempt fails the exit code will be `3`, even
    if other attempts are successful.

  If `SSH_AUTH_SOCK` is set to a compartment not named in the
  configuration file:
  - The compartment name will always be printed to stdout.
  - When an agent is not running for the compartment and neither the
    `-f` nor the `--force` flag is given, a message will be printed to
    stderr and the exit code will be `1`.
  - If an agent is running for the compartment or the `-f` or
    `--force` flag is given, the unconfigured compartment name will
    not be treated as an error:
    - No warning will be printed.
    - An agent will be started for that compartment if one isn't
      already running. If an agent cannot be started ckset will exit
      with code `2`.

  Adding `-v`/`--verbose` will print all the compartment's configured
  keyfiles, noting which ones are present and absent in the agent.

* `ckset [-f] [-n] COMPARTMENT-NAME`

  Switch to the given compartment. Command-line completion should be
  provide for the compartment name.

  If the compartment is not named in the config file and no agent is
  running for it ckset will exit with code `1`. The `-f` or `--force`
  option will override the behaviour, treating the compartment as
  known (though obviously without any keyfiles configured).

  If no agent is running for the compartment one will be started.
  ckset will exit with code `2` if an agent can't be started.

  If `-n` or `--no-load` is given, the command is guaranteed never to
  be interactive and is suitable for use in startup scripts that do
  not have a tty such as `.xsession`. Otherwise an attempt will be
  made to load all configured keyfiles that are not already loaded.
  All unloaded keyfiles will be attempted; if any attempt fails the
  exit code will be `3`.

* `ckset -l [-v]`

  List all compartments (configured with `CK_Compartment` directives)
  and their code (running or not). With `-v`/`--verbose`, also show
  the keyfiles configured for each compartment and whether or not they
  are loaded.

* `ckset -d [COMPARTMENT-NAME]`  
  `ckset -D`

  `-d` removes the keys from the named compartment or the current
  compartment if no name is given. `-D` deletes the keys from all
  running compartments (even those not named in the config file).

### Exit Codes

The following exit codes are common to all commands.

- 0: The command was entirely successful.
- 1: The requested compartment does not exist (i.e., it's not named in
     the configuration file) and the `-f`/`--force` option was not
     supplied.
- 2: The compartment could not be started (`ssh-agent` failed to start).
- 3: The compartment was started, but at least one configured key
     could not be added.

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
