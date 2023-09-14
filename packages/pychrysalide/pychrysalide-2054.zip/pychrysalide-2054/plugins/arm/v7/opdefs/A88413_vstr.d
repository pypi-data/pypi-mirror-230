
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


@title VSTR

@id 373

@desc {

	This instruction stores a single extension register to memory, using an address from an ARM core register, with an optional offset. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 and Summary of access controls for Advanced SIMD functionality on page B1-1232 summarize these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 0 1 U(1) D(1) 0 0 Rn(4) Vd(4) 1 0 1 1 imm8(8)

	@syntax {

		@subid 3653

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8:'00', 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm vstr dwvec_D maccess

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 1 0 1 U(1) D(1) 0 0 Rn(4) Vd(4) 1 0 1 0 imm8(8)

	@syntax {

		@subid 3654

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8:'00', 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm vstr swvec_D maccess

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 0 1 U(1) D(1) 0 0 Rn(4) Vd(4) 1 0 1 1 imm8(8)

	@syntax {

		@subid 3655

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8:'00', 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm vstr dwvec_D maccess

	}

}

@encoding (A2) {

	@word 1 1 1 0 1 1 0 1 U(1) D(1) 0 0 Rn(4) Vd(4) 1 0 1 0 imm8(8)

	@syntax {

		@subid 3656

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8:'00', 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm vstr swvec_D maccess

	}

}

