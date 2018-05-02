Notes for a Rewrite
===================


`ckset` Usage
-------------

The `ckset` command is a shell function that serves as an interface to
`ckssh-agent` and `ckssh-add`. The primary purpose of making it a
function is to allow it to change `SSH_AUTH_SOCK` and `SSH_AGENT_PID`
in the current process's environment. (`SSH_AGENT_PID` is little-used,
so simply unsetting it might be best for the moment.)

* `ckset [-v]`

  If `SSH_AUTH_SOCK` is not pointing to a configured compartment or is
  unset, `No compartment` is printed to stderr. Otherwise the current
  compartment name is printed to stdout.
  
  Additional warnings are printed to stderr when the compartment is
  not running (i.e., no agent is responding on that socket) and when a
  key defined for the compartment (with a `CK_Keyfile` directive) is
  not currently loaded.

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


`ckssh-agent`/`ckssh-add`/`ckssh-???` Usage
-------------------------------------------

This is the underlying program called by `ckset` that does all the
heavy lifting.

I'm not sure if we need to have separate `-agent` and `-add` programs,
as OpenSSH does, or if we can just have one program that does all the
work.

This is probably most easily written in Python using the [Paramiko]
library.


`ckssh` Usage
-------------

For options, one idea is to have `ckssh` set up a new ssh_config file
(in `/run/user/1765/ckssh/ssh_config/COMPARTMENT/HOST`) which includes
its configuration at the top and includes `~/.ssh/config` after that
(via the ssh_config `Include` directive or simply by copying it into
the file). But I'm not sure how much (if any) advantage this offers
over simply adding `-o` options to the `ssh` command that it runs.


`ssh` Usage
-----------

I'm worried about people typing `ssh` when they meant `ckssh` and
forwarding from agents with keys that shouldn't be available on the
remote. I think this is solved via disabling forwarding for all (or
most) hosts by default, and enabling it only when ckssh is used. Maybe
we want a lint program to check that things are configured this way?



[Paramiko]: http://docs.paramiko.org/
