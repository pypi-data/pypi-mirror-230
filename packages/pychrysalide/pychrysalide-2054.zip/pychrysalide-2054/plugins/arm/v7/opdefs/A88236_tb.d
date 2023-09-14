
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


@title TBB, TBH

@id 231

@desc {

	Table Branch Byte causes a PC-relative forward branch using a table of single byte offsets. A base register provides a pointer to the table, and a second register supplies an index into the table. The branch length is twice the value of the byte returned from the table. Table Branch Halfword causes a PC-relative forward branch using a table of single halfword offsets. A base register provides a pointer to the table, and a second register supplies an index into the table. The branch length is twice the value of the halfword returned from the table.

}

@encoding (T1) {

	@word 1 1 1 0 1 0 0 0 1 1 0 1 Rn(4) 1 1 1 1 0 0 0 0 0 0 0 H(1) Rm(4)

	@syntax {

		@subid 721

		@assert {

			H == 0

		}

		@conv {

			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessOffset(reg_N, reg_M)

		}

		@asm tbb maccess

	}

	@syntax {

		@subid 722

		@assert {

			H == 1

		}

		@conv {

			reg_N = Register(Rn)
			reg_M = Register(Rm)
			fixed_shift = BuildFixedShift(SRType_LSL, 1)
			maccess = MemAccessOffsetExtended(reg_N, reg_M, fixed_shift)

		}

		@asm tbh maccess

	}

}

