
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


@title VLD2 (multiple 2-element structures)

@id 314

@desc {

	This instruction loads multiple 2-element structures from memory into two or four registers, with de-interleaving. For more information, see Element and structure load/store instructions on page A4-181. Every element of each register is loaded. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 1 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 1649

		@assert {

			Rm == 1111
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1650

		@assert {

			Rm == 1111
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1651

		@assert {

			Rm == 1111
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1652

		@assert {

			Rm == 1111
			size == 0
			type == 1001
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1653

		@assert {

			Rm == 1111
			size == 0
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1654

		@assert {

			Rm == 1111
			size == 0
			type == 1001
			align == 0

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

		@subid 1655

		@assert {

			Rm == 1111
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1656

		@assert {

			Rm == 1111
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1657

		@assert {

			Rm == 1111
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1658

		@assert {

			Rm == 1111
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1659

		@assert {

			Rm == 1111
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1660

		@assert {

			Rm == 1111
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1661

		@assert {

			Rm == 1111
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1662

		@assert {

			Rm == 1111
			size == 1
			type == 1001
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1663

		@assert {

			Rm == 1111
			size == 1
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1664

		@assert {

			Rm == 1111
			size == 1
			type == 1001
			align == 0

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

		@subid 1665

		@assert {

			Rm == 1111
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1666

		@assert {

			Rm == 1111
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1667

		@assert {

			Rm == 1111
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1668

		@assert {

			Rm == 1111
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1669

		@assert {

			Rm == 1111
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1670

		@assert {

			Rm == 1111
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1671

		@assert {

			Rm == 1111
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1672

		@assert {

			Rm == 1111
			size == 10
			type == 1001
			align == 1

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

		@subid 1673

		@assert {

			Rm == 1111
			size == 10
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1674

		@assert {

			Rm == 1111
			size == 10
			type == 1001
			align == 0

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

		@subid 1675

		@assert {

			Rm == 1111
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1676

		@assert {

			Rm == 1111
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1677

		@assert {

			Rm == 1111
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1678

		@assert {

			Rm == 1111
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1679

		@assert {

			Rm == 1101
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1680

		@assert {

			Rm == 1101
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1681

		@assert {

			Rm == 1101
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1682

		@assert {

			Rm == 1101
			size == 0
			type == 1001
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1683

		@assert {

			Rm == 1101
			size == 0
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1684

		@assert {

			Rm == 1101
			size == 0
			type == 1001
			align == 0

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

		@subid 1685

		@assert {

			Rm == 1101
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1686

		@assert {

			Rm == 1101
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1687

		@assert {

			Rm == 1101
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1688

		@assert {

			Rm == 1101
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1689

		@assert {

			Rm == 1101
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1690

		@assert {

			Rm == 1101
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1691

		@assert {

			Rm == 1101
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1692

		@assert {

			Rm == 1101
			size == 1
			type == 1001
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1693

		@assert {

			Rm == 1101
			size == 1
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1694

		@assert {

			Rm == 1101
			size == 1
			type == 1001
			align == 0

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

		@subid 1695

		@assert {

			Rm == 1101
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1696

		@assert {

			Rm == 1101
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1697

		@assert {

			Rm == 1101
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1698

		@assert {

			Rm == 1101
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1699

		@assert {

			Rm == 1101
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1700

		@assert {

			Rm == 1101
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1701

		@assert {

			Rm == 1101
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1702

		@assert {

			Rm == 1101
			size == 10
			type == 1001
			align == 1

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

		@subid 1703

		@assert {

			Rm == 1101
			size == 10
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1704

		@assert {

			Rm == 1101
			size == 10
			type == 1001
			align == 0

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

		@subid 1705

		@assert {

			Rm == 1101
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1706

		@assert {

			Rm == 1101
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1707

		@assert {

			Rm == 1101
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1708

		@assert {

			Rm == 1101
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1709

		@assert {

			Rm != 11x1
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1710

		@assert {

			Rm != 11x1
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1711

		@assert {

			Rm != 11x1
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1712

		@assert {

			Rm != 11x1
			size == 0
			type == 1001
			align == 1

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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1713

		@assert {

			Rm != 11x1
			size == 0
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1714

		@assert {

			Rm != 11x1
			size == 0
			type == 1001
			align == 0

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

		@subid 1715

		@assert {

			Rm != 11x1
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1716

		@assert {

			Rm != 11x1
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1717

		@assert {

			Rm != 11x1
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1718

		@assert {

			Rm != 11x1
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1719

		@assert {

			Rm != 11x1
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1720

		@assert {

			Rm != 11x1
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1721

		@assert {

			Rm != 11x1
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1722

		@assert {

			Rm != 11x1
			size == 1
			type == 1001
			align == 1

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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1723

		@assert {

			Rm != 11x1
			size == 1
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1724

		@assert {

			Rm != 11x1
			size == 1
			type == 1001
			align == 0

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

		@subid 1725

		@assert {

			Rm != 11x1
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1726

		@assert {

			Rm != 11x1
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1727

		@assert {

			Rm != 11x1
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1728

		@assert {

			Rm != 11x1
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1729

		@assert {

			Rm != 11x1
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1730

		@assert {

			Rm != 11x1
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1731

		@assert {

			Rm != 11x1
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1732

		@assert {

			Rm != 11x1
			size == 10
			type == 1001
			align == 1

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

		@subid 1733

		@assert {

			Rm != 11x1
			size == 10
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1734

		@assert {

			Rm != 11x1
			size == 10
			type == 1001
			align == 0

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

	@syntax {

		@subid 1735

		@assert {

			Rm != 11x1
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1736

		@assert {

			Rm != 11x1
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1737

		@assert {

			Rm != 11x1
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1738

		@assert {

			Rm != 11x1
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 1 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 1739

		@assert {

			Rm == 1111
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1740

		@assert {

			Rm == 1111
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1741

		@assert {

			Rm == 1111
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1742

		@assert {

			Rm == 1111
			size == 0
			type == 1001
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1743

		@assert {

			Rm == 1111
			size == 0
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1744

		@assert {

			Rm == 1111
			size == 0
			type == 1001
			align == 0

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

		@subid 1745

		@assert {

			Rm == 1111
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1746

		@assert {

			Rm == 1111
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1747

		@assert {

			Rm == 1111
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1748

		@assert {

			Rm == 1111
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1749

		@assert {

			Rm == 1111
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1750

		@assert {

			Rm == 1111
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1751

		@assert {

			Rm == 1111
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1752

		@assert {

			Rm == 1111
			size == 1
			type == 1001
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1753

		@assert {

			Rm == 1111
			size == 1
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1754

		@assert {

			Rm == 1111
			size == 1
			type == 1001
			align == 0

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

		@subid 1755

		@assert {

			Rm == 1111
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1756

		@assert {

			Rm == 1111
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1757

		@assert {

			Rm == 1111
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1758

		@assert {

			Rm == 1111
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1759

		@assert {

			Rm == 1111
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1760

		@assert {

			Rm == 1111
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1761

		@assert {

			Rm == 1111
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1762

		@assert {

			Rm == 1111
			size == 10
			type == 1001
			align == 1

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

		@subid 1763

		@assert {

			Rm == 1111
			size == 10
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessOffset(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1764

		@assert {

			Rm == 1111
			size == 10
			type == 1001
			align == 0

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

		@subid 1765

		@assert {

			Rm == 1111
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1766

		@assert {

			Rm == 1111
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1767

		@assert {

			Rm == 1111
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1768

		@assert {

			Rm == 1111
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1769

		@assert {

			Rm == 1101
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1770

		@assert {

			Rm == 1101
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1771

		@assert {

			Rm == 1101
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1772

		@assert {

			Rm == 1101
			size == 0
			type == 1001
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1773

		@assert {

			Rm == 1101
			size == 0
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1774

		@assert {

			Rm == 1101
			size == 0
			type == 1001
			align == 0

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

		@subid 1775

		@assert {

			Rm == 1101
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1776

		@assert {

			Rm == 1101
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1777

		@assert {

			Rm == 1101
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1778

		@assert {

			Rm == 1101
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1779

		@assert {

			Rm == 1101
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1780

		@assert {

			Rm == 1101
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1781

		@assert {

			Rm == 1101
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1782

		@assert {

			Rm == 1101
			size == 1
			type == 1001
			align == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 64)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1783

		@assert {

			Rm == 1101
			size == 1
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1784

		@assert {

			Rm == 1101
			size == 1
			type == 1001
			align == 0

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

		@subid 1785

		@assert {

			Rm == 1101
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1786

		@assert {

			Rm == 1101
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1787

		@assert {

			Rm == 1101
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1788

		@assert {

			Rm == 1101
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1789

		@assert {

			Rm == 1101
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1790

		@assert {

			Rm == 1101
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1791

		@assert {

			Rm == 1101
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1792

		@assert {

			Rm == 1101
			size == 10
			type == 1001
			align == 1

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

		@subid 1793

		@assert {

			Rm == 1101
			size == 10
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			maccess = MemAccessPreIndexed(aligned, NULL)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1794

		@assert {

			Rm == 1101
			size == 10
			type == 1001
			align == 0

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

		@subid 1795

		@assert {

			Rm == 1101
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1796

		@assert {

			Rm == 1101
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1797

		@assert {

			Rm == 1101
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1798

		@assert {

			Rm == 1101
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1799

		@assert {

			Rm != 11x1
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1800

		@assert {

			Rm != 11x1
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1801

		@assert {

			Rm != 11x1
			size == 0
			type == 1000
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1802

		@assert {

			Rm != 11x1
			size == 0
			type == 1001
			align == 1

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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1803

		@assert {

			Rm != 11x1
			size == 0
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1804

		@assert {

			Rm != 11x1
			size == 0
			type == 1001
			align == 0

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

		@subid 1805

		@assert {

			Rm != 11x1
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1806

		@assert {

			Rm != 11x1
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1807

		@assert {

			Rm != 11x1
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1808

		@assert {

			Rm != 11x1
			size == 0
			type == 11
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

		@asm vld2.8 list maccess

	}

	@syntax {

		@subid 1809

		@assert {

			Rm != 11x1
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1810

		@assert {

			Rm != 11x1
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1811

		@assert {

			Rm != 11x1
			size == 1
			type == 1000
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1812

		@assert {

			Rm != 11x1
			size == 1
			type == 1001
			align == 1

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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1813

		@assert {

			Rm != 11x1
			size == 1
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1814

		@assert {

			Rm != 11x1
			size == 1
			type == 1001
			align == 0

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

		@subid 1815

		@assert {

			Rm != 11x1
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1816

		@assert {

			Rm != 11x1
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1817

		@assert {

			Rm != 11x1
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1818

		@assert {

			Rm != 11x1
			size == 1
			type == 11
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

		@asm vld2.16 list maccess

	}

	@syntax {

		@subid 1819

		@assert {

			Rm != 11x1
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1820

		@assert {

			Rm != 11x1
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1821

		@assert {

			Rm != 11x1
			size == 10
			type == 1000
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1822

		@assert {

			Rm != 11x1
			size == 10
			type == 1001
			align == 1

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

		@subid 1823

		@assert {

			Rm != 11x1
			size == 10
			type == 1001
			align == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim2(dwvec_D, dwvec_D_2)
			reg_N = Register(Rn)
			aligned = AlignedRegister(reg_N, 128)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(aligned, reg_M)

		}

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1824

		@assert {

			Rm != 11x1
			size == 10
			type == 1001
			align == 0

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

	@syntax {

		@subid 1825

		@assert {

			Rm != 11x1
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1826

		@assert {

			Rm != 11x1
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1827

		@assert {

			Rm != 11x1
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

	@syntax {

		@subid 1828

		@assert {

			Rm != 11x1
			size == 10
			type == 11
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

		@asm vld2.32 list maccess

	}

}

