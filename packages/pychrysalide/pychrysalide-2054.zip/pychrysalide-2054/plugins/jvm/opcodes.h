
/* Chrysalide - Outil d'analyse de fichiers binaires
 * opcodes.h - prototypes pour la liste de tous les opcodes de l'architecture JVM
 *
 * Copyright (C) 2018 Cyrille Bagard
 *
 *  This file is part of Chrysalide.
 *
 *  Chrysalide is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  Chrysalide is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#ifndef _ARCH_JVM_OPCODES_H
#define _ARCH_JVM_OPCODES_H


#include "processor.h"



/* Décode une instruction de type 'aconst_null'. */
GArchInstruction *jvm_read_instr_aconst_null(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'aload_n'. */
GArchInstruction *jvm_read_instr_aload_n(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'areturn'. */
GArchInstruction *jvm_read_instr_areturn(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'd2f'. */
GArchInstruction *jvm_read_instr_d2f(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'd2i'. */
GArchInstruction *jvm_read_instr_d2i(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'd2l'. */
GArchInstruction *jvm_read_instr_d2l(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'dreturn'. */
GArchInstruction *jvm_read_instr_dreturn(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'dup'. */
GArchInstruction *jvm_read_instr_dup(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'dup_x1'. */
GArchInstruction *jvm_read_instr_dup_x1(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'dup_x2'. */
GArchInstruction *jvm_read_instr_dup_x2(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'dup2'. */
GArchInstruction *jvm_read_instr_dup2(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'dup2_x1'. */
GArchInstruction *jvm_read_instr_dup2_x1(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'dup2_x2'. */
GArchInstruction *jvm_read_instr_dup2_x2(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'f2d'. */
GArchInstruction *jvm_read_instr_f2d(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'f2i'. */
GArchInstruction *jvm_read_instr_f2i(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'f2l'. */
GArchInstruction *jvm_read_instr_f2l(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'freturn'. */
GArchInstruction *jvm_read_instr_freturn(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'getstatic'. */
GArchInstruction *jvm_read_instr_getstatic(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'i2b'. */
GArchInstruction *jvm_read_instr_i2b(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'i2c'. */
GArchInstruction *jvm_read_instr_i2c(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'i2d'. */
GArchInstruction *jvm_read_instr_i2d(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'i2f'. */
GArchInstruction *jvm_read_instr_i2f(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'i2l'. */
GArchInstruction *jvm_read_instr_i2l(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'i2s'. */
GArchInstruction *jvm_read_instr_i2s(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'iadd'. */
GArchInstruction *jvm_read_instr_iadd(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'iconst_n'. */
GArchInstruction *jvm_read_instr_iconst_n(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'iload_n'. */
GArchInstruction *jvm_read_instr_iload_n(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'invokespecial'. */
GArchInstruction *jvm_read_instr_invokespecial(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'invokestatic'. */
GArchInstruction *jvm_read_instr_invokestatic(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'invokevirtual'. */
GArchInstruction *jvm_read_instr_invokevirtual(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'istore_n'. */
GArchInstruction *jvm_read_instr_istore_n(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'ireturn'. */
GArchInstruction *jvm_read_instr_ireturn(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'lreturn'. */
GArchInstruction *jvm_read_instr_lreturn(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'l2d'. */
GArchInstruction *jvm_read_instr_l2d(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'l2i'. */
GArchInstruction *jvm_read_instr_l2i(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'l2f'. */
GArchInstruction *jvm_read_instr_l2f(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'monitorenter'. */
GArchInstruction *jvm_read_instr_monitorenter(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'monitorexit'. */
GArchInstruction *jvm_read_instr_monitorexit(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'nop'. */
GArchInstruction *jvm_read_instr_nop(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'pop'. */
GArchInstruction *jvm_read_instr_pop(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'pop2'. */
GArchInstruction *jvm_read_instr_pop2(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);

/* Décode une instruction de type 'return'. */
GArchInstruction *jvm_read_instr_return(const bin_t *, off_t *, off_t, vmpa_t, const GJvmProcessor *);



#endif  /* _ARCH_JVM_OPCODES_H */
