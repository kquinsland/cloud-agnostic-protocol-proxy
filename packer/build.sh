#!/bin/bash
#
# Crude script to kick off Packer
##

# Set up a few variables we'll need for later
BUILD_TAG="HEAD"
BUILD_HASH=$(git rev-parse --short $BUILD_TAG)
echo "[I]   Building \$BUILD_HASH is at $BUILD_HASH"

# Copy over python code / files
echo "[I]   Copying CAPP files..."
# Make space
mkdir -p salt/state_tree/base/capp/files/
# rsync everything... using a blacklist
rsync -a --exclude-from='.rsync_ignore' ../ salt/state_tree/base/capp/files/

echo "[I]   Building..."
source cloud.auth

# Change into dir w/ all packer vars
cd protocol-proxy
packer build -on-error=ask -var-file=variables.json -var build_hash="$BUILD_HASH" -var build_uuid"=$UUID" -var salt_log_level='debug' $@ packer.json
