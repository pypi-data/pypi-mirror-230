
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


@title PKH

@id 120

@desc {

	Pack Halfword combines one halfword of its first operand with the other halfword of its shifted second operand.

}

@encoding (T1) {

	@word 1 1 1 0 1 0 1 0 1 1 0 S(1) Rn(4) 0 imm3(3) Rd(4) imm2(2) tb(1) T(1) Rm(4)

	@syntax {

		@subid 373

		@assert {

			tb == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(tb:'0', imm3:imm2)

		}

		@asm pkhbt ?reg_D reg_N reg_M ?shift

	}

	@syntax {

		@subid 374

		@assert {

			tb == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(tb:'0', imm3:imm2)

		}

		@asm pkhtb ?reg_D reg_N reg_M ?shift

	}

}

@encoding (A1) {

	@word cond(4) 0 1 1 0 1 0 0 0 Rn(4) Rd(4) imm5(5) tb(1) 0 1 Rm(4)

	@syntax {

		@subid 375

		@assert {

			tb == 0

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(tb:'0', imm5)

		}

		@asm pkhbt ?reg_D reg_N reg_M ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 376

		@assert {

			tb == 1

		}

		@conv {

			reg_D = Register(Rd)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			shift = DecodeImmShift(tb:'0', imm5)

		}

		@asm pkhtb ?reg_D reg_N reg_M ?shift

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

