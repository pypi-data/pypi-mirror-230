
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


@title VST3 (multiple 3-element structures)

@id 370

@desc {

	This instruction stores multiple 3-element structures to memory from three registers, with interleaving. For more information, see Element and structure load/store instructions on page A4-181. Every element of each register is saved. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 0 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 3429

		@assert {

			Rm == 1111
			size == 0
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3430

		@assert {

			Rm == 1111
			size == 0
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3431

		@assert {

			Rm == 1111
			size == 0
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3432

		@assert {

			Rm == 1111
			size == 0
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3433

		@assert {

			Rm == 1111
			size == 1
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3434

		@assert {

			Rm == 1111
			size == 1
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3435

		@assert {

			Rm == 1111
			size == 1
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3436

		@assert {

			Rm == 1111
			size == 1
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3437

		@assert {

			Rm == 1111
			size == 10
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3438

		@assert {

			Rm == 1111
			size == 10
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3439

		@assert {

			Rm == 1111
			size == 10
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3440

		@assert {

			Rm == 1111
			size == 10
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3441

		@assert {

			Rm == 1101
			size == 0
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3442

		@assert {

			Rm == 1101
			size == 0
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3443

		@assert {

			Rm == 1101
			size == 0
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3444

		@assert {

			Rm == 1101
			size == 0
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3445

		@assert {

			Rm == 1101
			size == 1
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3446

		@assert {

			Rm == 1101
			size == 1
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3447

		@assert {

			Rm == 1101
			size == 1
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3448

		@assert {

			Rm == 1101
			size == 1
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3449

		@assert {

			Rm == 1101
			size == 10
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3450

		@assert {

			Rm == 1101
			size == 10
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3451

		@assert {

			Rm == 1101
			size == 10
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3452

		@assert {

			Rm == 1101
			size == 10
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3453

		@assert {

			Rm != 11x1
			size == 0
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3454

		@assert {

			Rm != 11x1
			size == 0
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3455

		@assert {

			Rm != 11x1
			size == 0
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3456

		@assert {

			Rm != 11x1
			size == 0
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3457

		@assert {

			Rm != 11x1
			size == 1
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3458

		@assert {

			Rm != 11x1
			size == 1
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3459

		@assert {

			Rm != 11x1
			size == 1
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3460

		@assert {

			Rm != 11x1
			size == 1
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3461

		@assert {

			Rm != 11x1
			size == 10
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3462

		@assert {

			Rm != 11x1
			size == 10
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3463

		@assert {

			Rm != 11x1
			size == 10
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3464

		@assert {

			Rm != 11x1
			size == 10
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.32 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 0 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 3465

		@assert {

			Rm == 1111
			size == 0
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3466

		@assert {

			Rm == 1111
			size == 0
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3467

		@assert {

			Rm == 1111
			size == 0
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3468

		@assert {

			Rm == 1111
			size == 0
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3469

		@assert {

			Rm == 1111
			size == 1
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3470

		@assert {

			Rm == 1111
			size == 1
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3471

		@assert {

			Rm == 1111
			size == 1
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3472

		@assert {

			Rm == 1111
			size == 1
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3473

		@assert {

			Rm == 1111
			size == 10
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3474

		@assert {

			Rm == 1111
			size == 10
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3475

		@assert {

			Rm == 1111
			size == 10
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3476

		@assert {

			Rm == 1111
			size == 10
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3477

		@assert {

			Rm == 1101
			size == 0
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3478

		@assert {

			Rm == 1101
			size == 0
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3479

		@assert {

			Rm == 1101
			size == 0
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3480

		@assert {

			Rm == 1101
			size == 0
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3481

		@assert {

			Rm == 1101
			size == 1
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3482

		@assert {

			Rm == 1101
			size == 1
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3483

		@assert {

			Rm == 1101
			size == 1
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3484

		@assert {

			Rm == 1101
			size == 1
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3485

		@assert {

			Rm == 1101
			size == 10
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3486

		@assert {

			Rm == 1101
			size == 10
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3487

		@assert {

			Rm == 1101
			size == 10
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3488

		@assert {

			Rm == 1101
			size == 10
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3489

		@assert {

			Rm != 11x1
			size == 0
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3490

		@assert {

			Rm != 11x1
			size == 0
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3491

		@assert {

			Rm != 11x1
			size == 0
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3492

		@assert {

			Rm != 11x1
			size == 0
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.8 list maccess

	}

	@syntax {

		@subid 3493

		@assert {

			Rm != 11x1
			size == 1
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3494

		@assert {

			Rm != 11x1
			size == 1
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3495

		@assert {

			Rm != 11x1
			size == 1
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3496

		@assert {

			Rm != 11x1
			size == 1
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.16 list maccess

	}

	@syntax {

		@subid 3497

		@assert {

			Rm != 11x1
			size == 10
			type == 100
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3498

		@assert {

			Rm != 11x1
			size == 10
			type == 100
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3499

		@assert {

			Rm != 11x1
			size == 10
			type == 101
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.32 list maccess

	}

	@syntax {

		@subid 3500

		@assert {

			Rm != 11x1
			size == 10
			type == 101
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst3.32 list maccess

	}

}

