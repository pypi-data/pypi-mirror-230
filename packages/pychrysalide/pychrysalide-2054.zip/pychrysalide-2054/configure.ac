# Process this file with autoconf to produce a configure script.

############################################################
# Autoconf requirements
############################################################

m4_include([gitrev.m4])

AC_PREREQ([2.71])
AC_INIT([chrysalide],[gitversion],[nocbos@gmail.com])

AC_CONFIG_HEADERS([config.h])
AC_CONFIG_MACRO_DIR([m4])

AM_INIT_AUTOMAKE
AM_SILENT_RULES

AM_GNU_GETTEXT_VERSION([0.18.3])
AM_GNU_GETTEXT([external])

AC_CONFIG_SRCDIR([src/main.c])


############################################################
# Information on the package
############################################################

#--- Checks for programs

AC_PROG_CC
AM_PROG_CC_C_O
AC_PROG_LEX
AC_PROG_YACC
AC_PROG_INSTALL
AC_PROG_MAKE_SET
LT_INIT

CFLAGS=""

AC_EGREP_CPP(yes,
[#ifdef __PIE__
  yes
#endif
], has_default_pie=yes, has_default_pie=no)

if test "x$has_default_pie" = "xyes"; then
   CFLAGS="$CFLAGS -fPIC"
fi

AC_PATH_PROG(YACC_INST, $YACC)
AC_PATH_PROG(LEX_INST, $LEX)


#--- Checks for CPU

AX_EXT


#--- Checks for libraries

AC_CHECK_LIB([dl], [dlopen])


#--- Checks for header files

