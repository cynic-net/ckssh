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
