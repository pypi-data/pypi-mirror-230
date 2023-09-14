
include $(top_srcdir)/tools/d2c/d2c.mk


D2C_BIN = $(top_srcdir)/tools/d2c/d2c
GEN_BIN = $(top_srcdir)/tools/d2c/d2c_genmakefile.sh


D2C_OUTDIR = $(abs_srcdir)/../

D2C_TYPE = format

D2C_ARCH = "Dalvik v35"
D2C_ARCH_CN = Dalvik35
D2C_GUARD = PLUGINS_DALVIK_V35_OPCODES

D2C_ENCODINGS =							\
	-e none

D2C_ID_PREFIX = DOP35
D2C_ID_COUNT = 255

D2C_SPECIFIC = --op-prefix=DALVIK_OPT_


FIXED_C_INCLUDES = 						\
	\#include <stdint.h>				\
	\n									\
	\n\#include "identifiers.h"			\
	\n\#include "../instruction.h"		\
	\n\#include "../operand.h"			\
	\n\#include "../../helpers.h"

FIXED_H_INCLUDES = 						\
	\#include <stdint.h>				\
	\n									\
	\n\#include <analysis/content.h>	\
	\n\#include <arch/context.h>		\
	\n\#include <format/executable.h>	\
	\n									\
	\n\#include "../processor.h"

FIXED_H_HOOKS_INCLUDES = 				\
	\#include "../../fetch.h"			\
	\n\#include "../../link.h"			\
	\n\#include "../../post.h"


