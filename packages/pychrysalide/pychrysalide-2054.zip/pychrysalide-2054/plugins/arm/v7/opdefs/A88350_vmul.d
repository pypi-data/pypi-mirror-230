
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


@title VMUL, VMULL (integer and polynomial)

@id 332

@desc {

	Vector Multiply multiplies corresponding elements in two vectors. Vector Multiply Long does the same thing, but with destination vector elements that are twice as long as the elements that are multiplied. For information about multiplying polynomials see Polynomial arithmetic over {0, 1} on page A2-93. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 op(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 1 0 0 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2411

		@assert {

			Q == 1
			op == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.i8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2412

		@assert {

			Q == 1
			op == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.i16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2413

		@assert {

			Q == 1
			op == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.i32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2414

		@assert {

			Q == 1
			op == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.p8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2415

		@assert {

			Q == 1
			op == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.p16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2416

		@assert {

			Q == 1
			op == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.p32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2417

		@assert {

			Q == 0
			op == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.i8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2418

		@assert {

			Q == 0
			op == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.i16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2419

		@assert {

			Q == 0
			op == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.i32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2420

		@assert {

			Q == 0
			op == 1
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.p8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2421

		@assert {

			Q == 0
			op == 1
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.p16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2422

		@assert {

			Q == 0
			op == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.p32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 1 1 op(1) 0 N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 2423

		@assert {

			op == 0
			U == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2424

		@assert {

			op == 0
			U == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2425

		@assert {

			op == 0
			U == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2426

		@assert {

			op == 0
			U == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2427

		@assert {

			op == 0
			U == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2428

		@assert {

			op == 0
			U == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.u32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2429

		@assert {

			op == 1
			U == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.p8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2430

		@assert {

			op == 1
			U == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.p16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2431

		@assert {

			op == 1
			U == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.p32 qwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 op(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 1 0 0 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2432

		@assert {

			Q == 1
			op == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.i8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2433

		@assert {

			Q == 1
			op == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.i16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2434

		@assert {

			Q == 1
			op == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.i32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2435

		@assert {

			Q == 1
			op == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.p8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2436

		@assert {

			Q == 1
			op == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.p16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2437

		@assert {

			Q == 1
			op == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmul.p32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2438

		@assert {

			Q == 0
			op == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.i8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2439

		@assert {

			Q == 0
			op == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.i16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2440

		@assert {

			Q == 0
			op == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.i32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2441

		@assert {

			Q == 0
			op == 1
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.p8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2442

		@assert {

			Q == 0
			op == 1
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.p16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2443

		@assert {

			Q == 0
			op == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmul.p32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 1 1 op(1) 0 N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 2444

		@assert {

			op == 0
			U == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2445

		@assert {

			op == 0
			U == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2446

		@assert {

			op == 0
			U == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2447

		@assert {

			op == 0
			U == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2448

		@assert {

			op == 0
			U == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2449

		@assert {

			op == 0
			U == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.u32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2450

		@assert {

			op == 1
			U == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.p8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2451

		@assert {

			op == 1
			U == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.p16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2452

		@assert {

			op == 1
			U == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmull.p32 qwvec_D dwvec_N dwvec_M

	}

}

