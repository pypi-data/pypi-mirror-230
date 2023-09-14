
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


@title VLD4 (single 4-element structure to all lanes)

@id 319

@desc {

	This instruction loads one 4-element structure from memory into all lanes of four registers. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 1 D(1) 1 0 Rn(4) Vd(4) 1 1 1 1 size(2) T(1) a(1) Rm(4)

	@syntax {

		@subid 2153

		@assert {

			Rm == 1111
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2154

		@assert {

			Rm == 1111
			size == 0
			T == 0
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2155

		@assert {

			Rm == 1111
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2156

		@assert {

			Rm == 1111
			size == 0
			T == 1
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2157

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2158

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2159

		@assert {

			Rm == 1111
			size == 1
			T == 1
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2160

		@assert {

			Rm == 1111
			size == 1
			T == 1
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2161

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2162

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2163

		@assert {

			Rm == 1111
			size == 10
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2164

		@assert {

			Rm == 1111
			size == 10
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2165

		@assert {

			Rm == 1111
			size == 11
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2166

		@assert {

			Rm == 1111
			size == 11
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2167

		@assert {

			Rm == 1111
			size == 11
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2168

		@assert {

			Rm == 1111
			size == 11
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2169

		@assert {

			Rm == 1101
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2170

		@assert {

			Rm == 1101
			size == 0
			T == 0
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2171

		@assert {

			Rm == 1101
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2172

		@assert {

			Rm == 1101
			size == 0
			T == 1
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2173

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2174

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2175

		@assert {

			Rm == 1101
			size == 1
			T == 1
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2176

		@assert {

			Rm == 1101
			size == 1
			T == 1
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2177

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2178

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2179

		@assert {

			Rm == 1101
			size == 10
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2180

		@assert {

			Rm == 1101
			size == 10
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2181

		@assert {

			Rm == 1101
			size == 11
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2182

		@assert {

			Rm == 1101
			size == 11
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2183

		@assert {

			Rm == 1101
			size == 11
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2184

		@assert {

			Rm == 1101
			size == 11
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2185

		@assert {

			Rm != 11x1
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2186

		@assert {

			Rm != 11x1
			size == 0
			T == 0
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2187

		@assert {

			Rm != 11x1
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2188

		@assert {

			Rm != 11x1
			size == 0
			T == 1
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2189

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2190

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2191

		@assert {

			Rm != 11x1
			size == 1
			T == 1
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2192

		@assert {

			Rm != 11x1
			size == 1
			T == 1
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2193

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2194

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2195

		@assert {

			Rm != 11x1
			size == 10
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2196

		@assert {

			Rm != 11x1
			size == 10
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2197

		@assert {

			Rm != 11x1
			size == 11
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2198

		@assert {

			Rm != 11x1
			size == 11
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2199

		@assert {

			Rm != 11x1
			size == 11
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2200

		@assert {

			Rm != 11x1
			size == 11
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 1 D(1) 1 0 Rn(4) Vd(4) 1 1 1 1 size(2) T(1) a(1) Rm(4)

	@syntax {

		@subid 2201

		@assert {

			Rm == 1111
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2202

		@assert {

			Rm == 1111
			size == 0
			T == 0
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2203

		@assert {

			Rm == 1111
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2204

		@assert {

			Rm == 1111
			size == 0
			T == 1
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2205

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2206

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2207

		@assert {

			Rm == 1111
			size == 1
			T == 1
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2208

		@assert {

			Rm == 1111
			size == 1
			T == 1
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2209

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2210

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2211

		@assert {

			Rm == 1111
			size == 10
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2212

		@assert {

			Rm == 1111
			size == 10
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2213

		@assert {

			Rm == 1111
			size == 11
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2214

		@assert {

			Rm == 1111
			size == 11
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2215

		@assert {

			Rm == 1111
			size == 11
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2216

		@assert {

			Rm == 1111
			size == 11
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2217

		@assert {

			Rm == 1101
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2218

		@assert {

			Rm == 1101
			size == 0
			T == 0
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2219

		@assert {

			Rm == 1101
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2220

		@assert {

			Rm == 1101
			size == 0
			T == 1
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2221

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2222

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2223

		@assert {

			Rm == 1101
			size == 1
			T == 1
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2224

		@assert {

			Rm == 1101
			size == 1
			T == 1
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2225

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2226

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2227

		@assert {

			Rm == 1101
			size == 10
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2228

		@assert {

			Rm == 1101
			size == 10
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2229

		@assert {

			Rm == 1101
			size == 11
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2230

		@assert {

			Rm == 1101
			size == 11
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2231

		@assert {

			Rm == 1101
			size == 11
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2232

		@assert {

			Rm == 1101
			size == 11
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2233

		@assert {

			Rm != 11x1
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_3 = NextDoubleWordVector(dwvec_D, 3)
			list = VectorTableDim4(dwvec_D, dwvec_D_1, dwvec_D_2, dwvec_D_3)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2234

		@assert {

			Rm != 11x1
			size == 0
			T == 0
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2235

		@assert {

			Rm != 11x1
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			dwvec_D_6 = NextDoubleWordVector(dwvec_D, 6)
			list = VectorTableDim4(dwvec_D, dwvec_D_2, dwvec_D_4, dwvec_D_6)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2236

		@assert {

			Rm != 11x1
			size == 0
			T == 1
			a == 0

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2237

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2238

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2239

		@assert {

			Rm != 11x1
			size == 1
			T == 1
			a == 1

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2240

		@assert {

			Rm != 11x1
			size == 1
			T == 1
			a == 0

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2241

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2242

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2243

		@assert {

			Rm != 11x1
			size == 10
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2244

		@assert {

			Rm != 11x1
			size == 10
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2245

		@assert {

			Rm != 11x1
			size == 11
			T == 0
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2246

		@assert {

			Rm != 11x1
			size == 11
			T == 0
			a == 0

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2247

		@assert {

			Rm != 11x1
			size == 11
			T == 1
			a == 1

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2248

		@assert {

			Rm != 11x1
			size == 11
			T == 1
			a == 0

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

		@asm vld4.32 list maccess

	}

}

