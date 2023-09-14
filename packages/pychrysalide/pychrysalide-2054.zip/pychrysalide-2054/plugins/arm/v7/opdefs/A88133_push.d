
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


@title PUSH

@id 128

@desc {

	Push Multiple Registers stores multiple registers to the stack, storing to consecutive memory locations ending just below the address in SP, and updates SP to point to the start of the stored data.

}

@encoding (t1) {

	@half 1 0 1 1 0 1 0 M(1) register_list(8)

	@syntax {

		@subid 400

		@conv {

			registers = RegList('0':M:'000000':register_list)

		}

		@asm push registers

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 0 0 1 0 0 1 0 1 1 0 1 0 M(1) 0 register_list(13)

	@syntax {

		@subid 401

		@conv {

			registers = RegList('0':M:'0':register_list)

		}

		@asm push.w registers

	}

}

@encoding (T3) {

	@word 1 1 1 1 1 0 0 0 0 1 0 0 1 1 0 1 Rt(4) 1 1 0 1 0 0 0 0 0 1 0 0

	@syntax {

		@subid 402

		@conv {

			registers = SingleRegList(Rt)

		}

		@asm push.w registers

	}

}

@encoding (A1) {

	@word cond(4) 1 0 0 1 0 0 1 0 1 1 0 1 register_list(16)

	@syntax {

		@subid 403

		@conv {

			registers = RegList(register_list)

		}

		@asm push registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

@encoding (A2) {

	@word cond(4) 0 1 0 1 0 0 1 0 1 1 0 1 Rt(4) 0 0 0 0 0 0 0 0 0 1 0 0

	@syntax {

		@subid 404

		@conv {

			registers = SingleRegList(Rt)

		}

		@asm push registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

