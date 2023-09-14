
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


@title UDF

@id 242

@desc {

	Permanently Undefined generates an Undefined Instruction exception. The encodings for UDF used in this section are defined as permanently UNDEFINED in the versions of the architecture specified in this section. Issue C.a of this manual first defines an assembler mnemonic for these encodings. However: • with the Thumb instruction set, ARM deprecates using the UDF instruction in an IT block • in the ARM instruction set, UDF is not conditional.

}

@encoding (t1) {

	@half 1 1 0 1 1 1 1 0 imm8(8)

	@syntax {

		@subid 742

		@conv {

			imm32 = ZeroExtend(imm8, 32)

		}

		@asm udf imm32

	}

}

@encoding (T2) {

	@word 1 1 1 1 0 1 1 1 1 1 1 1 imm4(4) 1 0 1 0 imm12(12)

	@syntax {

		@subid 743

		@conv {

			imm32 = ZeroExtend(imm4:imm12, 32)

		}

		@asm udf.w imm32

	}

}

@encoding (A1) {

	@word 1 1 1 0 0 1 1 1 1 1 1 1 imm12(12) 1 1 1 1 imm4(4)

	@syntax {

		@subid 744

		@conv {

			imm32 = ZeroExtend(imm12:imm4, 32)

		}

		@asm udf imm32

	}

}

