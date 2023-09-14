
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


@title VLD2 (single 2-element structure to all lanes)

@id 315

@desc {

	This instruction loads one 2-element structure from memory into all lanes of two registers. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 1 D(1) 1 0 Rn(4) Vd(4) 1 1 0 1 size(2) T(1) a(1) Rm(4)

	@syntax {

		@subid 1829

		@assert {

			Rm == 1111
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1830

		@assert {

			Rm == 1111
			size == 0
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1831

		@assert {

			Rm == 1111
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1832

		@assert {

			Rm == 1111
			size == 0
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1833

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1834

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1835

		@assert {

			Rm == 1111
			size == 1
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1836

		@assert {

			Rm == 1111
			size == 1
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1837

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1838

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1839

		@assert {

			Rm == 1111
			size == 10
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1840

		@assert {

			Rm == 1111
			size == 10
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1841

		@assert {

			Rm == 1101
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1842

		@assert {

			Rm == 1101
			size == 0
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1843

		@assert {

			Rm == 1101
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1844

		@assert {

			Rm == 1101
			size == 0
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1845

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1846

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1847

		@assert {

			Rm == 1101
			size == 1
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1848

		@assert {

			Rm == 1101
			size == 1
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1849

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1850

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1851

		@assert {

			Rm == 1101
			size == 10
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1852

		@assert {

			Rm == 1101
			size == 10
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1853

		@assert {

			Rm != 11x1
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1854

		@assert {

			Rm != 11x1
			size == 0
			T == 0
			a == 0

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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1855

		@assert {

			Rm != 11x1
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1856

		@assert {

			Rm != 11x1
			size == 0
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1857

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1858

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 0

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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1859

		@assert {

			Rm != 11x1
			size == 1
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1860

		@assert {

			Rm != 11x1
			size == 1
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1861

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 1

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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1862

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 0

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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1863

		@assert {

			Rm != 11x1
			size == 10
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1864

		@assert {

			Rm != 11x1
			size == 10
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.32 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 1 D(1) 1 0 Rn(4) Vd(4) 1 1 0 1 size(2) T(1) a(1) Rm(4)

	@syntax {

		@subid 1865

		@assert {

			Rm == 1111
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1866

		@assert {

			Rm == 1111
			size == 0
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1867

		@assert {

			Rm == 1111
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1868

		@assert {

			Rm == 1111
			size == 0
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1869

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1870

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1871

		@assert {

			Rm == 1111
			size == 1
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1872

		@assert {

			Rm == 1111
			size == 1
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1873

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1874

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1875

		@assert {

			Rm == 1111
			size == 10
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1876

		@assert {

			Rm == 1111
			size == 10
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1877

		@assert {

			Rm == 1101
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1878

		@assert {

			Rm == 1101
			size == 0
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1879

		@assert {

			Rm == 1101
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1880

		@assert {

			Rm == 1101
			size == 0
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1881

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1882

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1883

		@assert {

			Rm == 1101
			size == 1
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1884

		@assert {

			Rm == 1101
			size == 1
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1885

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1886

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1887

		@assert {

			Rm == 1101
			size == 10
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1888

		@assert {

			Rm == 1101
			size == 10
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1889

		@assert {

			Rm != 11x1
			size == 0
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1890

		@assert {

			Rm != 11x1
			size == 0
			T == 0
			a == 0

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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1891

		@assert {

			Rm != 11x1
			size == 0
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1892

		@assert {

			Rm != 11x1
			size == 0
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1893

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			list = VectorTableDim2(dwvec_D, dwvec_D_1)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1894

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 0

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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1895

		@assert {

			Rm != 11x1
			size == 1
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1896

		@assert {

			Rm != 11x1
			size == 1
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1897

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 1

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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1898

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 0

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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1899

		@assert {

			Rm != 11x1
			size == 10
			T == 1
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1900

		@assert {

			Rm != 11x1
			size == 10
			T == 1
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.32 list maccess

	}

}

