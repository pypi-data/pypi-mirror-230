
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


@title POP (Thumb)

@id 126

@desc {

	Pop Multiple Registers loads multiple registers from the stack, loading from consecutive memory locations starting at the address in SP, and updates SP to point just above the loaded data.

}

@encoding (t1) {

	@half 1 0 1 1 1 1 0 P(1) register_list(8)

	@syntax {

		@subid 395

		@conv {

			registers = RegList(P:'0000000':register_list)

		}

		@asm pop registers

	}

	@hooks {

		link = handle_armv7_return_from_pop

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 0 0 0 1 0 1 1 1 1 0 1 P(1) M(1) 0 register_list(13)

	@syntax {

		@subid 396

		@conv {

			registers = RegList(P:M:'0':register_list)

		}

		@asm pop.w registers

	}

	@hooks {

		link = handle_armv7_return_from_pop

	}

}

@encoding (T3) {

	@word 1 1 1 1 1 0 0 0 0 1 0 1 1 1 0 1 Rt(4) 1 0 1 1 0 0 0 0 0 1 0 0

	@syntax {

		@subid 397

		@conv {

			registers = SingleRegList(Rt)

		}

		@asm pop.w registers

	}

	@hooks {

		link = handle_armv7_return_from_pop

	}

}

