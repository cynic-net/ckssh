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
