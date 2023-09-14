
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


@title VMLA, VMLAL, VMLS, VMLSL (integer)

@id 323

@desc {

	Vector Multiply Accumulate and Vector Multiply Subtract multiply corresponding elements in two vectors, and either add the products to, or subtract them from, the corresponding elements of the destination vector. Vector Multiply Accumulate Long and Vector Multiply Subtract Long do the same thing, but with destination vector elements that are twice as long as the elements that are multiplied. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 op(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 1 0 0 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2313

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

		@asm vmla.i8 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2314

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

		@asm vmla.i16 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2315

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

		@asm vmla.i32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2316

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

		@asm vmls.i8 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2317

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

		@asm vmls.i16 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2318

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

		@asm vmls.i32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2319

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

		@asm vmla.i8 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2320

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

		@asm vmla.i16 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2321

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

		@asm vmla.i32 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2322

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

		@asm vmls.i8 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2323

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

		@asm vmls.i16 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2324

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

		@asm vmls.i32 dwvec_D dwvec_N dwvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 1 0 op(1) 0 N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 2325

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

		@asm vmlal.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2326

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

		@asm vmlal.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2327

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

		@asm vmlal.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2328

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

		@asm vmlal.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2329

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

		@asm vmlal.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2330

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

		@asm vmlal.u32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2331

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

		@asm vmlsl.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2332

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

		@asm vmlsl.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2333

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

		@asm vmlsl.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2334

		@assert {

			op == 1
			U == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmlsl.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2335

		@assert {

			op == 1
			U == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmlsl.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2336

		@assert {

			op == 1
			U == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmlsl.u32 qwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 op(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 1 0 0 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2337

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

		@asm vmla.i8 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2338

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

		@asm vmla.i16 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2339

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

		@asm vmla.i32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2340

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

		@asm vmls.i8 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2341

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

		@asm vmls.i16 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2342

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

		@asm vmls.i32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2343

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

		@asm vmla.i8 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2344

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

		@asm vmla.i16 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2345

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

		@asm vmla.i32 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2346

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

		@asm vmls.i8 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2347

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

		@asm vmls.i16 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2348

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

		@asm vmls.i32 dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 1 0 op(1) 0 N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 2349

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

		@asm vmlal.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2350

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

		@asm vmlal.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2351

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

		@asm vmlal.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2352

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

		@asm vmlal.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2353

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

		@asm vmlal.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2354

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

		@asm vmlal.u32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2355

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

		@asm vmlsl.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2356

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

		@asm vmlsl.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2357

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

		@asm vmlsl.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2358

		@assert {

			op == 1
			U == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmlsl.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2359

		@assert {

			op == 1
			U == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmlsl.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2360

		@assert {

			op == 1
			U == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmlsl.u32 qwvec_D dwvec_N dwvec_M

	}

}

