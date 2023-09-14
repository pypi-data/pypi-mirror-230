
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


@title LDREXD

@id 72

@desc {

	Load Register Exclusive Doubleword derives an address from a base register value, loads a 64-bit doubleword from memory, writes it to two registers and: • if the address has the Shared Memory attribute, marks the physical address as exclusive access for the executing processor in a global monitor • causes the executing processor to indicate an active exclusive access in the local monitor. For more information about support for shared memory see Synchronization and semaphores on page A3-114. For information about memory accesses see Memory accesses on page A8-294.

}

@encoding (T1) {

	@word 1 1 1 0 1 0 0 0 1 1 0 1 Rn(4) Rt(4) Rt2(4) 0 1 1 1 1 1 1 1

	@syntax {

		@subid 220

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm ldrexd reg_T reg_T2 maccess

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 1 0 1 1 Rn(4) Rt(4) 1 1 1 1 1 0 0 1 1 1 1 1

	@syntax {

		@subid 221

		@conv {

			reg_T = Register(Rt)
			reg_T2 = NextRegister(Rt)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm ldrexd reg_T reg_T2 maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

