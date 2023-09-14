
EXECUTABLES=hm

all: $(EXECUTABLES)

hm: hm.c
	$(ARM_CROSS)gcc $< -o $@

clean:
	rm -f $(EXECUTABLES)
