
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


@title MRRC, MRRC2

@id 103

@desc {

	Move to two ARM core registers from Coprocessor causes a coprocessor to transfer values to two ARM core registers. If no coprocessor can execute the instruction, an Undefined Instruction exception is generated. This is a generic coprocessor instruction. Some of the fields have no functionality defined by the architecture and are free for use by the coprocessor instruction set designer. These are the opc1 and CRm fields. However, coprocessors CP8-CP15 are reserved for use by ARM, and this manual defines the valid MRRC and MRRC2 instructions when coproc is in the range p8-p15. For more information see Coprocessor support on page A2-94. In an implementation that includes the Virtualization Extensions, MRRC accesses to system control registers can be trapped to Hyp mode, meaning that an attempt to execute an MRRC instruction in a Non-secure mode other than Hyp mode, that would be permitted in the absence of the Hyp trap controls, generates a Hyp Trap exception. For more information, see Traps to the hypervisor on page B1-1247. Note Because of the range of possible traps to Hyp mode, the MRRC pseudocode does not show these possible traps.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 0 0 0 1 0 1 Rt2(4) Rt(4) coproc(4) opc1(4) CRm(4)

	@syntax {

		@subid 331

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			direct_CRm = UInt(CRm)

		}

		@asm mrrc cp direct_opc1 reg_T reg_T2 direct_CRm

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 1 0 0 0 1 0 1 Rt2(4) Rt(4) coproc(4) opc1(4) CRm(4)

	@syntax {

		@subid 332

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			direct_CRm = UInt(CRm)

		}

		@asm mrrc cp direct_opc1 reg_T reg_T2 direct_CRm

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 0 0 0 1 0 1 Rt2(4) Rt(4) coproc(4) opc1(4) CRm(4)

	@syntax {

		@subid 333

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			direct_CRm = UInt(CRm)

		}

		@asm mrrc cp direct_opc1 reg_T reg_T2 direct_CRm

	}

}

@encoding (A2) {

	@word 1 1 1 1 1 1 0 0 0 1 0 1 Rt2(4) Rt(4) coproc(4) opc1(4) CRm(4)

	@syntax {

		@subid 334

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			direct_CRm = UInt(CRm)

		}

		@asm mrrc cp direct_opc1 reg_T reg_T2 direct_CRm

	}

}

