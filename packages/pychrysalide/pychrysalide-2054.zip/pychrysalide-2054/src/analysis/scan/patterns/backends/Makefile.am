
noinst_LTLIBRARIES  = libanalysisscanpatternsbackends.la


libanalysisscanpatternsbackends_la_SOURCES =	\
	acism-int.h								\
	acism.h acism.c							\
	bitap-int.h								\
	bitap.h bitap.c

# Cf. https://www.gnu.org/software/automake/manual/html_node/Per_002dObject-Flags.html

AM_CFLAGS = $(LIBGOBJ_CFLAGS)



#AM_CFLAGS:=$(filter-out -O2,$(AM_CFLAGS))


#bitap.lo: AM_CFLAGS += -Ofast -march=native -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1 #-mavx512bw
#bitap.lo: AM_CFLAGS += -O3 -march=native -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1 #-mavx512bw
bitap.lo: AM_CFLAGS += -g -march=native -mno-vzeroupper -falign-functions=1 -falign-jumps=1 -falign-loops=1 -falign-labels=1


devdir = $(includedir)/chrysalide/$(subdir:src/%=core/%)

dev_HEADERS = $(libanalysisscanpatternsbackends_la_SOURCES:%c=)