# for (( i = 0; i < 256; i++)); do def=$(ls `printf "*_%02x.d" $i` 2> /dev/null); test -z "$def" || echo -e "\t$def\t\t\t\t\t\t\t\\" ; done
DALVIK_DEFS = 							\
	nop_00.d							\
	move_01.d							\
	move_02.d							\
	move_03.d							\
	move_04.d							\
	move_05.d							\
	move_06.d							\
	move_07.d							\
	move_08.d							\
	move_09.d							\
	move_0a.d							\
	move_0b.d							\
	move_0c.d							\
	move_0d.d							\
	return_0e.d							\
	return_0f.d							\
	return_10.d							\
	return_11.d							\
	const_12.d							\
	const_13.d							\
	const_14.d							\
	const_15.d							\
	const_16.d							\
	const_17.d							\
	const_18.d							\
	const_19.d							\
	const_1a.d							\
	const_1b.d							\
	const_1c.d							\
	monitor_1d.d						\
	monitor_1e.d						\
	check_1f.d							\
	instanceof_20.d						\
	array_21.d							\
	new_22.d							\
	new_23.d							\
	array_24.d							\
	filled_25.d							\
	array_26.d							\
	throw_27.d							\
	goto_28.d							\
	goto_29.d							\
	goto_2a.d							\
	switch_2b.d							\
	switch_2c.d							\
	cmpl_2d.d							\
	cmpg_2e.d							\
	cmpl_2f.d							\
	cmpg_30.d							\
	cmp_31.d							\
	if_32.d								\
	if_33.d								\
	if_34.d								\
	if_35.d								\
	if_36.d								\
	if_37.d								\
	if_38.d								\
	if_39.d								\
	if_3a.d								\
	if_3b.d								\
	if_3c.d								\
	if_3d.d								\
	unused_3e.d							\
	unused_3f.d							\
	unused_40.d							\
	unused_41.d							\
	unused_42.d							\
	unused_43.d							\
	aget_44.d							\
	aget_45.d							\
	aget_46.d							\
	aget_47.d							\
	aget_48.d							\
	aget_49.d							\
	aget_4a.d							\
	aput_4b.d							\
	aput_4c.d							\
	aput_4d.d							\
	aput_4e.d							\
	aput_4f.d							\
	aput_50.d							\
	aput_51.d							\
	iget_52.d							\
	iget_53.d							\
	iget_54.d							\
	iget_55.d							\
	iget_56.d							\
	iget_57.d							\
	iget_58.d							\
	iput_59.d							\
	iput_5a.d							\
	iput_5b.d							\
	iput_5c.d							\
	iput_5d.d							\
	iput_5e.d							\
	iput_5f.d							\
	sget_60.d							\
	sget_61.d							\
	sget_62.d							\
	sget_63.d							\
	sget_64.d							\
	sget_65.d							\
	sget_66.d							\
	sput_67.d							\
	sput_68.d							\
	sput_69.d							\
	sput_6a.d							\
	sput_6b.d							\
	sput_6c.d							\
	sput_6d.d							\
	invoke_6e.d							\
	invoke_6f.d							\
	invoke_70.d							\
	invoke_71.d							\
	invoke_72.d							\
	unused_73.d							\
	invoke_74.d							\
	invoke_75.d							\
	invoke_76.d							\
	invoke_77.d							\
	invoke_78.d							\
	unused_79.d							\
	unused_7a.d							\
	neg_7b.d							\
	not_7c.d							\
	neg_7d.d							\
	not_7e.d							\
	neg_7f.d							\
	neg_80.d							\
	to_81.d								\
	to_82.d								\
	to_83.d								\
	to_84.d								\
	to_85.d								\
	to_86.d								\
	to_87.d								\
	to_88.d								\
	to_89.d								\
	to_8a.d								\
	to_8b.d								\
	to_8c.d								\
	to_8d.d								\
	to_8e.d								\
	to_8f.d								\
	add_90.d							\
	sub_91.d							\
	mul_92.d							\
	div_93.d							\
	rem_94.d							\
	and_95.d							\
	or_96.d								\
	xor_97.d							\
	shl_98.d							\
	shr_99.d							\
	ushr_9a.d							\
	add_9b.d							\
	sub_9c.d							\
	mul_9d.d							\
	div_9e.d							\
	rem_9f.d							\
	and_a0.d							\
	or_a1.d								\
	xor_a2.d							\
	shl_a3.d							\
	shr_a4.d							\
	ushr_a5.d							\
	add_a6.d							\
	sub_a7.d							\
	mul_a8.d							\
	div_a9.d							\
	rem_aa.d							\
	add_ab.d							\
	sub_ac.d							\
	mul_ad.d							\
	div_ae.d							\
	rem_af.d							\
	add_b0.d							\
	sub_b1.d							\
	mul_b2.d							\
	div_b3.d							\
	rem_b4.d							\
	and_b5.d							\
	or_b6.d								\
	xor_b7.d							\
	shl_b8.d							\
	shr_b9.d							\
	ushr_ba.d							\
	add_bb.d							\
	sub_bc.d							\
	mul_bd.d							\
	div_be.d							\
	rem_bf.d							\
	and_c0.d							\
	or_c1.d								\
	xor_c2.d							\
	shl_c3.d							\
	shr_c4.d							\
	ushr_c5.d							\
	add_c6.d							\
	sub_c7.d							\
	mul_c8.d							\
	div_c9.d							\
	rem_ca.d							\
	add_cb.d							\
	sub_cc.d							\
	mul_cd.d							\
	div_ce.d							\
	rem_cf.d							\
	add_d0.d							\
	rsub_d1.d							\
	mul_d2.d							\
	div_d3.d							\
	rem_d4.d							\
	and_d5.d							\
	or_d6.d								\
	xor_d7.d							\
	add_d8.d							\
	rsub_d9.d							\
	mul_da.d							\
	div_db.d							\
	rem_dc.d							\
	and_dd.d							\
	or_de.d								\
	xor_df.d							\
	shl_e0.d							\
	shr_e1.d							\
	ushr_e2.d							\
	unused_e3.d							\
	unused_e4.d							\
	unused_e5.d							\
	unused_e6.d							\
	unused_e7.d							\
	unused_e8.d							\
	unused_e9.d							\
	unused_ea.d							\
	unused_eb.d							\
	unused_ec.d							\
	unused_ed.d							\
	unused_ee.d							\
	unused_ef.d							\
	unused_f0.d							\
	unused_f1.d							\
	unused_f2.d							\
	unused_f3.d							\
	unused_f4.d							\
	unused_f5.d							\
	unused_f6.d							\
	unused_f7.d							\
	unused_f8.d							\
	unused_f9.d							\
	unused_fa.d							\
	unused_fb.d							\
	unused_fc.d							\
	unused_fd.d							\
	unused_fe.d							\
	unused_ff.d


# make dist procède répertoire par répertoire. Or le répertoire opcodes utilise
# le contenu du répertoire opdefs. Il faut donc générer les fichiers nécessaires
# au répertoire opcodes. Et comme on ne peut pas compléter la règle dist, on
# ajoute à la distribution les cibles marquant la génération. (1/2)

EXTRA_DIST = $(DALVIK_DEFS) $(DALVIK_DEFS:.d=.g)

# Après coup, on supprime les fichiers inutiles de la distribution/ (2/2)

dist-hook:
	cd $(distdir) && rm $(DALVIK_DEFS:.d=.g)

all: $(DALVIK_DEFS:.d=.g) fmk.done d2c_final_rules

fmk.done: $(DALVIK_DEFS)
	$(GEN_BIN) $(D2C_OUTDIR)opcodes/ -
	touch $@

clean:
	rm -rf $(DALVIK_DEFS:.d=.g) .gen fmk.done
