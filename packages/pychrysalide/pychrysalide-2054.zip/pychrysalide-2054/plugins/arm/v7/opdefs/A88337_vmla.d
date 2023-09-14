
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


@title VMLA, VMLS (floating-point)

@id 324

@desc {

	Vector Multiply Accumulate multiplies corresponding elements in two vectors, and accumulates the results into the elements of the destination vector. Vector Multiply Subtract multiplies corresponding elements in two vectors, subtracts the products from corresponding elements of the destination vector, and places the results in the destination vector. Note ARM recommends that software does not use the VMLS instruction in the Round towards Plus Infinity and Round towards Minus Infinity rounding modes, because the rounding of the product and of the sum can change the result of the instruction in opposite directions, defeating the purpose of these rounding modes. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 and Summary of access controls for Advanced SIMD functionality on page B1-1232 summarize these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 1 0 D(1) op(1) sz(1) Vn(4) Vd(4) 1 1 0 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2361

		@assert {

			Q == 1
			sz == 0
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmla.f32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2362

		@assert {

			Q == 1
			sz == 0
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmls.f32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2363

		@assert {

			Q == 0
			sz == 0
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmla.f32 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2364

		@assert {

			Q == 0
			sz == 0
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmls.f32 dwvec_D dwvec_N dwvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 1 1 0 0 D(1) 0 0 Vn(4) Vd(4) 1 0 1 sz(1) N(1) op(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2365

		@assert {

			sz == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmla.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2366

		@assert {

			sz == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmls.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2367

		@assert {

			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vmla.f32 swvec_D swvec_N swvec_M

	}

	@syntax {

		@subid 2368

		@assert {

			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vmls.f32 swvec_D swvec_N swvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 1 0 D(1) op(1) sz(1) Vn(4) Vd(4) 1 1 0 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 2369

		@assert {

			Q == 1
			sz == 0
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmla.f32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2370

		@assert {

			Q == 1
			sz == 0
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmls.f32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2371

		@assert {

			Q == 0
			sz == 0
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmla.f32 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2372

		@assert {

			Q == 0
			sz == 0
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmls.f32 dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 0 1 1 1 0 0 D(1) 0 0 Vn(4) Vd(4) 1 0 1 sz(1) N(1) op(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2373

		@assert {

			sz == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmla.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2374

		@assert {

			sz == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmls.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2375

		@assert {

			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vmla.f32 swvec_D swvec_N swvec_M

	}

	@syntax {

		@subid 2376

		@assert {

			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vmls.f32 swvec_D swvec_N swvec_M

	}

}

