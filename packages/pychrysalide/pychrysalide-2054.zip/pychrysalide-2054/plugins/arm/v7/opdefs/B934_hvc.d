
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


@title HVC

@id 391

@desc {

	Hypervisor Call causes a Hypervisor Call exception. For more information see Hypervisor Call (HVC) exception on page B1-1211. Non-secure software executing at PL1 can use this instruction to call the hypervisor to request a service. The HVC instruction is: • UNDEFINED in Secure state, and in User mode in Non-secure state • when SCR.HCE is set to 0, UNDEFINED in Non-secure PL1 modes and UNPREDICTABLE in Hyp mode • UNPREDICTABLE in Debug state. On executing an HVC instruction, the HSR reports the exception as a Hypervisor Call exception, using the EC value 0x12, and captures the value of the immediate argument, see Use of the HSR on page B3-1424.

}

@encoding (T1) {

	@word 1 1 1 1 0 1 1 1 1 1 1 0 imm4(4) 1 0 0 0 imm12(12)

	@syntax {

		@subid 3792

		@conv {

			imm16 = UInt(imm4:imm12)

		}

		@asm hvc imm16

	}

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 1 0 0 imm12(12) 0 1 1 1 imm4(4)

	@syntax {

		@subid 3793

		@conv {

			imm16 = UInt(imm12:imm4)

		}

		@asm hvc imm16

	}

}

