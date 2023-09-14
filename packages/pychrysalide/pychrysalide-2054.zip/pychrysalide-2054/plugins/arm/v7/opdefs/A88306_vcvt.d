
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


@title VCVT, VCVTR (between floating-point and integer, Floating-point)

@id 301

@desc {

	These instructions convert a value in a register from floating-point to a 32-bit integer, or from a 32-bit integer to floating-point, and place the result in a second register. The floating-point to integer operation normally uses the Round towards Zero rounding mode, but can optionally use the rounding mode specified by the FPSCR. The integer to floating-point operation uses the rounding mode specified by the FPSCR. VCVT (between floating-point and fixed-point, Floating-point) on page A8-874 describes conversions between floating-point and 16-bit integers. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 summarizes these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 1 opc2(3) Vd(4) 1 0 1 sz(1) op(1) 1 M(1) 0 Vm(4)

	@syntax {

		@subid 1237

		@assert {

			opc2 == 101
			sz == 1
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvtr.s32.f64 swvec_D dwvec_M

	}

	@syntax {

		@subid 1238

		@assert {

			opc2 == 101
			sz == 1
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.s32.f64 swvec_D dwvec_M

	}

	@syntax {

		@subid 1239

		@assert {

			opc2 == 101
			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtr.s32.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1240

		@assert {

			opc2 == 101
			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvt.s32.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1241

		@assert {

			opc2 == 100
			sz == 1
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvtr.u32.f64 swvec_D dwvec_M

	}

	@syntax {

		@subid 1242

		@assert {

			opc2 == 100
			sz == 1
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.u32.f64 swvec_D dwvec_M

	}

	@syntax {

		@subid 1243

		@assert {

			opc2 == 100
			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtr.u32.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1244

		@assert {

			opc2 == 100
			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvt.u32.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1245

		@assert {

			opc2 == 000
			sz == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(Vd:D)
			swvec_M = SingleWordVector(M:Vm)

		}

		@asm vcvt.f64.s32 dwvec_D swvec_M

	}

	@syntax {

		@subid 1246

		@assert {

			opc2 == 000
			sz == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(Vd:D)
			swvec_M = SingleWordVector(M:Vm)

		}

		@asm vcvt.f64.u32 dwvec_D swvec_M

	}

	@syntax {

		@subid 1247

		@assert {

			opc2 == 000
			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvt.f32.s32 swvec_D swvec_M

	}

	@syntax {

		@subid 1248

		@assert {

			opc2 == 000
			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvt.f32.u32 swvec_D swvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 1 opc2(3) Vd(4) 1 0 1 sz(1) op(1) 1 M(1) 0 Vm(4)

	@syntax {

		@subid 1249

		@assert {

			opc2 == 101
			sz == 1
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvtr.s32.f64 swvec_D dwvec_M

	}

	@syntax {

		@subid 1250

		@assert {

			opc2 == 101
			sz == 1
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.s32.f64 swvec_D dwvec_M

	}

	@syntax {

		@subid 1251

		@assert {

			opc2 == 101
			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtr.s32.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1252

		@assert {

			opc2 == 101
			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvt.s32.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1253

		@assert {

			opc2 == 100
			sz == 1
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvtr.u32.f64 swvec_D dwvec_M

	}

	@syntax {

		@subid 1254

		@assert {

			opc2 == 100
			sz == 1
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcvt.u32.f64 swvec_D dwvec_M

	}

	@syntax {

		@subid 1255

		@assert {

			opc2 == 100
			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtr.u32.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1256

		@assert {

			opc2 == 100
			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvt.u32.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1257

		@assert {

			opc2 == 000
			sz == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(Vd:D)
			swvec_M = SingleWordVector(M:Vm)

		}

		@asm vcvt.f64.s32 dwvec_D swvec_M

	}

	@syntax {

		@subid 1258

		@assert {

			opc2 == 000
			sz == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(Vd:D)
			swvec_M = SingleWordVector(M:Vm)

		}

		@asm vcvt.f64.u32 dwvec_D swvec_M

	}

	@syntax {

		@subid 1259

		@assert {

			opc2 == 000
			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvt.f32.s32 swvec_D swvec_M

	}

	@syntax {

		@subid 1260

		@assert {

			opc2 == 000
			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvt.f32.u32 swvec_D swvec_M

	}

}

