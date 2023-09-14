
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


@title VLD1 (multiple single elements)

@id 312

@desc {

	This instruction loads elements from memory into one, two, three, or four registers, without de-interleaving. Every element of each register is loaded. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 1 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 1373

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1374

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1375

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1376

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1377

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1378

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1379

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1380

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1381

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1382

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1383

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1384

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1385

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1386

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1387

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1388

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1389

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1390

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1391

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1392

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1393

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1394

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1395

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1396

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1397

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1398

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1399

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1400

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1401

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1402

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1403

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1404

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1405

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1406

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1407

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1408

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1409

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1410

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1411

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1412

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1413

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1414

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1415

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1416

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1417

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1418

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1419

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1420

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1421

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1422

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1423

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1424

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1425

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1426

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1427

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1428

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1429

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1430

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1431

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1432

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1433

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1434

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1435

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1436

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1437

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1438

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1439

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1440

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1441

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1442

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1443

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1444

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1445

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1446

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1447

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1448

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1449

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1450

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1451

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1452

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1453

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1454

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1455

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1456

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1457

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1458

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1459

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1460

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1461

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1462

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1463

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1464

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1465

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1466

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1467

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1468

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1469

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1470

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1471

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1472

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1473

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1474

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1475

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1476

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1477

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1478

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1479

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1480

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

		@asm vld1.64 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 0 D(1) 1 0 Rn(4) Vd(4) type(4) size(2) align(2) Rm(4)

	@syntax {

		@subid 1481

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1482

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1483

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1484

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1485

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1486

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1487

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1488

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1489

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1490

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1491

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1492

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1493

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1494

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1495

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1496

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1497

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1498

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1499

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1500

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1501

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1502

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1503

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1504

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1505

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1506

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1507

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1508

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1509

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1510

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1511

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1512

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1513

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1514

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1515

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1516

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1517

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1518

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1519

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1520

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1521

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1522

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1523

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1524

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1525

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1526

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1527

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1528

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1529

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1530

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1531

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1532

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1533

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1534

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1535

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1536

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1537

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1538

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1539

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1540

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1541

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1542

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1543

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1544

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1545

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1546

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1547

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1548

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1549

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1550

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1551

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1552

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1553

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1554

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1555

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1556

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1557

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1558

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1559

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1560

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1561

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

		@asm vld1.8 list maccess

	}

	@syntax {

		@subid 1562

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1563

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1564

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1565

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1566

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1567

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1568

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1569

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1570

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

		@asm vld1.16 list maccess

	}

	@syntax {

		@subid 1571

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1572

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1573

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1574

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1575

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1576

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1577

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1578

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1579

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

		@asm vld1.32 list maccess

	}

	@syntax {

		@subid 1580

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1581

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1582

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1583

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1584

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1585

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1586

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1587

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

		@asm vld1.64 list maccess

	}

	@syntax {

		@subid 1588

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

		@asm vld1.64 list maccess

	}

}

