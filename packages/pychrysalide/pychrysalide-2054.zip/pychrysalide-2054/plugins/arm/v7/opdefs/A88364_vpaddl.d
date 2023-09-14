
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


@title VPADDL

@id 345

@desc {

	Vector Pairwise Add Long adds adjacent pairs of elements of two vectors, and places the results in the destination vector. The vectors can be doubleword or quadword. The operand elements can be 8-bit, 16-bit, or 32-bit integers. The result elements are twice the length of the operand elements. Figure A8-4 shows an example of the operation of VPADDL. Dm + + Dd Figure A8-4 VPADDL doubleword operation for data type S16 Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 0 Vd(4) 0 0 1 0 op(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2639

		@assert {

			Q == 1
			size == 0
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.s8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2640

		@assert {

			Q == 1
			size == 1
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.s16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2641

		@assert {

			Q == 1
			size == 10
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.s32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2642

		@assert {

			Q == 1
			size == 0
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.u8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2643

		@assert {

			Q == 1
			size == 1
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.u16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2644

		@assert {

			Q == 1
			size == 10
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.u32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2645

		@assert {

			Q == 0
			size == 0
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.s8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2646

		@assert {

			Q == 0
			size == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.s16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2647

		@assert {

			Q == 0
			size == 10
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.s32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2648

		@assert {

			Q == 0
			size == 0
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.u8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2649

		@assert {

			Q == 0
			size == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.u16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2650

		@assert {

			Q == 0
			size == 10
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.u32 dwvec_D dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 0 Vd(4) 0 0 1 0 op(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2651

		@assert {

			Q == 1
			size == 0
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.s8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2652

		@assert {

			Q == 1
			size == 1
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.s16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2653

		@assert {

			Q == 1
			size == 10
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.s32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2654

		@assert {

			Q == 1
			size == 0
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.u8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2655

		@assert {

			Q == 1
			size == 1
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.u16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2656

		@assert {

			Q == 1
			size == 10
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpaddl.u32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2657

		@assert {

			Q == 0
			size == 0
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.s8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2658

		@assert {

			Q == 0
			size == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.s16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2659

		@assert {

			Q == 0
			size == 10
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.s32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2660

		@assert {

			Q == 0
			size == 0
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.u8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2661

		@assert {

			Q == 0
			size == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.u16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2662

		@assert {

			Q == 0
			size == 10
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpaddl.u32 dwvec_D dwvec_M

	}

}

