##
# A few basic packages that make the host a bit easier to use
basic_packages:
  pkg.installed:
    - pkgs:
      - curl
      - gnupg2
      - git
      - htop
      - jq
      - nano
      - software-properties-common
      - ca-certificates
      # Netstat!
      - net-tools

# We also want to remove snap* from ubuntu
no_snapd:
  pkg.purged:
    - pkgs:
      - snapd
      - gnome-software-plugin-snap

##
# remove the haveged daemon as it's not needed, replace w/ newer and better
remove_haveged:
  pkg.purged:
    - name: haveged

install_rng:
  pkg.latest:
    - name: rng-tools
