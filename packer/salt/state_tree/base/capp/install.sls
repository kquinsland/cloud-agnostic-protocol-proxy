# Set up a venv for the CAPP tool
# See: https://docs.saltstack.com/en/master/ref/states/all/salt.states.virtualenv_mod.html
##

# First, install pip and a few packages necessary for venv creation :)
install_venv_pkgs:
  pkg.installed:
    - pkgs:
      - python3-pip
      - python3-virtualenv

# Then we use the venv module
setup_capp_venv_dir:
  file.directory:
    - name: {{pillar['capp']['path']}}/venv
    # recurse as needed
    - makedirs: True
    - user: {{pillar['capp']['user']}}
    - group: {{pillar['capp']['user']}}
    - dir_mode: 750
    - file_mode: 640
    - recurse:
      - user
      - group
      - mode

# Make sure that the parent dir too the venv is also writable
tweak_capp_venv_dir_perms:
  file.directory:
    - name: {{pillar['capp']['path']}}
    - user: {{pillar['capp']['user']}}
    - group: {{pillar['capp']['user']}}
    - dir_mode: 750
    - file_mode: 640
    - recurse:
      - user
      - group
      - mode

setup_capp_venv:
  virtualenv.managed:
    - name: {{pillar['capp']['path']}}/venv
    - user: {{pillar['capp']['user']}}
    - system_site_packages: False

    # Pass --upgrade to pip install
    - pip_upgrade: True

    - requirements: salt://capp/files/requirements.txt

    # Use system python3
    - python: /usr/bin/python3

install_capp:
  file.recurse:
    - name: {{pillar['capp']['path']}}
    - source: salt://capp/files/
    - user: {{pillar['capp']['user']}}
    - group: {{pillar['capp']['user']}}
    - dir_mode: 750
    - file_mode: 640
    - recurse:
      - user
      - group
      - mode
