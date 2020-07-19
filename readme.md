# Simple Cloud Agnostic TCP/UDP Proxy



## Why

There are a variety of ways to get traffic from WAN to a k8 cluster. Depending on where the k8 cluster is hosted, there
may be additional limitations.

This is a simple set of tools that create a simple reverse proxy host which can be configured to work aground almost all 
provider-specific limits.

Specifically, I built this tool for use with Digital Ocean, but it should be easily adaptable to your specific needs.


## How

 
There's two parts to this repo

0. Packer/Salt - builds the reverse proxy machine image
1. The Python3 tool that 
2. [traefik]() - The actual reverse proxy that powers it all.


I need a small-ish script that can take:

- The tag to ID cluster nodes with
- The proto/port in to port out map

It will then find the IP addresses for that cluster node
It will take the IP address(s) and the destination ports and render out a traefik config file

Then i can deploy two systemd files to the host where the traefik one depends on the unit wrapping this script
