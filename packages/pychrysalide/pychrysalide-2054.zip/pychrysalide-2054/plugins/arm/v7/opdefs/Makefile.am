
include $(top_srcdir)/tools/d2c/d2c.mk


D2C_BIN = $(top_srcdir)/tools/d2c/d2c
GEN_BIN = $(top_srcdir)/tools/d2c/d2c_genmakefile.sh


D2C_OUTDIR = $(abs_srcdir)/../

D2C_TYPE = raw

D2C_ARCH = ARMv7
D2C_ARCH_CN = ARMv7
D2C_GUARD = PLUGINS_ARM_V7_OPCODES

D2C_ENCODINGS =							\
	-e A=arm							\
	-e t=thumb_16						\
	-e T=thumb_32

D2C_ID_PREFIX = AOP7
D2C_ID_COUNT = 500

D2C_SPECIFIC = --filename-reuse=2


FIXED_C_INCLUDES =						\
	\#include <assert.h>				\
	\n									\
	\n\#include <common/bconst.h>		\
	\n									\
	\n\#include "identifiers.h"			\
	\n\#include "../helpers.h"			\
	\n\#include "../instruction.h"		\
	\n\#include "../../instruction.h"

FIXED_H_INCLUDES =						\
	\#include <stdint.h>				\
    \n									\
    \n\#include <arch/instruction.h>

FIXED_H_HOOKS_INCLUDES =				\
	\#include <arch/link.h>				\
	\n									\
	\n\#include "../fetch.h"			\
	\n\#include "../link.h"				\
	\n\#include "../post.h"				\
	\n\#include "../../link.h"


# for i in $(seq 1 426); do file=A88${i}_*d ; test -f $file && ls $file ; done | sed 's/^/\t/' | sed 's/$/\t\t\t\t\t\t\\/'
# for i in $(seq 1 22); do file=B93${i}_*d ; test -f $file && ls $file ; done | sed 's/^/\t/' | sed 's/$/\t\t\t\t\t\t\\/'

