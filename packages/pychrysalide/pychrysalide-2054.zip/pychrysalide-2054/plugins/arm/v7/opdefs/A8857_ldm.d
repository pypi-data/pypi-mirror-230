
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


@title LDM/LDMIA/LDMFD (Thumb)

@id 52

@desc {

	Load Multiple Increment After (Load Multiple Full Descending) loads multiple registers from consecutive memory locations using an address from a base register. The consecutive memory locations start at this address, and the address just above the highest of those locations can optionally be written back to the base register. The registers loaded can include the PC, causing a branch to a loaded address. Related system instructions are LDM (User registers) on page B9-1986 and LDM (exception return) on page B9-1984.

}

@encoding (t1) {

	@half 1 1 0 0 1 Rn(3) register_list(8)

	@syntax {

		@subid 163

		@conv {

			reg_N = Register(Rn)
			wb_reg = UncheckedWrittenBackReg(reg_N)
			registers = RegList('00000000':register_list)

		}

		@asm ldm wb_reg registers

	}

	@hooks {

		fetch = apply_write_back_from_registers

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 0 0 0 1 0 W(1) 1 Rn(4) P(1) M(1) 0 register_list(13)

	@syntax {

		@subid 164

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			registers = RegList(P:M:'0':register_list)

		}

		@asm ldm.w wb_reg registers

	}

}

