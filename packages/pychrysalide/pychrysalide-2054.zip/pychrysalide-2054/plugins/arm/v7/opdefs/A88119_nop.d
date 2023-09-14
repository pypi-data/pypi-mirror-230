
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


@title NOP

@id 114

@desc {

	No Operation does nothing. This instruction can be used for instruction alignment purposes. See Pre-UAL pseudo-instruction NOP on page AppxH-2472 for details of NOP before the introduction of UAL and the ARMv6K and ARMv6T2 architecture variants. Note The timing effects of including a NOP instruction in a program are not guaranteed. It can increase execution time, leave it unchanged, or even reduce it. Therefore, NOP instructions are not suitable for timing loops.

}

@encoding (t1) {

	@half 1 0 1 1 1 1 1 1 0 0 0 0 0 0 0 0

	@syntax {

		@subid 355

		@asm nop

	}

}

@encoding (T2) {

	@word 1 1 1 1 0 0 1 1 1 0 1 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

	@syntax {

		@subid 356

		@asm nop.w

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 1 0 0 1 0 0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0

	@syntax {

		@subid 357

		@asm nop

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