ARMV7_DEFS = 							\
	A881_adc.d							\
	A882_adc.d							\
	A883_adc.d							\
	A884_add.d							\
	A885_add.d							\
	A886_add.d							\
	A887_add.d							\
	A888_add.d							\
	A889_add.d							\
	A8810_add.d							\
	A8811_add.d							\
	A8812_adr.d							\
	A8813_and.d							\
	A8814_and.d							\
	A8815_and.d							\
	A8816_asr.d							\
	A8817_asr.d							\
	A8818_b.d							\
	A8819_bfc.d							\
	A8820_bfi.d							\
	A8821_bic.d							\
	A8822_bic.d							\
	A8823_bic.d							\
	A8824_bkpt.d						\
	A8825_bl.d							\
	A8826_blx.d							\
	A8827_bx.d							\
	A8828_bxj.d							\
	A8829_cb.d							\
	A8830_cdp.d							\
	A8832_clrex.d						\
	A8833_clz.d							\
	A8834_cmn.d							\
	A8835_cmn.d							\
	A8836_cmn.d							\
	A8837_cmp.d							\
	A8838_cmp.d							\
	A8839_cmp.d							\
	A8842_dbg.d							\
	A8843_dmb.d							\
	A8844_dsb.d							\
	A8846_eor.d							\
	A8847_eor.d							\
	A8848_eor.d							\
	A8853_isb.d							\
	A8854_it.d							\
	A8855_ldc.d							\
	A8856_ldc.d							\
	A8857_ldm.d							\
	A8858_ldm.d							\
	A8859_ldmda.d						\
	A8860_ldmdb.d						\
	A8861_ldmib.d						\
	A8862_ldr.d							\
	A8863_ldr.d							\
	A8864_ldr.d							\
	A8865_ldr.d							\
	A8866_ldr.d							\
	A8867_ldrb.d						\
	A8868_ldrb.d						\
	A8869_ldrb.d						\
	A8870_ldrb.d						\
	A8871_ldrbt.d						\
	A8872_ldrd.d						\
	A8873_ldrd.d						\
	A8874_ldrd.d						\
	A8875_ldrex.d						\
	A8876_ldrexb.d						\
	A8877_ldrexd.d						\
	A8878_ldrexh.d						\
	A8879_ldrh.d						\
	A8880_ldrh.d						\
	A8881_ldrh.d						\
	A8882_ldrh.d						\
	A8883_ldrht.d						\
	A8884_ldrsb.d						\
	A8885_ldrsb.d						\
	A8886_ldrsb.d						\
	A8887_ldrsbt.d						\
	A8888_ldrsh.d						\
	A8889_ldrsh.d						\
	A8890_ldrsh.d						\
	A8891_ldrsht.d						\
	A8892_ldrt.d						\
	A8894_lsl.d							\
	A8895_lsl.d							\
	A8896_lsr.d							\
	A8897_lsr.d							\
	A8898_mcr.d							\
	A8899_mcrr.d						\
	A88100_mla.d						\
	A88101_mls.d						\
	A88102_mov.d						\
	A88103_mov.d						\
	A88104_mov.d						\
	A88106_movt.d						\
	A88107_mrc.d						\
	A88108_mrrc.d						\
	A88109_mrs.d						\
	A88111_msr.d						\
	A88112_msr.d						\
	A88114_mul.d						\
	A88115_mvn.d						\
	A88116_mvn.d						\
	A88117_mvn.d						\
	A88119_nop.d						\
	A88120_orn.d						\
	A88121_orn.d						\
	A88122_orr.d						\
	A88123_orr.d						\
	A88124_orr.d						\
	A88125_pkh.d						\
	A88126_pld.d						\
	A88127_pld.d						\
	A88128_pld.d						\
	A88129_pli.d						\
	A88130_pli.d						\
	A88131_pop.d						\
	A88132_pop.d						\
	A88133_push.d						\
	A88134_qadd.d						\
	A88135_qadd16.d						\
	A88136_qadd8.d						\
	A88137_qasx.d						\
	A88138_qdadd.d						\
	A88139_qdsub.d						\
	A88140_qsax.d						\
	A88141_qsub.d						\
	A88142_qsub16.d						\
	A88143_qsub8.d						\
	A88144_rbit.d						\
	A88145_rev.d						\
	A88146_rev16.d						\
	A88147_revsh.d						\
	A88149_ror.d						\
	A88150_ror.d						\
	A88151_rrx.d						\
	A88152_rsb.d						\
	A88153_rsb.d						\
	A88154_rsb.d						\
	A88155_rsc.d						\
	A88156_rsc.d						\
	A88157_rsc.d						\
	A88158_sadd16.d						\
	A88159_sadd8.d						\
	A88160_sasx.d						\
	A88161_sbc.d						\
	A88162_sbc.d						\
	A88163_sbc.d						\
	A88164_sbfx.d						\
	A88165_sdiv.d						\
	A88166_sel.d						\
	A88167_setend.d						\
	A88168_sev.d						\
	A88169_shadd16.d					\
	A88170_shadd8.d						\
	A88171_shasx.d						\
	A88172_shsax.d						\
	A88173_shsub16.d					\
	A88174_shsub8.d						\
	A88176_smla.d						\
	A88177_smlad.d						\
	A88178_smlal.d						\
	A88179_smlal.d						\
	A88180_smlald.d						\
	A88181_smlaw.d						\
	A88182_smlsd.d						\
	A88183_smlsld.d						\
	A88184_smmla.d						\
	A88185_smmls.d						\
	A88186_smmul.d						\
	A88187_smuad.d						\
	A88188_smul.d						\
	A88189_smull.d						\
	A88190_smulw.d						\
	A88191_smusd.d						\
	A88193_ssat.d						\
	A88194_ssat16.d						\
	A88195_ssax.d						\
	A88196_ssub16.d						\
	A88197_ssub8.d						\
	A88198_stc.d						\
	A88199_stm.d						\
	A88200_stmda.d						\
	A88201_stmdb.d						\
	A88202_stmib.d						\
	A88203_str.d						\
	A88204_str.d						\
	A88205_str.d						\
	A88206_strb.d						\
	A88207_strb.d						\
	A88208_strb.d						\
	A88209_strbt.d						\
	A88210_strd.d						\
	A88211_strd.d						\
	A88212_strex.d						\
	A88213_strexb.d						\
	A88214_strexd.d						\
	A88215_strexh.d						\
	A88216_strh.d						\
	A88217_strh.d						\
	A88218_strh.d						\
	A88219_strht.d						\
	A88220_strt.d						\
	A88221_sub.d						\
	A88222_sub.d						\
	A88223_sub.d						\
	A88224_sub.d						\
	A88225_sub.d						\
	A88226_sub.d						\
	A88228_svc.d						\
	A88229_swp.d						\
	A88230_sxtab.d						\
	A88231_sxtab16.d					\
	A88232_sxtah.d						\
	A88233_sxtb.d						\
	A88234_sxtb16.d						\
	A88235_sxth.d						\
	A88236_tb.d							\
	A88237_teq.d						\
	A88238_teq.d						\
	A88239_teq.d						\
	A88240_tst.d						\
	A88241_tst.d						\
	A88242_tst.d						\
	A88243_uadd16.d						\
	A88244_uadd8.d						\
	A88245_uasx.d						\
	A88246_ubfx.d						\
	A88247_udf.d						\
	A88248_udiv.d						\
	A88249_uhadd16.d					\
	A88250_uhadd8.d						\
	A88251_uhasx.d						\
	A88252_uhsax.d						\
	A88253_uhsub16.d					\
	A88254_uhsub8.d						\
	A88255_umaal.d						\
	A88256_umlal.d						\
	A88257_umull.d						\
	A88258_uqadd16.d					\
	A88259_uqadd8.d						\
	A88260_uqasx.d						\
	A88261_uqsax.d						\
	A88262_uqsub16.d					\
	A88263_uqsub8.d						\
	A88264_usad8.d						\
	A88265_usada8.d						\
	A88266_usat.d						\
	A88267_usat16.d						\
	A88268_usax.d						\
	A88269_usub16.d						\
	A88270_usub8.d						\
	A88271_uxtab.d						\
	A88272_uxtab16.d					\
	A88273_uxtah.d						\
	A88274_uxtb.d						\
	A88275_uxtb16.d						\
	A88276_uxth.d						\
	A88277_vaba.d						\
	A88278_vabd.d						\
	A88279_vabd.d						\
	A88280_vabs.d						\
	A88281_vac.d						\
	A88282_vadd.d						\
	A88283_vadd.d						\
	A88284_vaddhn.d						\
	A88285_vadd.d						\
	A88287_vand.d						\
	A88288_vbic.d						\
	A88289_vbic.d						\
	A88290_vb.d							\
	A88291_vceq.d						\
	A88292_vceq.d						\
	A88293_vcge.d						\
	A88294_vcge.d						\
	A88295_vcgt.d						\
	A88296_vcgt.d						\
	A88298_vcle.d						\
	A88299_vcls.d						\
	A88301_vclt.d						\
	A88302_vclz.d						\
	A88303_vcmp.d						\
	A88304_vcnt.d						\
	A88305_vcvt.d						\
	A88306_vcvt.d						\
	A88309_vcvt.d						\
	A88310_vcvt.d						\
	A88311_vcvt.d						\
	A88312_vdiv.d						\
	A88314_vdup.d						\
	A88315_veor.d						\
	A88316_vext.d						\
	A88317_vfm.d						\
	A88318_vfnm.d						\
	A88319_vh.d							\
	A88320_vld1.d						\
	A88322_vld1.d						\
	A88323_vld2.d						\
	A88325_vld2.d						\
	A88326_vld3.d						\
	A88328_vld3.d						\
	A88329_vld4.d						\
	A88331_vld4.d						\
	A88332_vldm.d						\
	A88334_vmax.d						\
	A88335_vmax.d						\
	A88336_vmla.d						\
	A88337_vmla.d						\
	A88343_vmov.d						\
	A88344_vmov.d						\
	A88345_vmov.d						\
	A88346_vmovl.d						\
	A88347_vmovn.d						\
	A88348_vmrs.d						\
	A88349_vmsr.d						\
	A88350_vmul.d						\
	A88351_vmul.d						\
	A88353_vmvn.d						\
	A88354_vmvn.d						\
	A88355_vneg.d						\
	A88356_vnm.d						\
	A88358_vorn.d						\
	A88359_vorr.d						\
	A88360_vorr.d						\
	A88361_vpadal.d						\
	A88362_vpadd.d						\
	A88363_vpadd.d						\
	A88364_vpaddl.d						\
	A88365_vpmax.d						\
	A88366_vpmax.d						\
	A88367_vpop.d						\
	A88368_vpush.d						\
	A88369_vqabs.d						\
	A88370_vqadd.d						\
	A88374_vqmov.d						\
	A88375_vqneg.d						\
	A88377_vqrshl.d						\
	A88379_vqshl.d						\
	A88382_vqsub.d						\
	A88383_vraddhn.d					\
	A88384_vrecpe.d						\
	A88385_vrecps.d						\
	A88386_vrev.d						\
	A88387_vrhadd.d						\
	A88388_vrshl.d						\
	A88391_vrsqrte.d					\
	A88392_vrsqrts.d					\
	A88394_vrsubhn.d					\
	A88396_vshl.d						\
	A88401_vsqrt.d						\
	A88404_vst1.d						\
	A88406_vst2.d						\
	A88408_vst3.d						\
	A88410_vst4.d						\
	A88412_vstm.d						\
	A88413_vstr.d						\
	A88414_vsub.d						\
	A88415_vsub.d						\
	A88416_vsubhn.d						\
	A88417_vsub.d						\
	A88418_vswp.d						\
	A88419_vtb.d						\
	A88420_vtrn.d						\
	A88421_vtst.d						\
	A88422_vuzp.d						\
	A88423_vzip.d						\
	A88424_wfe.d						\
	A88425_wfi.d						\
	A88426_yield.d						\
	A931_enterx.d						\
	B931_cps.d							\
	B932_cps.d							\
	B933_eret.d							\
	B934_hvc.d							\
	B935_ldm.d							\
	B936_ldm.d							\
	B938_mrs.d							\
	B939_mrs.d							\
	B9310_msr.d							\
	B9311_msr.d							\
	B9312_msr.d							\
	B9313_rfe.d							\
	B9314_smc.d							\
	B9315_srs.d							\
	B9316_srs.d							\
	B9317_stm.d							\
	B9319_subs.d						\
	B9320_subs.d						\
	B9321_vmrs.d						\
	B9322_vmsr.d


# make dist procède répertoire par répertoire. Or le répertoire opcodes utilise
# le contenu du répertoire opdefs. Il faut donc générer les fichiers nécessaires
# au répertoire opcodes. Et comme on ne peut pas compléter la règle dist, on
# ajoute à la distribution les cibles marquant la génération. (1/2)

EXTRA_DIST = $(ARMV7_DEFS) $(ARMV7_DEFS:.d=.g)

# Après coup, on supprime les fichiers inutiles de la distribution/ (2/2)

dist-hook:
	cd $(distdir) && rm $(ARMV7_DEFS:.d=.g)

all: $(ARMV7_DEFS:.d=.g) fmk.done d2c_final_rules

fmk.done: $(ARMV7_DEFS)
	$(GEN_BIN) $(D2C_OUTDIR)opcodes/ arm thumb_32 thumb_16
	touch $@

clean:
	rm -rf $(ARMV7_DEFS:.d=.g) .gen fmk.done
