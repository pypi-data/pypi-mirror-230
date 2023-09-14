
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


@title VPADD (integer)

@id 343

@desc {

	Vector Pairwise Add (integer) adds adjacent pairs of elements of two vectors, and places the results in the destination vector. The operands and result are doubleword vectors. The operand and result elements must all be the same type, and can be 8-bit, 16-bit, or 32-bit integers. There is no distinction between signed and unsigned integers. Figure A8-3 shows an example of the operation of VPADD. Dm Dn + + + + Dd Figure A8-3 VPADD operation for data type I16 Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 1 0 1 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2631

		@assert {

			Q == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadd.i8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2632

		@assert {

			Q == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadd.i16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2633

		@assert {

			Q == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadd.i32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 1 0 1 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2634

		@assert {

			Q == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadd.i8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2635

		@assert {

			Q == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadd.i16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2636

		@assert {

			Q == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadd.i32 ?dwvec_D dwvec_N dwvec_M

	}

}

