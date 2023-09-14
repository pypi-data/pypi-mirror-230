
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


@title VLDM

@id 320

@desc {

	Vector Load Multiple loads multiple extension registers from consecutive memory locations using an address from an ARM core register. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 summarizes these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 0 P(1) U(1) D(1) W(1) 1 Rn(4) Vd(4) 1 0 1 1 imm8(8)

	@syntax {

		@subid 2249

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_DOUBLE_WORD, imm8, Vd:D, 2)

		}

		@asm vldmia wb_reg list

	}

	@syntax {

		@subid 2250

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_DOUBLE_WORD, imm8, Vd:D, 2)

		}

		@asm vldmdb wb_reg list

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 1 0 P(1) U(1) D(1) W(1) 1 Rn(4) Vd(4) 1 0 1 0 imm8(8)

	@syntax {

		@subid 2251

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_SINGLE_WORD, imm8, Vd:D, 1)

		}

		@asm vldmia wb_reg list

	}

	@syntax {

		@subid 2252

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_SINGLE_WORD, imm8, Vd:D, 1)

		}

		@asm vldmdb wb_reg list

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 0 P(1) U(1) D(1) W(1) 1 Rn(4) Vd(4) 1 0 1 1 imm8(8)

	@syntax {

		@subid 2253

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_DOUBLE_WORD, imm8, Vd:D, 2)

		}

		@asm vldmia wb_reg list

	}

	@syntax {

		@subid 2254

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_DOUBLE_WORD, imm8, Vd:D, 2)

		}

		@asm vldmdb wb_reg list

	}

}

@encoding (A2) {

	@word 1 1 1 0 1 1 0 P(1) U(1) D(1) W(1) 1 Rn(4) Vd(4) 1 0 1 0 imm8(8)

	@syntax {

		@subid 2255

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_SINGLE_WORD, imm8, Vd:D, 1)

		}

		@asm vldmia wb_reg list

	}

	@syntax {

		@subid 2256

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_SINGLE_WORD, imm8, Vd:D, 1)

		}

		@asm vldmdb wb_reg list

	}

}

