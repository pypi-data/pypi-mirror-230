
.NOTPARALLEL:

d2c_verbose = $(d2c_verbose_@AM_V@)
d2c_verbose_ = $(d2c_verbose_@AM_DEFAULT_V@)
d2c_verbose_0 = @echo "  D2C     " $<;

fini_verbose = $(fini_verbose_@AM_V@)
fini_verbose_ = $(fini_verbose_@AM_DEFAULT_V@)
fini_verbose_0 = echo "  FINI    " `basename $$f`;

fix_verbose = $(fix_verbose_@AM_V@)
fix_verbose_ = $(fix_verbose_@AM_DEFAULT_V@)
fix_verbose_0 = echo "  FIX     " `basename $$f`;


# D2C_BIN =
# GEN_BIN =

# D2C_OUTDIR =
# D2C_TYPE =
# D2C_ARCH =
# D2C_ARCH_CN =
# D2C_GUARD =
# D2C_ENCODINGS =
# D2C_ID_PREFIX =
# D2C_ID_COUNT =
# D2C_SPECIFIC =

# FIXED_C_INCLUDES =
# FIXED_H_INCLUDES =
# FIXED_H_HOOKS_INCLUDES =


SUFFIXES = .g

.d.g:
	$(d2c_verbose)$(D2C_BIN) -x cc -o $(D2C_OUTDIR) -t $(D2C_TYPE) -a $(D2C_ARCH) -n $(D2C_ARCH_CN)				\
		-G $(D2C_GUARD) $(D2C_ENCODINGS) --id-prefix=$(D2C_ID_PREFIX) --id-expected=$(D2C_ID_COUNT)				\
		$(D2C_SPECIFIC) $<
	@touch $@

d2c_final_rules: finish_headers fix_includes_in_c_templates fix_includes_in_h_templates untabify_disass

finish_headers:
	@for f in `find $(D2C_OUTDIR) -type f -name '*.h'`; do														\
		grep -q '#endif' $$f && continue;																		\
		$(fini_verbose)$(D2C_BIN) -x fini -o $(D2C_OUTDIR) -t $(D2C_TYPE) -a $(D2C_ARCH) -n $(D2C_ARCH_CN)		\
			-G $(D2C_GUARD) $(D2C_ENCODINGS) --id-prefix=$(D2C_ID_PREFIX) --id-expected=$(D2C_ID_COUNT)			\
			$(D2C_SPECIFIC) $$f																					\
			|| ( echo "Can not complete $$f" ; exit 1 ) ;														\
	done

fix_includes_in_c_templates:
	@for f in `find $(D2C_OUTDIR) -type f -name '*.c'`; do									\
		if grep -q '##INCLUDES##' $$f; then													\
			$(fix_verbose)sed -i 's@##INCLUDES##@$(FIXED_C_INCLUDES)@' $$f;					\
		fi;																					\
	done

fix_includes_in_h_templates:
	@for f in `find $(D2C_OUTDIR) -type f -name '*.h'`; do									\
		if grep -q '##INCLUDES##' $$f; then													\
			if [ `basename $$f` == "hooks.h" ]; then										\
				$(fix_verbose)sed -i 's@##INCLUDES##@$(FIXED_H_HOOKS_INCLUDES)@' $$f ;		\
			else																			\
				$(fix_verbose)sed -i 's@##INCLUDES##@$(FIXED_H_INCLUDES)@' $$f ;			\
			fi;																				\
		fi;																					\
	done

# Merci http://www.commandlinefu.com/commands/view/10276/grep-tab-t
untabify_disass:
	@find $(D2C_OUTDIR) -type f -name '*.[ch]' -exec grep -q $$'\t' {} \; -exec sed -i 's/\t/    /g' {} \;
