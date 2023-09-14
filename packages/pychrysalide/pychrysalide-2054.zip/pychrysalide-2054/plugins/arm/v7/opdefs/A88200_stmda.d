
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


@title STMDA (STMED)

@id 195

@desc {

	Store Multiple Decrement After (Store Multiple Empty Descending) stores multiple registers to consecutive memory locations using an address from a base register. The consecutive memory locations end at this address, and the address just below the lowest of those locations can optionally be written back to the base register. For details of related system instructions see STM (User registers) on page B9-2006.

}

@encoding (A1) {

	@word cond(4) 1 0 0 0 0 0 W(1) 0 Rn(4) register_list(16)

	@syntax {

		@subid 609

		@conv {

			reg_N = Register(Rn)
			wb_reg = WrittenBackReg(reg_N, W)
			registers = RegList(register_list)

		}

		@asm stmda wb_reg registers

		@rules {

			check g_arm_instruction_set_cond(cond)

		}

	}

}

