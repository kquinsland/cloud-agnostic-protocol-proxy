# Simple Cloud Agnostic TCP/UDP Proxy

A small collection of tools and scripts to build a standalone reverse proxy for multiple protocols. Hence the name:
Cloud Agnostic Protocol Proxy. 

Two components:

1. A set of packer/salt states to install the excellent [traeefik](https://containo.us/traefik/) proxy application and 
    wrap everything up in a single machine image 
2. A simple python tool to configure traefik based to forward traffic to the correct node/ports for a given k8 cluster.


As of right now, this tool only supports k8 clusters hosted in `digitalocean`, but it should be pretty easy to extend
to other cloud providers. See how the [digitalocean](capp/cloud_providers/digitalocean/__init__.py) 'plugin' is implemented for details.
 

## Why

There are a variety of ways to get traffic from WAN into a k8 cluster. Depending on where the k8 cluster is hosted, there
may be additional limitations imposed by the host environment and k8 control plane configuration. Specifically,
Digital Ocean [does not support UDP load balancing](https://ideas.digitalocean.com/ideas/DO-I-310).    


Typically:

0. some service on the k8 cluster is exposed via a [`nodePort`](https://kubernetes.io/docs/concepts/services-networking/service/#nodeport)
1. some provider specific integration with the k8 cluster maps the the intended [`targetPort`](https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service) to the arbitrary `nodePort`
2. additional provider specific integration keeps the list of 'backend' IP addresses and nodes in the k8 cluster with the `nodePort` in sync

The result is that the user can make a request like `udp://some.ip.addy.here:999` and the device living at `some.ip.addy.here` will forward the packet to the appropriate
'backend' servers on the appropriate `nodePort`.

Since my k8 provider does not offer UDP support, I did some research and [found](https://medium.com/asl19-developers/build-your-own-cloud-agnostic-tcp-udp-loadbalancer-for-your-kubernetes-apps-3959335f4ec3) that everybody ends up
creating a standalone reverse proxy node.

This is my own take on creating the proxy and configuring it.


## Example:


Using the CAPP tool is simple. The default command-line arguments are suited for the machine image that Packer creates, but here's a more 'explicit' example.

```bash
# Copy the traefik.init.yaml to traefik.yaml so we have something to diff w/ @ the end.
$ cp example/traefik.init.yaml example/traefik.yaml

# Then run the tool
$ python3 main.py --log-level INFO  --traefik-dynamic-dir ./example/out  --traefik-static-file ./example/traefik.yaml --config-file ./example/in.yaml 
2020-07-20 14:18:20,425: main.py [INFO     ] Fetching the digitalocean provider...
2020-07-20 14:18:20,749: main.py [INFO     ] Configuring provider...
2020-07-20 14:18:20,750: main.py [INFO     ] Fetching IPs from provider...
2020-07-20 14:18:21,568: main.py [INFO     ] Combining IPs for 1 cluster with the 1 clusters from user
2020-07-20 14:18:21,568: main.py [INFO     ] Generating config files...
2020-07-20 14:18:21,568: main.py [INFO     ] Generating the dynamic config for cluster://606aeaef-3829-b234-123456789012
2020-07-20 14:18:21,571: main.py [INFO     ] Generating the static config for cluster://606aeaef-3829-b234-123456789012
2020-07-20 14:18:21,578: main.py [INFO     ] Wrote 4 entrypoints back to static config file
2020-07-20 14:18:21,580: main.py [INFO     ] GoodBye!

# Then check out the diff between the two traefik config files
$ diff example/traefik.init.yaml example/traefik.yaml
1,4d0
< ##
< # This file represents a 'typical' traefik config file. The CAPP tool will parse this file
< # and add any additional entrypoints needed to it. To 'start' only one entrypoint is defined; ping
< ##
8a5,6
>   https:
>     address: :443/tcp
10a9,12
>   some-weird-udp-service:
>     address: :5182/udp
>   some_tcp_svc:
>     address: :999/tcp

```

Notice that in the `traefik.yaml` file we have two new entrypoints: `some-weird-udp-service:` and `some_tcp_svc:`


### Packer

For local testing, I use a virtualbox image. To build only the digitalocean, use:

```bash
./build.sh --only=digitalocean
[I]   Building $BUILD_HASH is at 2941ac6
[I]   Copying CAPP files...
[I]   Building...
digitalocean: output will be in this color.

==> digitalocean: Creating temporary ssh key for droplet...
==> digitalocean: Creating droplet...
==> digitalocean: Waiting for droplet to become active...
<snip>
```
