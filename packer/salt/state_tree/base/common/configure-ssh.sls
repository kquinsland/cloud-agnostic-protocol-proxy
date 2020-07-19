##
# We want the banner/motd to be the same across all instance
###

# We make a few tweaks to the MOTD banner, too
configure_ssh_motd:
  # Install the figlet tool whhich makes nice ASCII art 
  pkg.installed:
    - name: figlet

  # Then deploy a small shell sccript that'll get executed
  #     when the motd is requested (bby sshd)
  file.managed:
   - name: /etc/update-motd.d/100-kq
   - source: salt://common/files/ubuntu/etc/update-motd.d/100-kq
   - user: root
   - group: root
   - mode: 0755

disable_ssh_banner_help_text:
  file.managed:
   - name: /etc/update-motd.d/10-help-text
   # Normally: 755, but we want to -x it
   - mode: 444

# And now we need to disable the part of /etc/motd generation that phones home to Canonical
disable_ssh_motd_news:
  file.managed:
   - name: /etc/default/motd-news
   - source: salt://common/files/ubuntu/etc/default/motd-news
   - user: root
   - group: root
   - mode: 0644
