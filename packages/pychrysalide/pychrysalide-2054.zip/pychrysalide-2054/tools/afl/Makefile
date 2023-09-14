
all: itanium

itanium: itanium.c
	afl-gcc -o $@ \
		`pkg-config --libs --cflags gtk+-3.0 glib-2.0 libxml-2.0` \
		 -I../.. -I../../src \
		-Wl,-rpath,$(PWD)/../../src/.libs -L../../src/.libs -lchrysacore \
		-Wl,-rpath,$(PWD)/../../plugins/itanium/.libs -L../../plugins/itanium/.libs -litanium \
		$^

clean:
	rm -f itanium *~
