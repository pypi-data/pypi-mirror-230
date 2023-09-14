
noinst_LTLIBRARIES = libcommon.la

libcommon_la_SOURCES =					\
	alloc.h alloc.c						\
	array.h array.c						\
	asm.h asm.c							\
	bconst.h							\
	bits.h bits.c						\
	compression.h compression.c			\
	cpp.h								\
	cpu.h cpu.c							\
	dllist.h dllist.c					\
	endianness.h endianness.c			\
	environment.h environment.c			\
	extstr.h extstr.c					\
	hex.h hex.c							\
	ibuf.h ibuf.c						\
	io.h io.c							\
	itoa.h itoa.c						\
	fnv1a.h fnv1a.c						\
	leb128.h leb128.c					\
	macros.h							\
	net.h net.c							\
	packed.h packed.c					\
	pathname.h pathname.c				\
	pearson.h pearson.c					\
	shuffle.h shuffle.c					\
	sort.h sort.c						\
	sqlite.h sqlite.c					\
	szstr.h								\
	utf8.h utf8.c						\
	xdg.h xdg.c							\
	xml.h xml.c

if BUILD_CURL_SUPPORT

libcommon_la_SOURCES +=					\
	curl.h curl.c

endif

cpu.lo: CFLAGS += -mavx512f

libcommon_la_CFLAGS = $(TOOLKIT_CFLAGS) $(LIBXML_CFLAGS)

if BUILD_CURL_SUPPORT

libcommon_la_CFLAGS += $(LIBCURL_CFLAGS)

endif


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libcommon_la_SOURCES:%c=)
