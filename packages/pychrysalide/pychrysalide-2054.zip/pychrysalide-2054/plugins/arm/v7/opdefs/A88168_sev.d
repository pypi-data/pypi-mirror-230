
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


@title SEV

@id 163

@desc {

	Send Event is a hint instruction. It causes an event to be signaled to all processors in the multiprocessor system. For more information, see Wait For Event and Send Event on page B1-1199.

}

@encoding (t1) {

	@half 1 0 1 1 1 1 1 1 0 1 0 0 0 0 0 0

	@syntax {

		@subid 491

		@asm sev

	}

}

@encoding (T2) {

	@word 1 1 1 1 0 0 1 1 1 0 1 0 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0

	@syntax {

		@subid 492

		@asm sev.w

	}

}

@encoding (A1) {

	@word cond(4) 0 0 1 1 0 0 1 0 0 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 1 0 0

	@syntax {

		@subid 493

		@asm sev

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

