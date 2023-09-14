
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


@title VPOP

@id 348

@desc {

	Vector Pop loads multiple consecutive extension registers from the stack. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 and Summary of access controls for Advanced SIMD functionality on page B1-1232 summarize these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 0 0 1 D(1) 1 1 1 1 0 1 Vd(4) 1 0 1 1 imm8(8)

	@syntax {

		@subid 2691

		@conv {

			list = DynamicVectorTable(SRM_DOUBLE_WORD, imm8, Vd:D, 2)

		}

		@asm vpop list

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 1 0 0 1 D(1) 1 1 1 1 0 1 Vd(4) 1 0 1 0 imm8(8)

	@syntax {

		@subid 2692

		@conv {

			list = DynamicVectorTable(SRM_SINGLE_WORD, imm8, Vd:D, 1)

		}

		@asm vpop list

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 0 0 1 D(1) 1 1 1 1 0 1 Vd(4) 1 0 1 1 imm8(8)

	@syntax {

		@subid 2693

		@conv {

			list = DynamicVectorTable(SRM_DOUBLE_WORD, imm8, Vd:D, 2)

		}

		@asm vpop list

	}

}

@encoding (A2) {

	@word 1 1 1 0 1 1 0 0 1 D(1) 1 1 1 1 0 1 Vd(4) 1 0 1 0 imm8(8)

	@syntax {

		@subid 2694

		@conv {

			list = DynamicVectorTable(SRM_SINGLE_WORD, imm8, Vd:D, 1)

		}

		@asm vpop list

	}

}

