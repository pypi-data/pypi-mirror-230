
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


@title PLD, PLDW (immediate)

@id 121

@desc {

	Preload Data signals the memory system that data memory accesses from a specified address are likely in the near future. The memory system can respond by taking actions that are expected to speed up the memory accesses when they do occur, such as pre-loading the cache line containing the specified address into the data cache. On an architecture variant that includes both the PLD and PLDW instructions, the PLD instruction signals that the likely memory access is a read, and the PLDW instruction signals that it is a write. The effect of a PLD or PLDW instruction is IMPLEMENTATION DEFINED. For more information, see Preloading caches on page A3-157 and Behavior of Preload Data (PLD, PLDW) and Preload Instruction (PLI) with caches on page B2-1269.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 0 1 0 W(1) 1 Rn(4) 1 1 1 1 imm12(12)

	@syntax {

		@subid 377

		@assert {

			W == 0

		}

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm pld maccess

	}

	@syntax {

		@subid 378

		@assert {

			W == 1

		}

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm pldw maccess

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 0 0 0 0 0 W(1) 1 Rn(4) 1 1 1 1 1 1 0 0 imm8(8)

	@syntax {

		@subid 379

		@assert {

			W == 0

		}

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm pld maccess

	}

	@syntax {

		@subid 380

		@assert {

			W == 1

		}

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm8, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm pldw maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 0 1 0 1 U(1) R(1) 0 1 Rn(4) 1 1 1 1 imm12(12)

	@syntax {

		@subid 381

		@assert {

			R == 1

		}

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm pld maccess

	}

	@syntax {

		@subid 382

		@assert {

			R == 0

		}

		@conv {

			reg_N = Register(Rn)
			imm32 = ZeroExtend(imm12, 32)
			maccess = MemAccessOffset(reg_N, imm32)

		}

		@asm pldw maccess

	}

}

