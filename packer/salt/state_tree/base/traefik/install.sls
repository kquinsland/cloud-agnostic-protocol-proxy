# Installs the Traefik proxy an installs a basic static config file
#
# Traefik is a golang.... so just download the binary and rur it !
# See: https://github.com/containous/traefik/releases
##

# See: https://docs.saltstack.com/en/latest/ref/states/all/salt.states.user.html
traefik_user:
  # Make a user for the group
  user.present:
    - name: {{pillar['traefik']['config']['user']}}
    # Traefik is not running in a container so we create a system level user for traefik
    - system: True
    # Traefik requires no shell
    - shell: /bin/false
    # Make a group identical to user name, add user to that grooup
    - usergroup: True

##
# User/Group exist, fetch the binary
download_traefik:
  archive.extracted:
    #  When extracted, there will be a traefik binary at /usr/local/bin/traefik
    - name: /usr/local/bin/
    - enforce_toplevel: false
    - source: https://github.com/containous/traefik/releases/download/{{ pillar['traefik']['version']}}/traefik_{{ pillar['traefik']['version']}}_linux_amd64.tar.gz
    - source_hash: https://github.com/containous/traefik/releases/download/{{ pillar['traefik']['version']}}/traefik_{{ pillar['traefik']['version']}}_checksums.txt
    # Root owns...
    - user: root
    - group: root
    - mode: 0700

##
# We deploy the static config file...
configure_traefik_static:
  file.managed:
    - makedirs: True
    - name: {{pillar['traefik']['config']['path']}}/traefik.yaml
    - source: salt://traefik/files/debian/config/traefik.yaml
    # Root owns so that traefik *cant* overwrite it's own config file
    - user: root
    - group: {{pillar['traefik']['config']['group']}}
    - mode: 040
    - template: jinja
    - defaults:
        dynamic_config_dir: {{pillar['traefik']['dynamic']['path']}}


##
# Create the space for TLS certificates
configure_traefik_tls:
  file.directory:
    - name: {{pillar['traefik']['tls']['path']}}/
    - user: {{pillar['traefik']['tls']['user']}}
    - group: {{pillar['traefik']['tls']['group']}}
    - dir_mode: 750
    - file_mode: 640
    - recurse:
      - user
      - group
      - mode

##
# create space on disk
configure_traefik_dynamic_dir:
  file.directory:
    - name: {{pillar['traefik']['dynamic']['path']}}
    - user: {{pillar['traefik']['config']['user']}}
    - group: {{pillar['traefik']['config']['group']}}
    - dir_mode: 550
    - file_mode: 440
    - recurse:
      - user
      - group
      - mode

##
# At this point, we have a user/group + a binary and basic config on disk.
# Plug the binary into systemd so it'll be started when the machine is next booted!
##
traefik_service:
  file.managed:
    - makedirs: True
    - name: /etc/systemd/system/traefik.service
    - source: salt://traefik/files/debian/systemd/traefik.service
    - user: root
    - group: root
    - mode: 0755
    - template: jinja
    - defaults:
        user: {{pillar['traefik']['config']['user']}}
        group: {{pillar['traefik']['config']['group']}}

        # Pass in the tls/dynamic config dirs
        tls_dir: {{pillar['traefik']['tls']['path']}}/
        config_dir: {{pillar['traefik']['dynamic']['path']}}
        
        # And the full path to the static config file
        static_config: {{pillar['traefik']['config']['path']}}/traefik.yaml

  # If the service file changed, we need to reload the changes..
  module.run:
    - name: service.systemctl_reload
    - onchanges:
      - file: traefik_service

  # In any event, we want to make sure the service is enabled so it will be running on next boot
  service.enabled:
    - name: traefik.service
    # Make sure that it'll start @ boot
    - enable: True
