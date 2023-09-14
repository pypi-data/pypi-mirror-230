
/* Chrysalide - Outil d'analyse de fichiers binaires
 * ##FILE## - traduction d'instructions ARMv7
 *
 * Copyright (C) 2017 Cyrille Bagard
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


@title VST4 (multiple 4-element structures)

@id 371

@desc {

	This instruction stores multiple 4-element structures to memory from four registers, with interleaving. For more information, see Element and structure load/store instructions on page A4-181. Every element of each register is saved. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 0 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 3501

		@assert {

			Rm == 1111
			size == 0
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3502

		@assert {

			Rm == 1111
			size == 0
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3503

		@assert {

			Rm == 1111
			size == 0
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3504

		@assert {

			Rm == 1111
			size == 0
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3505

		@assert {

			Rm == 1111
			size == 0
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3506

		@assert {

			Rm == 1111
			size == 0
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3507

		@assert {

			Rm == 1111
			size == 0
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3508

		@assert {

			Rm == 1111
			size == 0
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3509

		@assert {

			Rm == 1111
			size == 1
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3510

		@assert {

			Rm == 1111
			size == 1
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3511

		@assert {

			Rm == 1111
			size == 1
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3512

		@assert {

			Rm == 1111
			size == 1
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3513

		@assert {

			Rm == 1111
			size == 1
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3514

		@assert {

			Rm == 1111
			size == 1
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3515

		@assert {

			Rm == 1111
			size == 1
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3516

		@assert {

			Rm == 1111
			size == 1
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3517

		@assert {

			Rm == 1111
			size == 10
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3518

		@assert {

			Rm == 1111
			size == 10
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3519

		@assert {

			Rm == 1111
			size == 10
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3520

		@assert {

			Rm == 1111
			size == 10
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3521

		@assert {

			Rm == 1111
			size == 10
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3522

		@assert {

			Rm == 1111
			size == 10
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3523

		@assert {

			Rm == 1111
			size == 10
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3524

		@assert {

			Rm == 1111
			size == 10
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3525

		@assert {

			Rm == 1101
			size == 0
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3526

		@assert {

			Rm == 1101
			size == 0
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3527

		@assert {

			Rm == 1101
			size == 0
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3528

		@assert {

			Rm == 1101
			size == 0
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3529

		@assert {

			Rm == 1101
			size == 0
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3530

		@assert {

			Rm == 1101
			size == 0
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3531

		@assert {

			Rm == 1101
			size == 0
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3532

		@assert {

			Rm == 1101
			size == 0
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3533

		@assert {

			Rm == 1101
			size == 1
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3534

		@assert {

			Rm == 1101
			size == 1
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3535

		@assert {

			Rm == 1101
			size == 1
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3536

		@assert {

			Rm == 1101
			size == 1
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3537

		@assert {

			Rm == 1101
			size == 1
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3538

		@assert {

			Rm == 1101
			size == 1
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3539

		@assert {

			Rm == 1101
			size == 1
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3540

		@assert {

			Rm == 1101
			size == 1
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3541

		@assert {

			Rm == 1101
			size == 10
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3542

		@assert {

			Rm == 1101
			size == 10
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3543

		@assert {

			Rm == 1101
			size == 10
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3544

		@assert {

			Rm == 1101
			size == 10
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3545

		@assert {

			Rm == 1101
			size == 10
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3546

		@assert {

			Rm == 1101
			size == 10
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3547

		@assert {

			Rm == 1101
			size == 10
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3548

		@assert {

			Rm == 1101
			size == 10
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3549

		@assert {

			Rm != 11x1
			size == 0
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3550

		@assert {

			Rm != 11x1
			size == 0
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3551

		@assert {

			Rm != 11x1
			size == 0
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3552

		@assert {

			Rm != 11x1
			size == 0
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3553

		@assert {

			Rm != 11x1
			size == 0
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3554

		@assert {

			Rm != 11x1
			size == 0
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3555

		@assert {

			Rm != 11x1
			size == 0
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3556

		@assert {

			Rm != 11x1
			size == 0
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3557

		@assert {

			Rm != 11x1
			size == 1
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3558

		@assert {

			Rm != 11x1
			size == 1
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3559

		@assert {

			Rm != 11x1
			size == 1
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3560

		@assert {

			Rm != 11x1
			size == 1
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3561

		@assert {

			Rm != 11x1
			size == 1
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3562

		@assert {

			Rm != 11x1
			size == 1
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3563

		@assert {

			Rm != 11x1
			size == 1
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3564

		@assert {

			Rm != 11x1
			size == 1
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3565

		@assert {

			Rm != 11x1
			size == 10
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3566

		@assert {

			Rm != 11x1
			size == 10
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3567

		@assert {

			Rm != 11x1
			size == 10
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3568

		@assert {

			Rm != 11x1
			size == 10
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3569

		@assert {

			Rm != 11x1
			size == 10
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3570

		@assert {

			Rm != 11x1
			size == 10
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3571

		@assert {

			Rm != 11x1
			size == 10
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3572

		@assert {

			Rm != 11x1
			size == 10
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 0 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 3573

		@assert {

			Rm == 1111
			size == 0
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3574

		@assert {

			Rm == 1111
			size == 0
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3575

		@assert {

			Rm == 1111
			size == 0
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3576

		@assert {

			Rm == 1111
			size == 0
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3577

		@assert {

			Rm == 1111
			size == 0
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3578

		@assert {

			Rm == 1111
			size == 0
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3579

		@assert {

			Rm == 1111
			size == 0
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3580

		@assert {

			Rm == 1111
			size == 0
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3581

		@assert {

			Rm == 1111
			size == 1
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3582

		@assert {

			Rm == 1111
			size == 1
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3583

		@assert {

			Rm == 1111
			size == 1
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3584

		@assert {

			Rm == 1111
			size == 1
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3585

		@assert {

			Rm == 1111
			size == 1
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3586

		@assert {

			Rm == 1111
			size == 1
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3587

		@assert {

			Rm == 1111
			size == 1
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3588

		@assert {

			Rm == 1111
			size == 1
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3589

		@assert {

			Rm == 1111
			size == 10
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3590

		@assert {

			Rm == 1111
			size == 10
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3591

		@assert {

			Rm == 1111
			size == 10
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3592

		@assert {

			Rm == 1111
			size == 10
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3593

		@assert {

			Rm == 1111
			size == 10
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3594

		@assert {

			Rm == 1111
			size == 10
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3595

		@assert {

			Rm == 1111
			size == 10
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3596

		@assert {

			Rm == 1111
			size == 10
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3597

		@assert {

			Rm == 1101
			size == 0
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3598

		@assert {

			Rm == 1101
			size == 0
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3599

		@assert {

			Rm == 1101
			size == 0
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3600

		@assert {

			Rm == 1101
			size == 0
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3601

		@assert {

			Rm == 1101
			size == 0
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3602

		@assert {

			Rm == 1101
			size == 0
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3603

		@assert {

			Rm == 1101
			size == 0
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3604

		@assert {

			Rm == 1101
			size == 0
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3605

		@assert {

			Rm == 1101
			size == 1
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3606

		@assert {

			Rm == 1101
			size == 1
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3607

		@assert {

			Rm == 1101
			size == 1
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3608

		@assert {

			Rm == 1101
			size == 1
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3609

		@assert {

			Rm == 1101
			size == 1
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3610

		@assert {

			Rm == 1101
			size == 1
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3611

		@assert {

			Rm == 1101
			size == 1
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3612

		@assert {

			Rm == 1101
			size == 1
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3613

		@assert {

			Rm == 1101
			size == 10
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3614

		@assert {

			Rm == 1101
			size == 10
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3615

		@assert {

			Rm == 1101
			size == 10
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3616

		@assert {

			Rm == 1101
			size == 10
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3617

		@assert {

			Rm == 1101
			size == 10
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3618

		@assert {

			Rm == 1101
			size == 10
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3619

		@assert {

			Rm == 1101
			size == 10
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3620

		@assert {

			Rm == 1101
			size == 10
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3621

		@assert {

			Rm != 11x1
			size == 0
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3622

		@assert {

			Rm != 11x1
			size == 0
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3623

		@assert {

			Rm != 11x1
			size == 0
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3624

		@assert {

			Rm != 11x1
			size == 0
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3625

		@assert {

			Rm != 11x1
			size == 0
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3626

		@assert {

			Rm != 11x1
			size == 0
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3627

		@assert {

			Rm != 11x1
			size == 0
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3628

		@assert {

			Rm != 11x1
			size == 0
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.8 list maccess

	}

	@syntax {

		@subid 3629

		@assert {

			Rm != 11x1
			size == 1
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3630

		@assert {

			Rm != 11x1
			size == 1
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3631

		@assert {

			Rm != 11x1
			size == 1
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3632

		@assert {

			Rm != 11x1
			size == 1
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3633

		@assert {

			Rm != 11x1
			size == 1
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3634

		@assert {

			Rm != 11x1
			size == 1
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3635

		@assert {

			Rm != 11x1
			size == 1
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3636

		@assert {

			Rm != 11x1
			size == 1
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.16 list maccess

	}

	@syntax {

		@subid 3637

		@assert {

			Rm != 11x1
			size == 10
			type == 0
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3638

		@assert {

			Rm != 11x1
			size == 10
			type == 0
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3639

		@assert {

			Rm != 11x1
			size == 10
			type == 0
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3640

		@assert {

			Rm != 11x1
			size == 10
			type == 0
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3641

		@assert {

			Rm != 11x1
			size == 10
			type == 1
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3642

		@assert {

			Rm != 11x1
			size == 10
			type == 1
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3643

		@assert {

			Rm != 11x1
			size == 10
			type == 1
			align == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 256)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

	@syntax {

		@subid 3644

		@assert {

			Rm != 11x1
			size == 10
			type == 1
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst4.32 list maccess

	}

}

