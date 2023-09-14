
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


@title BKPT

@id 23

@desc {

	Breakpoint causes a software breakpoint to occur. Breakpoint is always unconditional, even when inside an IT block.

}

@encoding (t1) {

	@half 1 0 1 1 1 1 1 0 imm8(8)

	@syntax {

		@subid 85

		@conv {

			imm32 = ZeroExtend(imm8, 32)

		}

		@asm bkpt imm32

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 0 1 0 imm12(12) 0 1 1 1 imm4(4)

	@syntax {

		@subid 86

		@conv {

			imm32 = ZeroExtend(imm12:imm4, 32)

		}

		@asm bkpt imm32

	}

}

