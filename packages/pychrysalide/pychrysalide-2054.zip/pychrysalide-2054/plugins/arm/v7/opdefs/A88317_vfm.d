
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


@title VFMA, VFMS

@id 309

@desc {

	Vector Fused Multiply Accumulate multiplies corresponding elements of two vectors, and accumulates the results into the elements of the destination vector. The instruction does not round the result of the multiply before the accumulation. Vector Fused Multiply Subtract negates the elements of one vector and multiplies them with the corresponding elements of another vector, adds the products to the corresponding elements of the destination vector, and places the results in the destination vector. The instruction does not round the result of the multiply before the addition. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 and Summary of access controls for Advanced SIMD functionality on page B1-1232 summarize these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 1 0 D(1) op(1) sz(1) Vn(4) Vd(4) 1 1 0 0 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 1301

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

		@asm vfma.f32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1302

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

		@asm vfms.f32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1303

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

		@asm vfma.f32 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1304

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

		@asm vfms.f32 dwvec_D dwvec_N dwvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 0 Vn(4) Vd(4) 1 0 1 sz(1) N(1) op(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1305

		@assert {

			sz == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vfma.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1306

		@assert {

			sz == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vfms.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1307

		@assert {

			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vfma.f32 swvec_D swvec_N swvec_M

	}

	@syntax {

		@subid 1308

		@assert {

			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vfms.f32 swvec_D swvec_N swvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 1 0 D(1) op(1) sz(1) Vn(4) Vd(4) 1 1 0 0 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 1309

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

		@asm vfma.f32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1310

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

		@asm vfms.f32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1311

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

		@asm vfma.f32 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1312

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

		@asm vfms.f32 dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 0 Vn(4) Vd(4) 1 0 1 sz(1) N(1) op(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1313

		@assert {

			sz == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vfma.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1314

		@assert {

			sz == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vfms.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1315

		@assert {

			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vfma.f32 swvec_D swvec_N swvec_M

	}

	@syntax {

		@subid 1316

		@assert {

			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vfms.f32 swvec_D swvec_N swvec_M

	}

}

