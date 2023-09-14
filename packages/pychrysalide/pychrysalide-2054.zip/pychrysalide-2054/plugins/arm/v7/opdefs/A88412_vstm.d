
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


@title VSTM

@id 372

@desc {

	Vector Store Multiple stores multiple extension registers to consecutive memory locations using an address from an ARM core register. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 and Summary of access controls for Advanced SIMD functionality on page B1-1232 summarize these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 0 P(1) U(1) D(1) W(1) 0 Rn(4) Vd(4) 1 0 1 1 imm8(8)

	@syntax {

		@subid 3645

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_DOUBLE_WORD, imm8, Vd:D, 2)

		}

		@asm vstmia wb_reg list

	}

	@syntax {

		@subid 3646

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_DOUBLE_WORD, imm8, Vd:D, 2)

		}

		@asm vstmdb wb_reg list

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 1 0 P(1) U(1) D(1) W(1) 0 Rn(4) Vd(4) 1 0 1 0 imm8(8)

	@syntax {

		@subid 3647

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_SINGLE_WORD, imm8, Vd:D, 1)

		}

		@asm vstmia wb_reg list

	}

	@syntax {

		@subid 3648

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_SINGLE_WORD, imm8, Vd:D, 1)

		}

		@asm vstmdb wb_reg list

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 0 P(1) U(1) D(1) W(1) 0 Rn(4) Vd(4) 1 0 1 1 imm8(8)

	@syntax {

		@subid 3649

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_DOUBLE_WORD, imm8, Vd:D, 2)

		}

		@asm vstmia wb_reg list

	}

	@syntax {

		@subid 3650

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_DOUBLE_WORD, imm8, Vd:D, 2)

		}

		@asm vstmdb wb_reg list

	}

}

@encoding (A2) {

	@word 1 1 1 0 1 1 0 P(1) U(1) D(1) W(1) 0 Rn(4) Vd(4) 1 0 1 0 imm8(8)

	@syntax {

		@subid 3651

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_SINGLE_WORD, imm8, Vd:D, 1)

		}

		@asm vstmia wb_reg list

	}

	@syntax {

		@subid 3652

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			list = DynamicVectorTable(SRM_SINGLE_WORD, imm8, Vd:D, 1)

		}

		@asm vstmdb wb_reg list

	}

}

