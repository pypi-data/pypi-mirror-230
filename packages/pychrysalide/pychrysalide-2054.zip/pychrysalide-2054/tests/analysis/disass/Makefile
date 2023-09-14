
EXECUTABLES=hello endofname irreducible selfloop evalcommand h1b h2

all: $(EXECUTABLES)

hello: hello.c
	$(ARM_CROSS)gcc $< -o $@

endofname: endofname.c
	$(ARM_CROSS)gcc $< -o $@

irreducible: irreducible.c
	$(ARM_CROSS)gcc $< -o $@

selfloop: selfloop.c
	$(ARM_CROSS)gcc $< -o $@

evalcommand: evalcommand.c
	$(ARM_CROSS)gcc $< -o $@

h1b: h1b.c
	$(ARM_CROSS)gcc $< -o $@

h2: h2.c
	$(ARM_CROSS)gcc $< -o $@

clean:
	rm -f $(EXECUTABLES)
