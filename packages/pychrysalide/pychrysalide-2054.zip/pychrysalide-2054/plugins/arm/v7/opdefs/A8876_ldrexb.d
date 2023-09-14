
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


@title LDREXB

@id 71

@desc {

	Load Register Exclusive Byte derives an address from a base register value, loads a byte from memory, zero-extends it to form a 32-bit word, writes it to a register and: • if the address has the Shared Memory attribute, marks the physical address as exclusive access for the executing processor in a global monitor • causes the executing processor to indicate an active exclusive access in the local monitor. For more information about support for shared memory see Synchronization and semaphores on page A3-114. For information about memory accesses see Memory accesses on page A8-294.

}

@encoding (T1) {

	@word 1 1 1 0 1 0 0 0 1 1 0 1 Rn(4) Rt(4) 1 1 1 1 0 1 0 0 1 1 1 1

	@syntax {

		@subid 218

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm ldrexb reg_T maccess

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 1 1 0 1 Rn(4) Rt(4) 1 1 1 1 1 0 0 1 1 1 1 1

	@syntax {

		@subid 219

		@conv {

			reg_T = Register(Rt)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm ldrexb reg_T maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

