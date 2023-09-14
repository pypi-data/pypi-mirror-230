
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


@title SRS (ARM)

@id 403

@desc {

	Store Return State stores the LR and SPSR of the current mode to the stack of a specified mode. For information about memory accesses see Memory accesses on page A8-294. SRS is: • UNDEFINED in Hyp mode • UNPREDICTABLE if: — it is executed in User or System mode — it attempts to store the Monitor mode SP when in Non-secure state — NSACR.RFR is set to 1 and it attempts to store the FIQ mode SP when in Non-secure state — if it attempts to store the Hyp mode SP.

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 P(1) U(1) 1 W(1) 0 1 1 0 1 0 0 0 0 0 1 0 1 0 0 0 mode(5)

	@syntax {

		@subid 3821

		@assert {

			P == 0
			U == 0

		}

		@conv {

			reg_SP = Register(13)
			wb_reg = WrittenBackReg(reg_SP, W)
			direct_mode = UInt(mode)

		}

		@asm srsda wb_reg direct_mode

	}

	@syntax {

		@subid 3822

		@assert {

			P == 1
			U == 0

		}

		@conv {

			reg_SP = Register(13)
			wb_reg = WrittenBackReg(reg_SP, W)
			direct_mode = UInt(mode)

		}

		@asm srsdb wb_reg direct_mode

	}

	@syntax {

		@subid 3823

		@assert {

			P == 0
			U == 1

		}

		@conv {

			reg_SP = Register(13)
			wb_reg = WrittenBackReg(reg_SP, W)
			direct_mode = UInt(mode)

		}

		@asm srsia wb_reg direct_mode

	}

	@syntax {

		@subid 3824

		@assert {

			P == 1
			U == 1

		}

		@conv {

			reg_SP = Register(13)
			wb_reg = WrittenBackReg(reg_SP, W)
			direct_mode = UInt(mode)

		}

		@asm srsib wb_reg direct_mode

	}

}

