#!/bin/sh

# Define internationalization (i18n)

./tools/maint/init_potfiles.sh

# Replace "gettextize --no-changelog"
autopoint

# Beware of acknowledgment!

sed -i 's/po\/Makefile.in \(po\/Makefile.in *\)*/po\/Makefile.in /' configure.ac
sed -i 's/EXTRA_DIST.*$/EXTRA_DIST = config.rpath  ChangeLog/' Makefile.am

rm po/Makevars.template
cp /usr/share/gettext/gettext.h .

# Create a timestamp mark
echo "timestamp" > stamp-h.in

# As some Makefiles expect an external fragment built dynamically, ensure these files exist
touch plugins/arm/v7/opcodes/gencode.mk
touch plugins/dalvik/v35/opcodes/gencode.mk

touch ChangeLog

# Run the GNU tools
libtoolize --force
aclocal -Im4
autoheader
automake --add-missing --copy
autoconf

# Define the way the program will be built
#  - for development:
#./configure --prefix=/dev/shm/chrysalide --enable-silent-rules --enable-debug --with-local-resources
#  - for production:
#./configure --prefix=/usr/local --enable-silent-rules --disable-rpath
