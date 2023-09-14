
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


@title VLD3 (multiple 3-element structures)

@id 316

@desc {

	This instruction loads multiple 3-element structures from memory into three registers, with de-interleaving. For more information, see Element and structure load/store instructions on page A4-181. Every element of each register is loaded. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 1 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 1901

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1902

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1903

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1904

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1905

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1906

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1907

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1908

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1909

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1910

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1911

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1912

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1913

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1914

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1915

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1916

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1917

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1918

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1919

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1920

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1921

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1922

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1923

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1924

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1925

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1926

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1927

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1928

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1929

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1930

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1931

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1932

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1933

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1934

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1935

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1936

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

		@asm vld3.32 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 1 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 1937

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1938

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1939

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1940

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1941

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1942

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1943

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1944

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1945

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1946

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1947

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1948

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1949

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1950

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1951

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1952

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1953

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1954

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1955

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1956

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1957

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1958

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1959

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1960

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1961

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1962

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1963

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1964

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

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1965

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1966

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1967

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1968

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

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1969

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1970

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1971

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

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1972

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

		@asm vld3.32 list maccess

	}

}

