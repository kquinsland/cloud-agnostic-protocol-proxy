##
# Deposits the dpkg unattended upgrades configuration files
# See: https://wiki.debian.org/UnattendedUpgrades
##

install_unattended_upgrade:
  pkg.latest:
    - pkgs:
      - apt-listchanges
      - unattended-upgrades

unattended_upgrade:
  file.managed:
   - name: /etc/apt/apt.conf.d/20auto-upgrades
   - source: salt://common/files/ubuntu/unattended-upgrade/20auto-upgrades
   # Create nested dirs
   - makedirs: True
   - user: root
   - group: root
   - mode: 0644

unattended_upgrade_list_changes:
  file.managed:
   - name: /etc/apt/apt.conf.d/20listchanges
   - source: salt://common/files/ubuntu/unattended-upgrade/20listchanges
   # Create nested dirs
   - makedirs: True
   - user: root
   - group: root
   - mode: 0644
