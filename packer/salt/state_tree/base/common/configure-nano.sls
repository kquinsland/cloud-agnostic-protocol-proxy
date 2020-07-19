##
# Enhances the Nano text editor with a ton of file format sytax definitions
#
# See: https://github.com/scopatz/nanorc
##
enhance_nano_markup:

  # Salt needs the unzip binary
  pkg.installed:
    - name: unzip

  archive.extracted:
    # When extracted, there will be a ton of *.nanorc files in the dir
    - name: /usr/share/nano/
    # Hashi does not put binary into a folder
    - enforce_toplevel: False
    - source: https://github.com/scopatz/nanorc/archive/master.zip
    # Sadly, no SHA is offered :/
    - skip_verify: True
    # UnZip has no --strip-components=1 equivelent, but it does have a `junk-paths` flag
    #   which ignores the dir struccture of the zip
    # Pass in -n to never overwrite existing files
    # See: https://superuser.com/questions/518347/equivalent-to-tars-strip-components-1-in-unzip
    - options: -j -n
