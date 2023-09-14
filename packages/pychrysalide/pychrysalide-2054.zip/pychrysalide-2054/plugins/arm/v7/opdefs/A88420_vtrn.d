
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


@title VTRN

@id 380

@desc {

	Vector Transpose treats the elements of its operand vectors as elements of 2 × 2 matrices, and transposes the matrices. The elements of the vectors can be 8-bit, 16-bit, or 32-bit. There is no distinction between data types. Figure A8-7 shows the operation of doubleword VTRN. Quadword VTRN performs the same operation as doubleword VTRN twice, once on the upper halves of the quadword vectors, and once on the lower halves VTRN.32 VTRN.16 VTRN.8 1 0 3 2 1 0 7 6 5 4 3 2 1 0 Dd Dd Dd Dm Dm Dm Figure A8-7 VTRN doubleword operation Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 0 Vd(4) 0 0 0 0 1 Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 3723

		@assert {

			Q == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vtrn.8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 3724

		@assert {

			Q == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vtrn.16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 3725

		@assert {

			Q == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vtrn.32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 3726

		@assert {

			Q == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtrn.8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 3727

		@assert {

			Q == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtrn.16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 3728

		@assert {

			Q == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtrn.32 dwvec_D dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 0 Vd(4) 0 0 0 0 1 Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 3729

		@assert {

			Q == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vtrn.8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 3730

		@assert {

			Q == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vtrn.16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 3731

		@assert {

			Q == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vtrn.32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 3732

		@assert {

			Q == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtrn.8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 3733

		@assert {

			Q == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtrn.16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 3734

		@assert {

			Q == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtrn.32 dwvec_D dwvec_M

	}

}

