
EXECUTABLES=oob_section_name overlapping_areas strings

all: $(EXECUTABLES)

oob_section_name: oob_section_name.o
	$(ARM_CROSS)objcopy $< -O binary $@

overlapping_areas: overlapping_areas.o
	$(ARM_CROSS)objcopy $< -O binary $@

strings: strings.asm
	grep .global strings.asm | cut -d ' ' -f 2 > keep.lst
	$(ARM_CROSS)as -o strings.o strings.asm
	$(ARM_CROSS)ld -s --retain-symbols-file=keep.lst -o strings strings.o
	rm -f keep.lst


%.o: %.asm
	$(ARM_CROSS)as -c $< -o $@

clean:
	rm -f *.o $(EXECUTABLES)
