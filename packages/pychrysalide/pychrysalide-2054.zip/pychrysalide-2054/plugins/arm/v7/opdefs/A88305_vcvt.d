
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


@title VCVT (between floating-point and integer, Advanced SIMD)

@id 300

@desc {

	This instruction converts each element in a vector from floating-point to integer, or from integer to floating-point, and places the results in a second vector. The vector elements must be 32-bit floating-point numbers, or 32-bit integers. Signed and unsigned integers are distinct. The floating-point to integer operation uses the Round towards Zero rounding mode. The integer to floating-point operation uses the Round to Nearest rounding mode. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 1 Vd(4) 0 1 1 op(2) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1221

		@assert {

			Q == 1
			op == 10
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcvt.s32.f32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1222

		@assert {

			Q == 1
			op == 11
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcvt.u32.f32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1223

		@assert {

			Q == 1
			op == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcvt.f32.s32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1224

		@assert {

			Q == 1
			op == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcvt.f32.u32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1225

		@assert {

			Q == 0
			op == 10
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.s32.f32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1226

		@assert {

			Q == 0
			op == 11
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.u32.f32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1227

		@assert {

			Q == 0
			op == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.f32.s32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1228

		@assert {

			Q == 0
			op == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.f32.u32 dwvec_D dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 1 Vd(4) 0 1 1 op(2) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1229

		@assert {

			Q == 1
			op == 10
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcvt.s32.f32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1230

		@assert {

			Q == 1
			op == 11
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcvt.u32.f32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1231

		@assert {

			Q == 1
			op == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcvt.f32.s32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1232

		@assert {

			Q == 1
			op == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcvt.f32.u32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1233

		@assert {

			Q == 0
			op == 10
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.s32.f32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1234

		@assert {

			Q == 0
			op == 11
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.u32.f32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1235

		@assert {

			Q == 0
			op == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.f32.s32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1236

		@assert {

			Q == 0
			op == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.f32.u32 dwvec_D dwvec_M

	}

}

