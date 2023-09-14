
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


@title CDP, CDP2

@id 29

@desc {

	Coprocessor Data Processing tells a coprocessor to perform an operation that is independent of ARM core registers and memory. If no coprocessor can execute the instruction, an Undefined Instruction exception is generated. This is a generic coprocessor instruction. Some of the fields have no functionality defined by the architecture and are free for use by the coprocessor instruction set designer. These are the opc1, opc2, CRd, CRn, and CRm fields. However, coprocessors CP8-CP15 are reserved for use by ARM, and this manual defines the valid CDP and CDP2 instructions when coproc is in the range p8-p15. For more information see Coprocessor support on page A2-94.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 opc1(4) CRn(4) CRd(4) coproc(4) opc2(3) 0 CRm(4)

	@syntax {

		@subid 99

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			direct_CRd = UInt(CRd)
			direct_CRn = UInt(CRn)
			direct_CRm = UInt(CRm)
			direct_opc2 = UInt(opc2)

		}

		@asm cdp cp direct_opc1 direct_CRd direct_CRn direct_CRm ?direct_opc2

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 1 1 0 opc1(4) CRn(4) CRd(4) coproc(4) opc2(3) 0 CRm(4)

	@syntax {

		@subid 100

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			direct_CRd = UInt(CRd)
			direct_CRn = UInt(CRn)
			direct_CRm = UInt(CRm)
			direct_opc2 = UInt(opc2)

		}

		@asm cdp cp direct_opc1 direct_CRd direct_CRn direct_CRm ?direct_opc2

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 opc1(4) CRn(4) CRd(4) coproc(4) opc2(3) 0 CRm(4)

	@syntax {

		@subid 101

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			direct_CRd = UInt(CRd)
			direct_CRn = UInt(CRn)
			direct_CRm = UInt(CRm)
			direct_opc2 = UInt(opc2)

		}

		@asm cdp cp direct_opc1 direct_CRd direct_CRn direct_CRm ?direct_opc2

	}

}

@encoding (A2) {

	@word 1 1 1 1 1 1 1 0 opc1(4) CRn(4) CRd(4) coproc(4) opc2(3) 0 CRm(4)

	@syntax {

		@subid 102

		@conv {

			cp = CoProcessor(coproc)
			direct_opc1 = UInt(opc1)
			direct_CRd = UInt(CRd)
			direct_CRn = UInt(CRn)
			direct_CRm = UInt(CRm)
			direct_opc2 = UInt(opc2)

		}

		@asm cdp cp direct_opc1 direct_CRd direct_CRn direct_CRm ?direct_opc2

	}

}

