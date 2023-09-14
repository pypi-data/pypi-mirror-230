
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


@title LDC, LDC2 (literal)

@id 51

@desc {

	Load Coprocessor loads memory data from a sequence of consecutive memory addresses to a coprocessor. If no coprocessor can execute the instruction, an Undefined Instruction exception is generated. This is a generic coprocessor instruction. Some of the fields have no functionality defined by the architecture and are free for use by the coprocessor instruction set designer. These are the D bit, the CRd field, and in the Unindexed addressing mode only, the imm8 field. However, coprocessors CP8-CP15 are reserved for use by ARM, and this manual defines the valid LDC and LDC2 instructions when coproc is in the range p8-p15. For more information see Coprocessor support on page A2-94. In an implementation that includes the Virtualization Extensions, the permitted LDC access to a system control register can be trapped to Hyp mode, meaning that an attempt to execute an LDC instruction in a Non-secure mode other than Hyp mode, that would be permitted in the absence of the Hyp trap controls, generates a Hyp Trap exception. For more information, see Trapping general CP14 accesses to debug registers on page B1-1260. Note For simplicity, the LDC pseudocode does not show this possible trap to Hyp mode.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 0 P(1) U(1) D(1) W(1) 1 1 1 1 1 CRd(4) coproc(4) imm8(8)

	@syntax {

		@subid 157

		@assert {

			P == 1
			W == 0

		}

		@conv {

			cp = CoProcessor(coproc)
			direct_CRd = UInt(CRd)
			imm32 = ZeroExtend(imm8:'00', 32)

		}

		@asm ldc cp direct_CRd imm32

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 1 0 P(1) U(1) D(1) W(1) 1 1 1 1 1 CRd(4) coproc(4) imm8(8)

	@syntax {

		@subid 158

		@assert {

			P == 1
			W == 0

		}

		@conv {

			cp = CoProcessor(coproc)
			direct_CRd = UInt(CRd)
			imm32 = ZeroExtend(imm8:'00', 32)

		}

		@asm ldc cp direct_CRd imm32

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 0 P(1) U(1) D(1) W(1) 1 1 1 1 1 CRd(4) coproc(4) imm8(8)

	@syntax {

		@subid 159

		@assert {

			P == 0
			U == 1
			W == 0

		}

		@conv {

			cp = CoProcessor(coproc)
			direct_CRd = UInt(CRd)
			reg_PC = Register(15)
			maccess = MemAccessOffset(reg_PC, NULL)
			option = ZeroExtend(imm8:'00', 32)

		}

		@asm ldc cp direct_CRd maccess option

	}

	@syntax {

		@subid 160

		@assert {

			P == 1
			W == 0

		}

		@conv {

			cp = CoProcessor(coproc)
			direct_CRd = UInt(CRd)
			imm32 = ZeroExtend(imm8:'00', 32)

		}

		@asm ldc cp direct_CRd imm32

	}

}

@encoding (A2) {

	@word 1 1 1 1 1 1 0 P(1) U(1) D(1) W(1) 1 1 1 1 1 CRd(4) coproc(4) imm8(8)

	@syntax {

		@subid 161

		@assert {

			P == 0
			U == 1
			W == 0

		}

		@conv {

			cp = CoProcessor(coproc)
			direct_CRd = UInt(CRd)
			reg_PC = Register(15)
			maccess = MemAccessOffset(reg_PC, NULL)
			option = ZeroExtend(imm8:'00', 32)

		}

		@asm ldc cp direct_CRd maccess option

	}

	@syntax {

		@subid 162

		@assert {

			P == 1
			W == 0

		}

		@conv {

			cp = CoProcessor(coproc)
			direct_CRd = UInt(CRd)
			imm32 = ZeroExtend(imm8:'00', 32)

		}

		@asm ldc cp direct_CRd imm32

	}

}