AC_HEADER_DIRENT
AC_HEADER_STDBOOL
m4_warn([obsolete],
[The preprocessor macro `STDC_HEADERS' is obsolete.
  Except in unusual embedded environments, you can safely include all
  ISO C90 headers unconditionally.])dnl
# Autoupdate added the next two lines to ensure that your configure
# script's behavior did not change.  They are probably safe to remove.
AC_CHECK_INCLUDES_DEFAULT
AC_PROG_EGREP

AC_CHECK_HEADERS([malloc.h])
AC_CHECK_HEADERS([netdb.h])
AC_CHECK_HEADERS([stdlib.h])
AC_CHECK_HEADERS([string.h])
AC_CHECK_HEADERS([unistd.h])


#--- Checks for types

AC_TYPE_SIZE_T

AC_MSG_CHECKING([for suitable size_t])
AC_COMPILE_IFELSE( [AC_LANG_PROGRAM([[#include <stddef.h>]],
                                    [[char dummy[sizeof(size_t) == sizeof(unsigned long) ? 1 : -1];]])],
                   [
                      AC_MSG_RESULT([yes])
                      suitable_size_t=yes
                    ],
                    [
                      AC_MSG_RESULT([no])
                      suitable_size_t=no
                    ]
                 )

if test "x$suitable_size_t" = "xno"; then
   AC_MSG_FAILURE([Current size of size_t is not supported])
fi


#--- Checks for structures

AC_STRUCT_TM


#--- Checks for compiler characteristics

AC_C_CONST


#--- Checks for library functions

AC_FUNC_CLOSEDIR_VOID
AC_FUNC_MALLOC
AC_FUNC_REALLOC
AC_FUNC_STAT
AC_FUNC_STRFTIME
AC_FUNC_VPRINTF

AC_CHECK_FUNCS([pow])
AC_CHECK_FUNCS([regcomp])
AC_CHECK_FUNCS([strdup])
AC_CHECK_FUNCS([strerror])
AC_CHECK_FUNCS([strndup])
AC_CHECK_FUNCS([strrchr])


#--- Checks for system services



#--- Autoheader Macros

AH_TEMPLATE([REVISION], [Define the version number of the program for the about box.])
AH_TEMPLATE([PACKAGE_SOURCE_DIR], [Define the directory where the code source is waiting for being compiled.])
AH_TEMPLATE([PIXMAPS_DIR], [Define the directory where the pictures will be installed.])
AH_TEMPLATE([THEMES_DIR], [Define the main directory where all themes will be installed.])
AH_TEMPLATE([PLUGINS_LIB_DIR], [Define the directory where the plugin librairies are installed.])
AH_TEMPLATE([PLUGINS_DATA_DIR], [Define the directory where the plugin data is installed.])
AH_TEMPLATE([BUILD_PREFIX_DIR], [Define the prefix for all installation directories.])
AH_TEMPLATE([LOCALE_DIR], [Define the directory where the message catalogs are installed.])


AC_DEFINE_UNQUOTED(REVISION, AC_PACKAGE_VERSION)

packagesrcdir=`cd $srcdir && pwd`
AC_DEFINE_UNQUOTED(PACKAGE_SOURCE_DIR, "${packagesrcdir}")


AC_LIB_PREPARE_PREFIX


basedir=${datadir}/${PACKAGE}

while : ; do
   oldbasedir=${basedir}
   AC_LIB_WITH_FINAL_PREFIX([basedir=$(eval echo ${basedir} )])
   test ${oldbasedir} = ${basedir} && break
done

if echo ${basedir} | grep -q '^NONE'; then
   AC_MSG_FAILURE([NONE found in \$datadir])
fi


pixmapsdir="${basedir}/pixmaps"
AC_SUBST(pixmapsdir)

AC_DEFINE_UNQUOTED(PIXMAPS_DIR, "${pixmapsdir}")

themesdir="${basedir}/themes"
AC_SUBST(themesdir)

AC_DEFINE_UNQUOTED(THEMES_DIR, "${themesdir}")

pluginsdatadir="${basedir}/plugins"
AC_SUBST(pluginsdatadir)

AC_DEFINE_UNQUOTED(PLUGINS_DATA_DIR, "${pluginsdatadir}")


basedir=${libdir}/${PACKAGE}-plugins

while : ; do
   oldbasedir=${basedir}
   AC_LIB_WITH_FINAL_PREFIX([basedir=$(eval echo ${basedir} )])
   test ${oldbasedir} = ${basedir} && break
done

if echo ${basedir} | grep -q '^NONE'; then
   AC_MSG_FAILURE([NONE found in \$libdir])
fi


pluginslibdir="${basedir}"
AC_SUBST(pluginslibdir)

AC_DEFINE_UNQUOTED(PLUGINS_LIB_DIR, "${pluginslibdir}")


basedir=${prefix}

while : ; do
   oldbasedir=${basedir}
   AC_LIB_WITH_FINAL_PREFIX([basedir=$(eval echo ${basedir} )])
   test ${oldbasedir} = ${basedir} && break
done

if echo ${basedir} | grep -q '^NONE'; then
   AC_MSG_FAILURE([NONE found in \$prefix])
fi

AC_DEFINE_UNQUOTED(BUILD_PREFIX_DIR, "${basedir}")

AC_DEFINE_UNQUOTED(LOCALE_DIR, "${basedir}/share/locale")



############################################################
# Compilation options
############################################################

AC_ARG_ENABLE([debug],
              AS_HELP_STRING([--enable-debug], [compile with debugging support [default=no]]),
              [], [enable_debug=no])

AC_ARG_ENABLE([gtk-support],
              AS_HELP_STRING([--disable-gtk-support], [disable GTK support [default=no]]),
              [], [enable_gtk_support=yes])

AC_ARG_ENABLE([curl-support],
              AS_HELP_STRING([--disable-curl-support], [disable cURL support [default=no]]),
              [], [enable_curl_support=yes])

AC_ARG_ENABLE([magic-support],
              AS_HELP_STRING([--disable-magic-support], [disable magic number recognition [default=no]]),
              [], [enable_magic_support=yes])

AC_ARG_ENABLE([python-bindings],
              AS_HELP_STRING([--disable-python-bindings], [disable Python bindings [default=no]]),
              [], [enable_python_bindings=yes])

AC_ARG_ENABLE([python-package],
              AS_HELP_STRING([--enable-python-package], [configure the compilation for building a Python binary distribution [default=no]]),
              [build_python_package=$enableval], [build_python_package=no])

AC_ARG_WITH([gobject-leak-tracker],
            AS_HELP_STRING([--with-gobject-leak-tracker],
            [track remaining GObject instances at exit (imply --enable-debug and GLib support) [default=no]]),
            [], [with_gobject_leak_tracker=no])

AC_ARG_WITH([desktop-dir],
            AS_HELP_STRING([--with-desktop-dir=PATH],
            [specify to destination of desktop files (default=PREFIX/share)]))

AC_ARG_WITH([local-resources],
            AS_HELP_STRING([--with-local-resources],
            [define if built components located in the sources are used at runtime [default=no]]),
            [with_local_resources=$withval], [with_local_resources=no])


AM_CONDITIONAL([BUILD_PYTHON_PACKAGE], [test "x$build_python_package" = "xyes"])

AM_CONDITIONAL([BUILD_DISCARD_LOCAL], [test "x$with_local_resources" = "xno"])


#-- Delete all kinds of runtime library paths?

if test "x$enable_rpath" = "xno"; then
   hardcode_into_libs=no
fi


#--- Small enumerations and other basic flags

CPPFLAGS="$CPPFLAGS -D_LARGEFILE64_SOURCE"

CFLAGS="$CFLAGS -fshort-enums"


#--- Build binaries for Python package only?

if test "x$build_python_package" = "xyes"; then
   CPPFLAGS="$CPPFLAGS -DPYTHON_PACKAGE"
fi


#--- Discard local sources when looking for resources?

if test "x$with_local_resources" = "xno"; then
   CPPFLAGS="$CPPFLAGS -DDISCARD_LOCAL"
fi


#--- Is debug mode needed?

AM_CONDITIONAL([TRACK_GOBJECT_LEAKS], [test "x$with_gobject_leak_tracker" = "xyes"])

if test "x$with_gobject_leak_tracker" = "xyes"; then
   # Enable code for dumping remaining GObject instances at exit
   CPPFLAGS="$CPPFLAGS -DTRACK_GOBJECT_LEAKS"
   enable_debug="yes"
fi

if test "x$enable_debug" = "xyes"; then
   DEBUG_CPPFLAGS="-DDEBUG"
   DEBUG_CFLAGS="-O0 -ggdb -gdwarf-2"
else
   DEBUG_CPPFLAGS="-Ofast -DNDEBUG"
fi


#--- Compilation warnings

WARNING_CFLAGS="-Wall -Wimplicit -Wreturn-type -Wunused -Wswitch -Wcomment -Wuninitialized -Wparentheses -Wpointer-arith -Wmissing-prototypes"

#-Wcast-qual -Wconversion -Wsign-compare -Wdisabled-optimization

# _BSD_SOURCE: htobe64, be64toh
# _XOPEN_SOURCE: strdup, snprintf
# _ISOC99_SOURCE: INFINITY; NAN
# _GNU_SOURCE: strcasestr
# GTK_DISABLE_DEPRECATED: on reste conforme au C99
#COMPLIANCE_FLAGS="-D_BSD_SOURCE -D_GNU_SOURCE -DGTK_DISABLE_DEPRECATED"
COMPLIANCE_CPPFLAGS="-D_DEFAULT_SOURCE -D_GNU_SOURCE"


#--- Final exports

CPPFLAGS="$CPPFLAGS $DEBUG_CPPFLAGS $COMPLIANCE_CPPFLAGS"
CFLAGS="$CFLAGS $DEBUG_CFLAGS $WARNING_CFLAGS"

AC_SUBST(CPPFLAGS)
AC_SUBST(CFLAGS)


#--- Custom destination for desktop resources?

if test "x$with_desktop_dir" != x; then
   DESKTOP_DATADIR=$with_desktop_dir
else
   DESKTOP_DATADIR="$datadir"
fi

AM_CONDITIONAL(DESKTOP_DATADIR, test "x$with_desktop_dir" != xno)
AC_SUBST(DESKTOP_DATADIR)


#--- Checks for GTK 3.0 / GObject 2.0

AM_CONDITIONAL([BUILD_GTK_SUPPORT], [test "x$enable_gtk_support" = "xyes"])

if test "x$BUILD_GTK_SUPPORT_TRUE" = "x"; then
   # GTK support is available and enabled
   CPPFLAGS="$CPPFLAGS -DINCLUDE_GTK_SUPPORT"
fi


PKG_CHECK_MODULES(LIBGOBJ,gobject-2.0 >= 2.66.8,[libgobj_found=yes],[libgobj_found=no])

if test "$libgobj_found" = "yes"; then
   libgobj_version=`pkg-config gobject-2.0 --modversion`
else
   libgobj_version='-'
fi

PKG_CHECK_MODULES(LIBGTHREAD,gthread-2.0 >= 2.66.8,[libgthread_found=yes],[libgthread_found=no])

if test "$libgthread_found" = "yes"; then
   libgthread_version=`pkg-config gthread-2.0 --modversion`
else
   libgthread_version='-'
fi

PKG_CHECK_MODULES(LIBGMOD,gmodule-2.0 >= 2.66.8,[libgmod_found=yes],[libgmod_found=no])

if test "$libgmod_found" = "yes"; then
   libgmod_version=`pkg-config gmodule-2.0 --modversion`
else
   libgmod_version='-'
fi


PKG_CHECK_MODULES(LIBGTK,gtk+-3.0 >= 3.8.6,[libgtk_found=yes],[libgtk_found=no])

if test "$libgtk_found" = "yes"; then
   libgtk_version=`pkg-config gtk+-3.0 --modversion`
else
   libgtk_version='-'
fi


if test "x$enable_gtk_support" = "xyes"; then

    TOOLKIT_CFLAGS="$LIBGTK_CFLAGS $LIBGTHREAD_CFLAGS $LIBGMOD_CFLAGS"
    TOOLKIT_LIBS="$LIBGTK_LIBS $LIBGTHREAD_LIBS $LIBGMOD_LIBS"

    AC_SUBST(TOOLKIT_CFLAGS)
    AC_SUBST(TOOLKIT_LIBS)

else

    TOOLKIT_CFLAGS="$LIBGOBJ_CFLAGS $LIBGTHREAD_CFLAGS $LIBGMOD_CFLAGS"
    TOOLKIT_LIBS="$LIBGOBJ_LIBS $LIBGTHREAD_LIBS $LIBGMOD_LIBS"

    AC_SUBST(TOOLKIT_CFLAGS)
    AC_SUBST(TOOLKIT_LIBS)

fi


#--- Checks for libxml2

PKG_CHECK_MODULES(LIBXML,libxml-2.0 >= 2.6.11,[libxml_found=yes],[libxml_found=no])

if test "$libxml_found" = "yes"; then
   libxml_version=`pkg-config libxml-2.0 --modversion`
else
   libxml_version='-'
fi

AC_SUBST(LIBXML_CFLAGS)
AC_SUBST(LIBXML_LIBS)


#--- Checks for libarchive

PKG_CHECK_MODULES(LIBARCHIVE,libarchive >= 3.1.2,[libarchive_found=yes],[libarchive_found=no])

if test "$libarchive_found" = "yes"; then
   libarchive_version=`pkg-config libarchive --modversion`
else
   libarchive_version='-'
fi

AC_SUBST(LIBARCHIVE_CFLAGS)
AC_SUBST(LIBARCHIVE_LIBS)


#--- Checks for libsqlite

PKG_CHECK_MODULES(LIBSQLITE,sqlite3 >= 3.8.2,[libsqlite_found=yes],[libsqlite_found=no])

if test "$libsqlite_found" = "yes"; then
   libsqlite_version=`pkg-config sqlite3 --modversion`
else
   libsqlite_version='-'
fi

AC_SUBST(LIBSQLITE_CFLAGS)
AC_SUBST(LIBSQLITE_LIBS)


#--- Checks for libssl

PKG_CHECK_MODULES(LIBSSL,openssl >= 3.0.9,[libssl_found=yes],[libssl_found=no])

if test "$libssl_found" = "yes"; then
   libssl_version=`pkg-config openssl --modversion`
else
   libssl_version='-'
fi

AC_SUBST(LIBSSL_CFLAGS)
AC_SUBST(LIBSSL_LIBS)


#--- Checks for libcurl

AM_CONDITIONAL([BUILD_CURL_SUPPORT], [test "x$enable_curl_support" = "xyes"])

if test "x$BUILD_CURL_SUPPORT_TRUE" = "x"; then
   # cURL support is available and enabled
   CPPFLAGS="$CPPFLAGS -DINCLUDE_CURL_SUPPORT"
fi


PKG_CHECK_MODULES(LIBCURL,libcurl >= 7.64,[libcurl_found=yes],[libcurl_found=no])

if test "$libcurl_found" = "yes"; then
   libcurl_version=`pkg-config libcurl --modversion`
else
   libcurl_version='-'
fi

if test "x$enable_curl_support" = "xyes"; then

   AC_SUBST(LIBCURL_CFLAGS)
   AC_SUBST(LIBCURL_LIBS)

   true # empty if/then body not allowed

fi


#--- Checks for libyaml

PKG_CHECK_MODULES(LIBYAML,yaml-0.1 >= 0.2.5,[libyaml_found=yes],[libyaml_found=no])

if test "$libyaml_found" = "yes"; then
   libyaml_version=`pkg-config yaml-0.1 --modversion`
else
   libyaml_version='-'
fi

AC_SUBST(LIBYAML_CFLAGS)
AC_SUBST(LIBYAML_LIBS)


#--- Checks for libmagic

AM_CONDITIONAL([BUILD_MAGIC_SUPPORT], [test "x$enable_magic_support" = "xyes"])

if test "x$BUILD_MAGIC_SUPPORT_TRUE" = "x"; then
   # Magic support is available and enabled
   CPPFLAGS="$CPPFLAGS -DINCLUDE_MAGIC_SUPPORT"
fi


PKG_CHECK_MODULES(LIBMAGIC,libmagic >= 5.44,[libmagic_found=yes],[libmagic_found=no])

if test "$libmagic_found" = "yes"; then
   libmagic_version=`pkg-config libmagic --modversion`
else
   libmagic_version='-'
fi


if test "x$enable_magic_support" = "xyes"; then

   AC_SUBST(LIBMAGIC_CFLAGS)
   AC_SUBST(LIBMAGIC_LIBS)

   true # empty if/then body not allowed

fi


#--- Checks for Python

if test "x$enable_debug" = "xyes"; then
   AC_CHECK_PROG(python3_cfg_binary, [python3-dbg-config] , yes)
else
   AC_CHECK_PROG(python3_cfg_binary, [python3-config] , yes)
fi

AM_CONDITIONAL([BUILD_PYTHON3_BINDINGS], [test "x$enable_python_bindings$python3_cfg_binary" = "xyesyes"])

if test "x$BUILD_PYTHON3_BINDINGS_TRUE" = "x"; then
   # Python bindings are available and enabled
   CPPFLAGS="$CPPFLAGS -DINCLUDE_PYTHON3_BINDINGS"
fi

if test "x$python3_cfg_binary" = "xyes"; then

   if test "x$enable_debug" = "xyes"; then
      pyprefix="python3-dbg"
   else
      pyprefix="python3"
   fi

   LIBPYTHON_CFLAGS=`$pyprefix-config --cflags`
   LIBPYTHON_LIBS=`$pyprefix-config --libs`
   LIBPYTHON_INTERPRETER_CFLAGS="`$pyprefix-config --cflags --embed` -DPY_SSIZE_T_CLEAN"
   LIBPYTHON_INTERPRETER_LIBS=`$pyprefix-config --libs --embed`
   LIBPYTHON_ABI_FLAGS=`$pyprefix-config --abiflags`
   pythondep=$pyprefix

   AC_SUBST(LIBPYTHON_CFLAGS)
   AC_SUBST(LIBPYTHON_LIBS)
   AC_SUBST(LIBPYTHON_INTERPRETER_CFLAGS)
   AC_SUBST(LIBPYTHON_INTERPRETER_LIBS)
   AC_DEFINE_UNQUOTED(LIBPYTHON_ABI_FLAGS, "${LIBPYTHON_ABI_FLAGS}", [ABI flags of the linked Python library])

   if test "x$enable_python_bindings" = "xyes"; then
      python3_version=`$pyprefix --version | cut -d ' ' -f 2`
   else
      python3_version="`$pyprefix --version | cut -d ' ' -f 2` (skipped)"
   fi

else

   pythondep=
   python3_version='-'

fi


#--- Checks for pygobject-3.0

PKG_CHECK_MODULES(LIBPYGOBJECT,pygobject-3.0 >= 3.12.1,[libpygobject_found=yes],[libpygobject_found=no])

if test "$libpygobject_found" = "yes"; then
   if test "x$enable_python_bindings" = "xyes"; then
      libpygobject_version=`pkg-config pygobject-3.0 --modversion`
   else
      libpygobject_version="`pkg-config pygobject-3.0 --modversion` (skipped)"
   fi

   if test "x$pythondep" = "x"; then
      pythondep="pygobject-3.0"
   else
      pythondep="$pythondep pygobject-3.0"
   fi

else
   libpygobject_version='-'
fi

AC_SUBST(LIBPYGOBJECT_CFLAGS)
AC_SUBST(LIBPYGOBJECT_LIBS)

AC_SUBST(pythondep)


############################################################
# Outputting files
############################################################

AC_CONFIG_FILES([stamp-h po/Makefile.in], [echo timestamp > stamp-h])

AC_CONFIG_COMMANDS([marshal], [echo -e "VOID:UINT64\nVOID:INT,UINT64,INT\nVOID:OBJECT,OBJECT\nVOID:ENUM,OBJECT\nVOID:ENUM,ENUM\nVOID:BOOLEAN,UINT64\nVOID:BOOLEAN,ULONG,ULONG\nVOID:INT,INT\nVOID:OBJECT,BOOLEAN\nVOID:ULONG,BOOLEAN\nVOID:DOUBLE,DOUBLE" > src/glibext/chrysamarshal.list])

AC_CONFIG_FILES([Makefile
                 doc/Makefile
                 pixmaps/Makefile
                 plugins/Makefile
                 plugins/arm/Makefile
                 plugins/arm/python/Makefile
                 plugins/arm/python/v7/Makefile
                 plugins/arm/v7/Makefile
                 plugins/arm/v7/opdefs/Makefile
                 plugins/arm/v7/opcodes/Makefile
                 plugins/arm/v7/operands/Makefile
                 plugins/arm/v7/registers/Makefile
                 plugins/bhash/Makefile
                 plugins/bhash/python/Makefile
                 plugins/bootimg/Makefile
                 plugins/bootimg/python/Makefile
                 plugins/dalvik/Makefile
                 plugins/dalvik/operands/Makefile
                 plugins/dalvik/pseudo/Makefile
                 plugins/dalvik/python/Makefile
                 plugins/dalvik/python/v35/Makefile
                 plugins/dalvik/v35/Makefile
                 plugins/dalvik/v35/opcodes/Makefile
                 plugins/dalvik/v35/opdefs/Makefile
                 plugins/devdbg/Makefile
                 plugins/dex/Makefile
                 plugins/dex/python/Makefile
                 plugins/dexbnf/Makefile
                 plugins/dexbnf/python/Makefile
                 plugins/dwarf/Makefile
                 plugins/dwarf/v2/Makefile
                 plugins/dwarf/v3/Makefile
                 plugins/dwarf/v4/Makefile
                 plugins/elf/Makefile
                 plugins/elf/python/Makefile
                 plugins/fmtp/Makefile
                 plugins/gdbrsp/Makefile
                 plugins/gdbrsp/python/Makefile
                 plugins/itanium/Makefile
                 plugins/itanium/python/Makefile
                 plugins/java/Makefile
                 plugins/javadesc/Makefile
                 plugins/javadesc/python/Makefile
                 plugins/kaitai/Makefile
                 plugins/kaitai/parsers/Makefile
                 plugins/kaitai/records/Makefile
                 plugins/kaitai/python/Makefile
                 plugins/kaitai/python/parsers/Makefile
                 plugins/kaitai/python/records/Makefile
                 plugins/libcsem/Makefile
                 plugins/lnxsyscalls/Makefile
                 plugins/mobicore/Makefile
                 plugins/pe/Makefile
                 plugins/pe/python/Makefile
                 plugins/pychrysalide/Makefile
                 plugins/pychrysalide/analysis/Makefile
                 plugins/pychrysalide/analysis/contents/Makefile
                 plugins/pychrysalide/analysis/db/Makefile
                 plugins/pychrysalide/analysis/db/items/Makefile
                 plugins/pychrysalide/analysis/disass/Makefile
                 plugins/pychrysalide/analysis/scan/Makefile
                 plugins/pychrysalide/analysis/scan/patterns/Makefile
                 plugins/pychrysalide/analysis/scan/patterns/backends/Makefile
                 plugins/pychrysalide/analysis/scan/patterns/modifiers/Makefile
                 plugins/pychrysalide/analysis/storage/Makefile
                 plugins/pychrysalide/analysis/types/Makefile
                 plugins/pychrysalide/arch/Makefile
                 plugins/pychrysalide/arch/instructions/Makefile
                 plugins/pychrysalide/arch/operands/Makefile
                 plugins/pychrysalide/common/Makefile
                 plugins/pychrysalide/core/Makefile
                 plugins/pychrysalide/debug/Makefile
                 plugins/pychrysalide/format/Makefile
                 plugins/pychrysalide/glibext/Makefile
                 plugins/pychrysalide/gtkext/Makefile
                 plugins/pychrysalide/gtkext/graph/Makefile
                 plugins/pychrysalide/gui/Makefile
                 plugins/pychrysalide/gui/core/Makefile
                 plugins/pychrysalide/gui/panels/Makefile
                 plugins/pychrysalide/mangling/Makefile
                 plugins/pychrysalide/plugins/Makefile
                 plugins/python/Makefile
                 plugins/python/abackup/Makefile
                 plugins/python/apkfiles/Makefile
                 plugins/python/cglimpse/Makefile
                 plugins/python/checksec/Makefile
                 plugins/python/liveconv/Makefile
                 plugins/python/scripting/Makefile
                 plugins/readdex/Makefile
                 plugins/readelf/Makefile
                 plugins/readmc/Makefile
                 plugins/ropgadgets/Makefile
                 plugins/winordinals/Makefile
                 plugins/winordinals/python/Makefile
                 plugins/yaml/Makefile
                 plugins/yaml/python/Makefile
                 src/Makefile
                 src/analysis/Makefile
                 src/analysis/contents/Makefile
                 src/analysis/db/Makefile
                 src/analysis/db/items/Makefile
                 src/analysis/db/misc/Makefile
                 src/analysis/disass/Makefile
                 src/analysis/human/Makefile
                 src/analysis/human/asm/Makefile
                 src/analysis/scan/Makefile
                 src/analysis/scan/exprs/Makefile
                 src/analysis/scan/items/Makefile
                 src/analysis/scan/items/console/Makefile
                 src/analysis/scan/items/magic/Makefile
                 src/analysis/scan/items/math/Makefile
                 src/analysis/scan/items/string/Makefile
                 src/analysis/scan/items/time/Makefile
                 src/analysis/scan/matches/Makefile
                 src/analysis/scan/patterns/Makefile
                 src/analysis/scan/patterns/backends/Makefile
                 src/analysis/scan/patterns/modifiers/Makefile
                 src/analysis/scan/patterns/tokens/Makefile
                 src/analysis/scan/patterns/tokens/nodes/Makefile
                 src/analysis/storage/Makefile
                 src/analysis/types/Makefile
                 src/arch/Makefile
                 src/arch/instructions/Makefile
                 src/arch/operands/Makefile
                 src/common/Makefile
                 src/core/Makefile
                 src/debug/Makefile
                 src/format/Makefile
                 src/glibext/Makefile
                 src/glibext/generators/Makefile
                 src/gtkext/Makefile
                 src/gtkext/graph/Makefile
                 src/gui/Makefile
                 src/gui/core/Makefile
                 src/gui/dialogs/Makefile
                 src/gui/menus/Makefile
                 src/gui/panels/Makefile
                 src/gui/tb/Makefile
                 src/mangling/Makefile
                 src/plugins/Makefile
                 tools/Makefile
                 tools/d2c/Makefile
                 tools/d2c/args/Makefile
                 tools/d2c/assert/Makefile
                 tools/d2c/bits/Makefile
                 tools/d2c/conv/Makefile
                 tools/d2c/desc/Makefile
                 tools/d2c/format/Makefile
                 tools/d2c/hooks/Makefile
                 tools/d2c/id/Makefile
                 tools/d2c/pattern/Makefile
                 tools/d2c/rules/Makefile
                 system/Makefile
                 system/desktop/Makefile
                 system/pkgconfig/Makefile
                 themes/Makefile
                 themes/Adwaita/Makefile
                 themes/Solarized/Makefile
                 themes/emacs/Makefile])

AC_CONFIG_FILES([system/pkgconfig/chrysalide.pc])

AC_OUTPUT


echo
echo -n $PACKAGE r
echo AC_PACKAGE_VERSION

echo
echo The GLib type, object and signal library..... : $libgobj_version
echo The thread support for GLib.................. : $libgthread_version
echo The dynamic module loader for GLib........... : $libgmod_version
echo The GNU Image Manipulation Program Toolkit... : $libgtk_version
echo The XML C parser and toolkit of Gnome........ : $libxml_version
echo The flexible interface for archives I/O...... : $libarchive_version
echo The small, fast and reliable database engine. : $libsqlite_version
echo The cryptography and SSL/TLS toolkit......... : $libssl_version
echo The client URL library....................... : $libcurl_version
echo The YAML support library..................... : $libyaml_version
echo The magic number recognition library......... : $libmagic_version

echo
echo Available Python programming language........ : $python3_version
echo The Python GObject bindings.................. : $libpygobject_version

echo
echo Found lexical analyzer generator............. : $LEX_INST
echo Found general-purpose parser generator....... : $YACC_INST

if test "x$enable_gtk_support" = "xyes"; then
   disable_gtk_support="no"
else
   disable_gtk_support="yes"
fi

if test "x$enable_curl_support" = "xyes"; then
   disable_curl_support="no"
else
   disable_curl_support="yes"
fi

if test "x$enable_magic_support" = "xyes"; then
   disable_magic_support="no"
else
   disable_magic_support="yes"
fi

if test "x$enable_python_bindings" = "xyes"; then
   disable_python_bindings="no"
else
   disable_python_bindings="yes"
fi

echo
echo Print debugging messages..................... : $enable_debug
echo Consider local resources..................... : $with_local_resources
echo Disable GTK support.......................... : $disable_gtk_support
echo Disable cURL support......................... : $disable_curl_support
echo Disable Magic support........................ : $disable_magic_support
echo Disable Python bindings...................... : $disable_python_bindings
echo Build a Python binary distribution........... : $build_python_package

if test "$disable_python_bindings" = "yes" -a "x$build_python_package" = "xyes"; then

   echo

   m4_define([python_target_warning],[m4_joinall([m4_newline([])],
          [Lack of consistency detected as a proper Python package can not get built without Python bindings.],
          [Please fix the arguments provided to the configure script.])])

   AC_MSG_WARN([python_target_warning])

fi

if test -z "$LEX_INST" -o -z "$YACC_INST"; then

   echo

   m4_define([flex_bison_warning],[m4_joinall([m4_newline([])],
          [Only code from a release archive can be compiled without analyzer and parser generators.],
          [If the sources come from a repository snapshot, please install all the requiered dependencies for the software.])])

   AC_MSG_WARN([flex_bison_warning])

fi

echo
echo configure complete, now type \'make\'
echo
