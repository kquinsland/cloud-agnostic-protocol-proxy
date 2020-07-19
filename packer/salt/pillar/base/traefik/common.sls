
traefik:
  # Version of binary to fetch.
  # See: https://github.com/containous/traefik/releases/
  ##
  version: v2.2.6

  # The user/group traefik coonfig will be owned by
  config:
    user: traefik
    group: traefik
    path: /etc/traefik
  
  # The dynamic configuration will live here
  dynamic:
    path: /etc/traefik/dynamic

  # Note: not used by CAPP
  tls:
    user: traefik
    group: traefik
    path: /etc/traefik/tls

  # Logs
  log:
    user: traefik
    group: traefik
    path: /var/log/traefik
