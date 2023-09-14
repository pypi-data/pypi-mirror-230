
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


@title VLD1 (single element to all lanes)

@id 313

@desc {

	This instruction loads one element from memory into every element of one or two vectors. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 1 D(1) 1 0 Rn(4) Vd(4) 1 1 0 0 size(2) T(1) a(1) Rm(4)

	@syntax {

		@subid 1589

		@assert {

			Rm == 1111
			size == 0
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1590

		@assert {

			Rm == 1111
			size == 0
			T == 1
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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1591

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1592

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1593

		@assert {

			Rm == 1111
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1594

		@assert {

			Rm == 1111
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1595

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1596

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1597

		@assert {

			Rm == 1111
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1598

		@assert {

			Rm == 1111
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1599

		@assert {

			Rm == 1101
			size == 0
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1600

		@assert {

			Rm == 1101
			size == 0
			T == 1
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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1601

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1602

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1603

		@assert {

			Rm == 1101
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1604

		@assert {

			Rm == 1101
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1605

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1606

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1607

		@assert {

			Rm == 1101
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1608

		@assert {

			Rm == 1101
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1609

		@assert {

			Rm != 11x1
			size == 0
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1610

		@assert {

			Rm != 11x1
			size == 0
			T == 1
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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1611

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1612

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1613

		@assert {

			Rm != 11x1
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1614

		@assert {

			Rm != 11x1
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1615

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1616

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1617

		@assert {

			Rm != 11x1
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1618

		@assert {

			Rm != 11x1
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 1 D(1) 1 0 Rn(4) Vd(4) 1 1 0 0 size(2) T(1) a(1) Rm(4)

	@syntax {

		@subid 1619

		@assert {

			Rm == 1111
			size == 0
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1620

		@assert {

			Rm == 1111
			size == 0
			T == 1
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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1621

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1622

		@assert {

			Rm == 1111
			size == 1
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1623

		@assert {

			Rm == 1111
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1624

		@assert {

			Rm == 1111
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1625

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1626

		@assert {

			Rm == 1111
			size == 10
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1627

		@assert {

			Rm == 1111
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1628

		@assert {

			Rm == 1111
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1629

		@assert {

			Rm == 1101
			size == 0
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1630

		@assert {

			Rm == 1101
			size == 0
			T == 1
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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1631

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1632

		@assert {

			Rm == 1101
			size == 1
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1633

		@assert {

			Rm == 1101
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1634

		@assert {

			Rm == 1101
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1635

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1636

		@assert {

			Rm == 1101
			size == 10
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1637

		@assert {

			Rm == 1101
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1638

		@assert {

			Rm == 1101
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1639

		@assert {

			Rm != 11x1
			size == 0
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1640

		@assert {

			Rm != 11x1
			size == 0
			T == 1
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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1641

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 16)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1642

		@assert {

			Rm != 11x1
			size == 1
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1643

		@assert {

			Rm != 11x1
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1644

		@assert {

			Rm != 11x1
			size == 1
			T == 1
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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1645

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 32)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1646

		@assert {

			Rm != 11x1
			size == 10
			T == 0
			a == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			list = VectorTableDim1(dwvec_D)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 0)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1647

		@assert {

			Rm != 11x1
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1648

		@assert {

			Rm != 11x1
			size == 10
			T == 1
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

		@asm vld1.32 list maccess

	}

}

