
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


@title SWP, SWPB

@id 224

@desc {

	SWP (Swap) swaps a word between registers and memory. SWP loads a word from the memory address given by the value of register <Rn>. The value of register <Rt2> is then stored to the memory address given by the value of <Rn>, and the original loaded value is written to register <Rt>. If the same register is specified for <Rt> and <Rt2>, this instruction swaps the value of the register and the value at the memory address. SWPB (Swap Byte) swaps a byte between registers and memory. SWPB loads a byte from the memory address given by the value of register <Rn>. The value of the least significant byte of register <Rt2> is stored to the memory address given by <Rn>, the original loaded value is zero-extended to a 32-bit word, and the word is written to register <Rt>. If the same register is specified for <Rt> and <Rt2>, this instruction swaps the value of the least significant byte of the register and the byte value at the memory address, and clears the most significant three bytes of the register. For both instructions, the memory system ensures that no other memory access can occur to the memory location between the load access and the store access. Note • The SWP and SWPB instructions rely on the properties of the system beyond the processor to ensure that no stores from other observers can occur between the load access and the store access, and this might not be implemented for all regions of memory on some system implementations. In all cases, SWP and SWPB do ensure that no stores from the processor that executed the SWP or SWPB instruction can occur between the load access and the store access of the SWP or SWPB. • ARM deprecates the use of SWP and SWPB, and strongly recommends that new software uses: LDREX/STREX in preference to SWP — — LDREXB/STREXB in preference to SWPB. • If the translation table entries that relate to a memory location accessed by the SWP or SWPB instruction change, or are seen to change by the executing processor as a result of TLB eviction, this might mean that the translation table attributes, permissions or addresses for the load are different to those for the store. In this case, the architecture makes no guarantee that no memory access occur to these memory locations between the load and store. The Virtualization Extensions make the SWP and SWPB instructions OPTIONAL and deprecated: • If an implementation does not include the SWP and SWPB instructions, the ID_ISAR0.Swap_instrs and ID_ISAR4.SWP_frac fields are zero, see About the Instruction Set Attribute registers on page B7-1950. • In an implementation that includes SWP and SWPB, both instructions are UNDEFINED in Hyp mode.

}

@encoding (A1) {

	@word cond(4) 0 0 0 1 0 B(1) 0 0 Rn(4) Rt(4) 0 0 0 0 1 0 0 1 Rt2(4)

	@syntax {

		@subid 705

		@assert {

			B == 0

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm swp reg_T reg_T2 maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

	@syntax {

		@subid 706

		@assert {

			B == 1

		}

		@conv {

			reg_T = Register(Rt)
			reg_T2 = Register(Rt2)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm swpb reg_T reg_T2 maccess

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

