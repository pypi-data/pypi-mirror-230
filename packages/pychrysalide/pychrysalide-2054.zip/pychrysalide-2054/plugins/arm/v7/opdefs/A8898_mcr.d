
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


@title MCR, MCR2

@id 93

@desc {

	Move to Coprocessor from ARM core register passes the value of an ARM core register to a coprocessor. If no coprocessor can execute the instruction, an Undefined Instruction exception is generated. This is a generic coprocessor instruction. Some of the fields have no functionality defined by the architecture and are free for use by the coprocessor instruction set designer. These are the opc1, opc2, CRn, and CRm fields. However, coprocessors CP8-CP15 are reserved for use by ARM, and this manual defines the valid MCR and MCR2 instructions when coproc is in the range p8-p15. For more information see Coprocessor support on page A2-94. In an implementation that includes the Virtualization Extensions, MCR accesses to system control registers can be trapped to Hyp mode, meaning that an attempt to execute an MCR instruction in a Non-secure mode other than Hyp mode, that would be permitted in the absence of the Hyp trap controls, generates a Hyp Trap exception. For more information, see Traps to the hypervisor on page B1-1247. Note Because of the range of possible traps to Hyp mode, the MCR pseudocode does not show these possible traps.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 opc1(3) 0 CRn(4) Rt(4) coproc(4) opc2(3) 1 CRm(4)

	@syntax {

		@subid 299

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			reg_T = Register(Rt)
			direct_CRn = UInt(CRn)
			direct_CRm = UInt(CRm)
			direct_opc2 = UInt(opc2)

		}

		@asm mcr cp direct_opc1 reg_T direct_CRn direct_CRm ?direct_opc2

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 1 1 0 opc1(3) 0 CRn(4) Rt(4) coproc(4) opc2(3) 1 CRm(4)

	@syntax {

		@subid 300

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			reg_T = Register(Rt)
			direct_CRn = UInt(CRn)
			direct_CRm = UInt(CRm)
			direct_opc2 = UInt(opc2)

		}

		@asm mcr cp direct_opc1 reg_T direct_CRn direct_CRm ?direct_opc2

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 opc1(3) 0 CRn(4) Rt(4) coproc(4) opc2(3) 1 CRm(4)

	@syntax {

		@subid 301

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			reg_T = Register(Rt)
			direct_CRn = UInt(CRn)
			direct_CRm = UInt(CRm)
			direct_opc2 = UInt(opc2)

		}

		@asm mcr cp direct_opc1 reg_T direct_CRn direct_CRm ?direct_opc2

	}

}

@encoding (A2) {

	@word 1 1 1 1 1 1 1 0 opc1(3) 0 CRn(4) Rt(4) coproc(4) opc2(3) 1 CRm(4)

	@syntax {

		@subid 302

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			reg_T = Register(Rt)
			direct_CRn = UInt(CRn)
			direct_CRm = UInt(CRm)
			direct_opc2 = UInt(opc2)

		}

		@asm mcr cp direct_opc1 reg_T direct_CRn direct_CRm ?direct_opc2

	}

}

