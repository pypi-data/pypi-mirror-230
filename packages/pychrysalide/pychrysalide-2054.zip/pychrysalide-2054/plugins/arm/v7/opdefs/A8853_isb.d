
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


@title ISB

@id 48

@desc {

	Instruction Synchronization Barrier flushes the pipeline in the processor, so that all instructions following the ISB are fetched from cache or memory, after the instruction has been completed. It ensures that the effects of context changing operations executed before the ISB instruction are visible to the instructions fetched after the ISB. Context changing operations include changing the Address Space Identifier (ASID), TLB maintenance operations, branch predictor maintenance operations, and all changes to the CP15 registers. In addition, any branches that appear in program order after the ISB instruction are written into the branch prediction logic with the context that is visible after the ISB instruction. This is needed to ensure correct execution of the instruction stream.

}

@encoding (T1) {

	@word 1 1 1 1 0 0 1 1 1 0 1 1 1 1 1 1 1 0 0 0 1 1 1 1 0 1 1 0 option(4)

	@syntax {

		@subid 138

		@conv {

			direct_option = UInt(option)

		}

		@asm isb ?direct_option

	}

}

@encoding (A1) {

	@word 1 1 1 1 0 1 0 1 0 1 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 1 1 0 option(4)

	@syntax {

		@subid 139

		@conv {

			direct_option = UInt(option)

		}

		@asm isb ?direct_option

	}

}

