
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


@title PLI (immediate, literal)

@id 124

@desc {

	Preload Instruction signals the memory system that instruction memory accesses from a specified address are likely in the near future. The memory system can respond by taking actions that are expected to speed up the memory accesses when they do occur, such as pre-loading the cache line containing the specified address into the instruction cache. The effect of a PLI instruction is IMPLEMENTATION DEFINED. For more information, see Preloading caches on page A3-157 and Behavior of Preload Data (PLD, PLDW) and Preload Instruction (PLI) with caches on page B2-1269.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 1 0 0 1 Rn(4) 1 1 1 1 imm12(12)

	@syntax {

		@subid 389

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm pli maccess

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 0 0 1 0 0 0 1 Rn(4) 1 1 1 1 1 1 0 0 imm8(8)

	@syntax {

		@subid 390

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm pli maccess

	}

}

@encoding (T3) {

	@word 1 1 1 1 1 0 0 1 U(1) 0 0 1 1 1 1 1 1 1 1 1 imm12(12)

	@syntax {

		@subid 391

		@conv {

			imm32 = ZeroExtend(imm12, 32)

		}

		@asm pli imm32

	}

}

@encoding (A1) {

	@word 1 1 1 1 0 1 0 0 U(1) 1 0 1 Rn(4) 1 1 1 1 imm12(12)

	@syntax {

		@subid 392

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm pli maccess

	}

}

