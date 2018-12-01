Notes for a Rewrite
===================

`ckssh-agent`/`ckssh-add`/`ckssh-???` Usage
-------------------------------------------

This is the underlying program called by `ckset` that does all the
heavy lifting.

It's written in Python, and it may or may not want to use the
[Paramiko] library for some SSH agent operations. (Currently the
operations, such as getting a list of loaded keys from an agent, look
simple enough that either calling `ssh-add` or just writing the
minimal code to query the agent directly will be enough.)


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
