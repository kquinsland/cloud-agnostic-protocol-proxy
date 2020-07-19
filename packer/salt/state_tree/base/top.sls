##
# The TOP level state for all the various types of hosts that Salt buiilds for Packer
##
# Only 'used' when there is no explicit saltenv set
base:
  # Apply to all hosts
  '*':
    # A few common things
    - common

  # The salt-master image
  'packer-cloud-agnostic-protocol-proxy':
    - traefik
    - capp

# When operating in the digital_ocean environment
#digital_ocean:
