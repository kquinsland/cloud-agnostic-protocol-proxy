##
# Init.sls for `traefik`
# When the salt state file includes the 'traefik' state, salt will internally resolve that to traefik/init.sls
# So this file is where we figure out what "traefik" means
##
include:
  # Traefik is a static golang binary and a systemd service file
  - traefik.install
