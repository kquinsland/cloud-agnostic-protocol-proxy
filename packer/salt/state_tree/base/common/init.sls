##
# Init.sls for `common`. That is, all the things that are common to _every_ instance
##
# When the salt state file includes the 'common' state, salt will internally resolve that to common/init.sls
# So this file is where we figure out what "common" means
##
include:

  # Install a few basic packages
  # Remove other packages and set up the prefered substitutions
  - common.packages

  # Enhance the nano text editor so Karl feels @ home
  - common.configure-nano

  # We want to make the SSH experiencce consistent
  - common.configure-ssh

  # Last, we make sure that any security updates are automatically applied
  - common.unattended-upgrades
