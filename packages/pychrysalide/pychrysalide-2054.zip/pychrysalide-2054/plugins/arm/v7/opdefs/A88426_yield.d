
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


@title YIELD

@id 386

@desc {

	YIELD is a hint instruction. Software with a multithreading capability can use a YIELD instruction to indicate to the hardware that it is performing a task, for example a spin-lock, that could be swapped out to improve overall system performance. Hardware can use this hint to suspend and resume multiple software threads if it supports the capability. For more information about the recommended use of this instruction see The Yield instruction on page A4-178.

}

@encoding (t1) {

	@half 1 0 1 1 1 1 1 1 0 0 0 1 0 0 0 0

	@syntax {

		@subid 3777

		@asm yield

	}

}

@encoding (T2) {

	@word 1 1 1 1 0 0 1 1 1 0 1 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1

	@syntax {

		@subid 3778

		@asm yield.w

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 1 0 0 1 0 0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 1

	@syntax {

		@subid 3779

		@asm yield

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

