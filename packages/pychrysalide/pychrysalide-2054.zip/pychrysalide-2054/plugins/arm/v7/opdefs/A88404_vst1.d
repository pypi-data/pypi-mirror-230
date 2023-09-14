
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


@title VST1 (multiple single elements)

@id 368

@desc {

	Vector Store (multiple single elements) stores elements to memory from one, two, three, or four registers, without interleaving. Every element of each register is stored. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 0 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 3033

		@assert {

			Rm == 1111
			size == 0
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3034

		@assert {

			Rm == 1111
			size == 0
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3035

		@assert {

			Rm == 1111
			size == 0
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3036

		@assert {

			Rm == 1111
			size == 0
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3037

		@assert {

			Rm == 1111
			size == 0
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3038

		@assert {

			Rm == 1111
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3039

		@assert {

			Rm == 1111
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3040

		@assert {

			Rm == 1111
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3041

		@assert {

			Rm == 1111
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3042

		@assert {

			Rm == 1111
			size == 1
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3043

		@assert {

			Rm == 1111
			size == 1
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3044

		@assert {

			Rm == 1111
			size == 1
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3045

		@assert {

			Rm == 1111
			size == 1
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3046

		@assert {

			Rm == 1111
			size == 1
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3047

		@assert {

			Rm == 1111
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3048

		@assert {

			Rm == 1111
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3049

		@assert {

			Rm == 1111
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3050

		@assert {

			Rm == 1111
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3051

		@assert {

			Rm == 1111
			size == 10
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3052

		@assert {

			Rm == 1111
			size == 10
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3053

		@assert {

			Rm == 1111
			size == 10
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3054

		@assert {

			Rm == 1111
			size == 10
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3055

		@assert {

			Rm == 1111
			size == 10
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3056

		@assert {

			Rm == 1111
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3057

		@assert {

			Rm == 1111
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3058

		@assert {

			Rm == 1111
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3059

		@assert {

			Rm == 1111
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3060

		@assert {

			Rm == 1111
			size == 11
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3061

		@assert {

			Rm == 1111
			size == 11
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3062

		@assert {

			Rm == 1111
			size == 11
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3063

		@assert {

			Rm == 1111
			size == 11
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3064

		@assert {

			Rm == 1111
			size == 11
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3065

		@assert {

			Rm == 1111
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3066

		@assert {

			Rm == 1111
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3067

		@assert {

			Rm == 1111
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3068

		@assert {

			Rm == 1111
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3069

		@assert {

			Rm == 1101
			size == 0
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3070

		@assert {

			Rm == 1101
			size == 0
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3071

		@assert {

			Rm == 1101
			size == 0
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3072

		@assert {

			Rm == 1101
			size == 0
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3073

		@assert {

			Rm == 1101
			size == 0
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3074

		@assert {

			Rm == 1101
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3075

		@assert {

			Rm == 1101
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3076

		@assert {

			Rm == 1101
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3077

		@assert {

			Rm == 1101
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3078

		@assert {

			Rm == 1101
			size == 1
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3079

		@assert {

			Rm == 1101
			size == 1
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3080

		@assert {

			Rm == 1101
			size == 1
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3081

		@assert {

			Rm == 1101
			size == 1
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3082

		@assert {

			Rm == 1101
			size == 1
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3083

		@assert {

			Rm == 1101
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3084

		@assert {

			Rm == 1101
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3085

		@assert {

			Rm == 1101
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3086

		@assert {

			Rm == 1101
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3087

		@assert {

			Rm == 1101
			size == 10
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3088

		@assert {

			Rm == 1101
			size == 10
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3089

		@assert {

			Rm == 1101
			size == 10
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3090

		@assert {

			Rm == 1101
			size == 10
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3091

		@assert {

			Rm == 1101
			size == 10
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3092

		@assert {

			Rm == 1101
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3093

		@assert {

			Rm == 1101
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3094

		@assert {

			Rm == 1101
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3095

		@assert {

			Rm == 1101
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3096

		@assert {

			Rm == 1101
			size == 11
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3097

		@assert {

			Rm == 1101
			size == 11
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3098

		@assert {

			Rm == 1101
			size == 11
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3099

		@assert {

			Rm == 1101
			size == 11
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3100

		@assert {

			Rm == 1101
			size == 11
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3101

		@assert {

			Rm == 1101
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3102

		@assert {

			Rm == 1101
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3103

		@assert {

			Rm == 1101
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3104

		@assert {

			Rm == 1101
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3105

		@assert {

			Rm != 11x1
			size == 0
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3106

		@assert {

			Rm != 11x1
			size == 0
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3107

		@assert {

			Rm != 11x1
			size == 0
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3108

		@assert {

			Rm != 11x1
			size == 0
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3109

		@assert {

			Rm != 11x1
			size == 0
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3110

		@assert {

			Rm != 11x1
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3111

		@assert {

			Rm != 11x1
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3112

		@assert {

			Rm != 11x1
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3113

		@assert {

			Rm != 11x1
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3114

		@assert {

			Rm != 11x1
			size == 1
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3115

		@assert {

			Rm != 11x1
			size == 1
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3116

		@assert {

			Rm != 11x1
			size == 1
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3117

		@assert {

			Rm != 11x1
			size == 1
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3118

		@assert {

			Rm != 11x1
			size == 1
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3119

		@assert {

			Rm != 11x1
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3120

		@assert {

			Rm != 11x1
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3121

		@assert {

			Rm != 11x1
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3122

		@assert {

			Rm != 11x1
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3123

		@assert {

			Rm != 11x1
			size == 10
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3124

		@assert {

			Rm != 11x1
			size == 10
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3125

		@assert {

			Rm != 11x1
			size == 10
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3126

		@assert {

			Rm != 11x1
			size == 10
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3127

		@assert {

			Rm != 11x1
			size == 10
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3128

		@assert {

			Rm != 11x1
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3129

		@assert {

			Rm != 11x1
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3130

		@assert {

			Rm != 11x1
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3131

		@assert {

			Rm != 11x1
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3132

		@assert {

			Rm != 11x1
			size == 11
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3133

		@assert {

			Rm != 11x1
			size == 11
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3134

		@assert {

			Rm != 11x1
			size == 11
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3135

		@assert {

			Rm != 11x1
			size == 11
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3136

		@assert {

			Rm != 11x1
			size == 11
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3137

		@assert {

			Rm != 11x1
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3138

		@assert {

			Rm != 11x1
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3139

		@assert {

			Rm != 11x1
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3140

		@assert {

			Rm != 11x1
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 0 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 3141

		@assert {

			Rm == 1111
			size == 0
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3142

		@assert {

			Rm == 1111
			size == 0
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3143

		@assert {

			Rm == 1111
			size == 0
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3144

		@assert {

			Rm == 1111
			size == 0
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3145

		@assert {

			Rm == 1111
			size == 0
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3146

		@assert {

			Rm == 1111
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3147

		@assert {

			Rm == 1111
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3148

		@assert {

			Rm == 1111
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3149

		@assert {

			Rm == 1111
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3150

		@assert {

			Rm == 1111
			size == 1
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3151

		@assert {

			Rm == 1111
			size == 1
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3152

		@assert {

			Rm == 1111
			size == 1
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3153

		@assert {

			Rm == 1111
			size == 1
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3154

		@assert {

			Rm == 1111
			size == 1
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3155

		@assert {

			Rm == 1111
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3156

		@assert {

			Rm == 1111
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3157

		@assert {

			Rm == 1111
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3158

		@assert {

			Rm == 1111
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3159

		@assert {

			Rm == 1111
			size == 10
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3160

		@assert {

			Rm == 1111
			size == 10
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3161

		@assert {

			Rm == 1111
			size == 10
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3162

		@assert {

			Rm == 1111
			size == 10
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3163

		@assert {

			Rm == 1111
			size == 10
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3164

		@assert {

			Rm == 1111
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3165

		@assert {

			Rm == 1111
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3166

		@assert {

			Rm == 1111
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3167

		@assert {

			Rm == 1111
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3168

		@assert {

			Rm == 1111
			size == 11
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3169

		@assert {

			Rm == 1111
			size == 11
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3170

		@assert {

			Rm == 1111
			size == 11
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3171

		@assert {

			Rm == 1111
			size == 11
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3172

		@assert {

			Rm == 1111
			size == 11
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3173

		@assert {

			Rm == 1111
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3174

		@assert {

			Rm == 1111
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3175

		@assert {

			Rm == 1111
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3176

		@assert {

			Rm == 1111
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3177

		@assert {

			Rm == 1101
			size == 0
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3178

		@assert {

			Rm == 1101
			size == 0
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3179

		@assert {

			Rm == 1101
			size == 0
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3180

		@assert {

			Rm == 1101
			size == 0
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3181

		@assert {

			Rm == 1101
			size == 0
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3182

		@assert {

			Rm == 1101
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3183

		@assert {

			Rm == 1101
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3184

		@assert {

			Rm == 1101
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3185

		@assert {

			Rm == 1101
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3186

		@assert {

			Rm == 1101
			size == 1
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3187

		@assert {

			Rm == 1101
			size == 1
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3188

		@assert {

			Rm == 1101
			size == 1
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3189

		@assert {

			Rm == 1101
			size == 1
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3190

		@assert {

			Rm == 1101
			size == 1
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3191

		@assert {

			Rm == 1101
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3192

		@assert {

			Rm == 1101
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3193

		@assert {

			Rm == 1101
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3194

		@assert {

			Rm == 1101
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3195

		@assert {

			Rm == 1101
			size == 10
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3196

		@assert {

			Rm == 1101
			size == 10
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3197

		@assert {

			Rm == 1101
			size == 10
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3198

		@assert {

			Rm == 1101
			size == 10
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3199

		@assert {

			Rm == 1101
			size == 10
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3200

		@assert {

			Rm == 1101
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3201

		@assert {

			Rm == 1101
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3202

		@assert {

			Rm == 1101
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3203

		@assert {

			Rm == 1101
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3204

		@assert {

			Rm == 1101
			size == 11
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3205

		@assert {

			Rm == 1101
			size == 11
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3206

		@assert {

			Rm == 1101
			size == 11
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3207

		@assert {

			Rm == 1101
			size == 11
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3208

		@assert {

			Rm == 1101
			size == 11
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3209

		@assert {

			Rm == 1101
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3210

		@assert {

			Rm == 1101
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3211

		@assert {

			Rm == 1101
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3212

		@assert {

			Rm == 1101
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3213

		@assert {

			Rm != 11x1
			size == 0
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3214

		@assert {

			Rm != 11x1
			size == 0
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3215

		@assert {

			Rm != 11x1
			size == 0
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3216

		@assert {

			Rm != 11x1
			size == 0
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3217

		@assert {

			Rm != 11x1
			size == 0
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3218

		@assert {

			Rm != 11x1
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3219

		@assert {

			Rm != 11x1
			size == 0
			type == 110
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3220

		@assert {

			Rm != 11x1
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3221

		@assert {

			Rm != 11x1
			size == 0
			type == 10
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

		@asm vst1.8 list maccess

	}

	@syntax {

		@subid 3222

		@assert {

			Rm != 11x1
			size == 1
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3223

		@assert {

			Rm != 11x1
			size == 1
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3224

		@assert {

			Rm != 11x1
			size == 1
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3225

		@assert {

			Rm != 11x1
			size == 1
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3226

		@assert {

			Rm != 11x1
			size == 1
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3227

		@assert {

			Rm != 11x1
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3228

		@assert {

			Rm != 11x1
			size == 1
			type == 110
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3229

		@assert {

			Rm != 11x1
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3230

		@assert {

			Rm != 11x1
			size == 1
			type == 10
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

		@asm vst1.16 list maccess

	}

	@syntax {

		@subid 3231

		@assert {

			Rm != 11x1
			size == 10
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3232

		@assert {

			Rm != 11x1
			size == 10
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3233

		@assert {

			Rm != 11x1
			size == 10
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3234

		@assert {

			Rm != 11x1
			size == 10
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3235

		@assert {

			Rm != 11x1
			size == 10
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3236

		@assert {

			Rm != 11x1
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3237

		@assert {

			Rm != 11x1
			size == 10
			type == 110
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3238

		@assert {

			Rm != 11x1
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3239

		@assert {

			Rm != 11x1
			size == 10
			type == 10
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

		@asm vst1.32 list maccess

	}

	@syntax {

		@subid 3240

		@assert {

			Rm != 11x1
			size == 11
			type == 111
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3241

		@assert {

			Rm != 11x1
			size == 11
			type == 111
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3242

		@assert {

			Rm != 11x1
			size == 11
			type == 1010
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3243

		@assert {

			Rm != 11x1
			size == 11
			type == 1010
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3244

		@assert {

			Rm != 11x1
			size == 11
			type == 1010
			align == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3245

		@assert {

			Rm != 11x1
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3246

		@assert {

			Rm != 11x1
			size == 11
			type == 110
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3247

		@assert {

			Rm != 11x1
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

	@syntax {

		@subid 3248

		@assert {

			Rm != 11x1
			size == 11
			type == 10
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

		@asm vst1.64 list maccess

	}

}

