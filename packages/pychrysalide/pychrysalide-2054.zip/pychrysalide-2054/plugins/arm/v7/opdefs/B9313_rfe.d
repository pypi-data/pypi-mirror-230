
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


@title RFE

@id 400

@desc {

	Return From Exception loads the PC and the CPSR from the word at the specified address and the following word respectively. For information about memory accesses see Memory accesses on page A8-294. RFE is: • UNDEFINED in Hyp mode. • UNPREDICTABLE in: — The cases described in Restrictions on exception return instructions on page B9-1970. Note As identified in Restrictions on exception return instructions on page B9-1970, RFE differs from other exception return instructions in that it can be executed in System mode. — Debug state.

}

@encoding (T1) {

	@word 1 1 1 0 1 0 0 0 0 0 W(1) 1 Rn(4) 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0

	@syntax {

		@subid 3811

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)

		}

		@asm rfedb wb_reg

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 0 0 1 1 0 W(1) 1 Rn(4) 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0

	@syntax {

		@subid 3812

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)

		}

		@asm rfeia wb_reg

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 P(1) U(1) 0 W(1) 1 Rn(4) 0 0 0 0 1 0 1 0 0 0 0 0 0 0 0 0

	@syntax {

		@subid 3813

		@assert {

			P == 0
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)

		}

		@asm rfeda wb_reg

	}

	@syntax {

		@subid 3814

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)

		}

		@asm rfedb wb_reg

	}

	@syntax {

		@subid 3815

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)

		}

		@asm rfeia wb_reg

	}

	@syntax {

		@subid 3816

		@assert {

			P == 1
			U == 1

		}

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)

		}

		@asm rfeib wb_reg

	}

}

