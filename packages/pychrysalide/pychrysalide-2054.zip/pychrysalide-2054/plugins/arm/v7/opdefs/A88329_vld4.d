
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


@title VLD4 (multiple 4-element structures)

@id 318

@desc {

	This instruction loads multiple 4-element structures from memory into four registers, with de-interleaving. For more information, see Element and structure load/store instructions on page A4-181. Every element of each register is loaded. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 1 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 2009

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2010

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2011

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2012

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2013

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2014

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2015

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2016

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2017

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2018

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2019

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2020

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2021

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2022

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2023

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2024

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2025

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2026

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2027

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2028

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2029

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2030

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2031

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2032

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2033

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2034

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2035

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2036

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2037

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2038

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2039

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2040

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2041

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2042

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2043

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2044

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2045

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2046

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2047

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2048

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2049

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2050

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2051

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2052

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2053

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2054

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2055

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2056

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2057

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2058

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2059

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2060

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2061

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2062

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2063

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2064

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2065

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2066

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2067

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2068

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2069

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2070

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2071

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2072

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2073

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2074

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2075

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2076

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2077

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2078

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2079

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2080

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

		@asm vld4.32 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 1 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 2081

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2082

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2083

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2084

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2085

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2086

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2087

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2088

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2089

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2090

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2091

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2092

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2093

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2094

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2095

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2096

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2097

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2098

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2099

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2100

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2101

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2102

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2103

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2104

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2105

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2106

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2107

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2108

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2109

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2110

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2111

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2112

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2113

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2114

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2115

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2116

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2117

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2118

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2119

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2120

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2121

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2122

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2123

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2124

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2125

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2126

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2127

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2128

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2129

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2130

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2131

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2132

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2133

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2134

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2135

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2136

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

		@asm vld4.8 list maccess

	}

	@syntax {

		@subid 2137

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2138

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2139

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2140

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2141

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2142

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2143

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2144

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

		@asm vld4.16 list maccess

	}

	@syntax {

		@subid 2145

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2146

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2147

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2148

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2149

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2150

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2151

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

		@asm vld4.32 list maccess

	}

	@syntax {

		@subid 2152

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

		@asm vld4.32 list maccess

	}

}

