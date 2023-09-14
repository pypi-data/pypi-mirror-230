
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


@title CPS (Thumb)

@id 388

@desc {

	Change Processor State changes one or more of the CPSR.{A, I, F} interrupt mask bits and the CPSR.M mode field, without changing the other CPSR bits. CPS is treated as NOP if executed in User mode. CPS is UNPREDICTABLE if it is either: • attempting to change to a mode that is not permitted in the context in which it is executed, see Restrictions on updates to the CPSR.M field on page B9-1970 • executed in Debug state.

}

@encoding (t1) {

	@half 1 0 1 1 0 1 1 0 0 1 1 im(1) 0 A(1) I(1) F(1)

	@syntax {

		@subid 3782

		@assert {

			im == 0

		}

		@conv {

			iflags = IFlagsDefinition(a, i, f)

		}

		@asm cpsie iflags

	}

	@syntax {

		@subid 3783

		@assert {

			im == 1

		}

		@conv {

			iflags = IFlagsDefinition(a, i, f)

		}

		@asm cpsid iflags

	}

}

@encoding (T2) {

	@word 1 1 1 1 0 0 1 1 1 0 1 0 1 1 1 1 1 0 0 0 0 imod(2) M(1) A(1) I(1) F(1) mode(5)

	@syntax {

		@subid 3784

		@assert {

			M == 0
			imod == 10

		}

		@conv {

			iflags = IFlagsDefinition(a, i, f)

		}

		@asm cpsie.w iflags

	}

	@syntax {

		@subid 3785

		@assert {

			M == 0
			imod == 11

		}

		@conv {

			iflags = IFlagsDefinition(a, i, f)

		}

		@asm cpsid.w iflags

	}

	@syntax {

		@subid 3786

		@assert {

			M == 1

		}

		@conv {

			direct_mode = UInt(mode)

		}

		@asm cps.w direct_mode

	}

}

