Notes for a Rewrite
===================

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
