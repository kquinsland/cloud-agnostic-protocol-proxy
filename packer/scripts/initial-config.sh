#!/bin/bash
##
# Before Salt run, there's a few things that we need to take care of:
#
#   Force all APT repos to HTTPS and tell apt that we never want to accept a HTTPS to HTTP
#       downgrade.
#
#   Prevent any scheduled processess from automatically updating packages, locking apt so salt can't use it
#
#   Install any updates after refreshing using our HTTPS Only apt config and then remove
#       anything that's no longer needed.
##
# Bail if errors
set -e

### Initial setup
# Turn off automatic updates; prevents default ubuntu services from locking apt in the background
#   which will result in an error for our apt needs, which will cause packer to bail on the build.
echo 'APT::Periodic::Enable "0";' >> /etc/apt/apt.conf.d/10periodic

# And we also want all apt activity to be unobtrusive
export DEBIAN_FRONTEND=noninteractive
export DEBIAN_PRIORITY=critical

### Package updates
##
# First, we install apt-transport-https; ask that we only fetch repos over https
echo "initial apt-get update..."
apt-get -qy update -o Acquire::http::AllowRedirect=false
echo "install https transports..."
apt-get -qy install -o Acquire::http::AllowRedirect=false apt-transport-https
echo "initial apt-get upgrade..."
apt-get -qy upgrade -o "Dpkg::Options::=--force-confdef" -o "Dpkg::Options::=--force-confold"

# For some reason, issuing two apt upgrade calls back to back has a high probability of the second one blowing up 
#   and taking the packer run w/ it.
# For reasons that I don't understand, a sleep fixes it!
##
echo "pausing to let apt catch it's breath..."
sleep 5
apt-get -qy update -o Acquire::http::AllowRedirect=false

echo "Fetching updates..."
apt -qy dist-upgrade

# Clean artifacts...
apt-get -qy autoclean
apt-get -qy autoremove
