
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


@title VPADAL

@id 342

@desc {

	Vector Pairwise Add and Accumulate Long adds adjacent pairs of elements of a vector, and accumulates the results into the elements of the destination vector. The vectors can be doubleword or quadword. The operand elements can be 8-bit, 16-bit, or 32-bit integers. The result elements are twice the length of the operand elements. Figure A8-2 shows an example of the operation of VPADAL. Dm + + Dd Figure A8-2 VPADAL doubleword operation for data type S16 Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 0 Vd(4) 0 1 1 0 op(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2607

		@assert {

			Q == 1
			size == 0
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.s8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2608

		@assert {

			Q == 1
			size == 1
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.s16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2609

		@assert {

			Q == 1
			size == 10
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.s32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2610

		@assert {

			Q == 1
			size == 0
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.u8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2611

		@assert {

			Q == 1
			size == 1
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.u16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2612

		@assert {

			Q == 1
			size == 10
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.u32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2613

		@assert {

			Q == 0
			size == 0
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.s8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2614

		@assert {

			Q == 0
			size == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.s16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2615

		@assert {

			Q == 0
			size == 10
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.s32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2616

		@assert {

			Q == 0
			size == 0
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.u8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2617

		@assert {

			Q == 0
			size == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.u16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2618

		@assert {

			Q == 0
			size == 10
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.u32 dwvec_D dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 0 Vd(4) 0 1 1 0 op(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2619

		@assert {

			Q == 1
			size == 0
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.s8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2620

		@assert {

			Q == 1
			size == 1
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.s16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2621

		@assert {

			Q == 1
			size == 10
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.s32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2622

		@assert {

			Q == 1
			size == 0
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.u8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2623

		@assert {

			Q == 1
			size == 1
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.u16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2624

		@assert {

			Q == 1
			size == 10
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vpadal.u32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2625

		@assert {

			Q == 0
			size == 0
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.s8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2626

		@assert {

			Q == 0
			size == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.s16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2627

		@assert {

			Q == 0
			size == 10
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.s32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2628

		@assert {

			Q == 0
			size == 0
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.u8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2629

		@assert {

			Q == 0
			size == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.u16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2630

		@assert {

			Q == 0
			size == 10
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpadal.u32 dwvec_D dwvec_M

	}

}

