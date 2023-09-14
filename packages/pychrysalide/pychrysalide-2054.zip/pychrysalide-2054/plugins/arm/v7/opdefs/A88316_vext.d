
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


@title VEXT

@id 308

@desc {

	Vector Extract extracts elements from the bottom end of the second operand vector and the top end of the first, concatenates them and places the result in the destination vector. See Figure A8-1 for an example. The elements of the vectors are treated as being 8-bit fields. There is no distinction between data types. 7 6 5 4 3 2 1 0 7 6 5 4 3 2 1 0 Vm Vn Vd Figure A8-1 VEXT doubleword operation for imm = 3 Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 1 1 D(1) 1 1 Vn(4) Vd(4) imm4(4) N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1297

		@assert {

			Q == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)
			imm = Multiplication(8, imm4)

		}

		@asm vext.8 ?qwvec_D qwvec_N qwvec_M imm

	}

	@syntax {

		@subid 1298

		@assert {

			Q == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)
			imm = Multiplication(8, imm4)

		}

		@asm vext.8 ?dwvec_D dwvec_N dwvec_M imm

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 1 1 D(1) 1 1 Vn(4) Vd(4) imm4(4) N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1299

		@assert {

			Q == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)
			imm = Multiplication(8, imm4)

		}

		@asm vext.8 ?qwvec_D qwvec_N qwvec_M imm

	}

	@syntax {

		@subid 1300

		@assert {

			Q == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)
			imm = Multiplication(8, imm4)

		}

		@asm vext.8 ?dwvec_D dwvec_N dwvec_M imm

	}

}

