
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


@title STREXB

@id 208

@desc {

	Store Register Exclusive Byte derives an address from a base register value, and stores a byte from a register to memory if the executing processor has exclusive access to the memory addressed. For more information about support for shared memory see Synchronization and semaphores on page A3-114. For information about memory accesses see Memory accesses on page A8-294.

}

@encoding (T1) {

	@word 1 1 1 0 1 0 0 0 1 1 0 0 Rn(4) Rt(4) 1 1 1 1 0 1 0 0 Rd(4)

	@syntax {

		@subid 654

		@conv {

			reg_D = Register(Rd)
			reg_T = Register(Rt)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm strexb reg_D reg_T maccess

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 1 1 0 0 Rn(4) Rd(4) 1 1 1 1 1 0 0 1 Rt(4)

	@syntax {

		@subid 655

		@conv {

			reg_D = Register(Rd)
			reg_T = Register(Rt)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm strexb reg_D reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

