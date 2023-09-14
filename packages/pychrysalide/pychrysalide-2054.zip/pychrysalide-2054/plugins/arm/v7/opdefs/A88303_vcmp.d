
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


@title VCMP, VCMPE

@id 298

@desc {

	This instruction compares two floating-point registers, or one floating-point register and zero. It writes the result to the FPSCR flags. These are normally transferred to the ARM flags by a subsequent VMRS instruction. It can optionally raise an Invalid Operation exception if either operand is any type of NaN. It always raises an Invalid Operation exception if either operand is a signaling NaN. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 summarizes these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 0 1 0 0 Vd(4) 1 0 1 sz(1) E(1) 1 M(1) 0 Vm(4)

	@syntax {

		@subid 1201

		@assert {

			sz == 1
			E == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcmp.f64 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1202

		@assert {

			sz == 1
			E == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcmpe.f64 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1203

		@assert {

			sz == 0
			E == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcmp.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1204

		@assert {

			sz == 0
			E == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcmpe.f32 swvec_D swvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 0 1 0 1 Vd(4) 1 0 1 sz(1) E(1) 1 0 0 0 0 0 0

	@syntax {

		@subid 1205

		@assert {

			sz == 1
			E == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			zero = Zeros(8)

		}

		@asm vcmp.f64 dwvec_D zero

	}

	@syntax {

		@subid 1206

		@assert {

			sz == 1
			E == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			zero = Zeros(8)

		}

		@asm vcmpe.f64 dwvec_D zero

	}

	@syntax {

		@subid 1207

		@assert {

			sz == 0
			E == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			zero = Zeros(8)

		}

		@asm vcmp.f32 swvec_D zero

	}

	@syntax {

		@subid 1208

		@assert {

			sz == 0
			E == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			zero = Zeros(8)

		}

		@asm vcmpe.f32 swvec_D zero

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 0 1 0 0 Vd(4) 1 0 1 sz(1) E(1) 1 M(1) 0 Vm(4)

	@syntax {

		@subid 1209

		@assert {

			sz == 1
			E == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcmp.f64 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1210

		@assert {

			sz == 1
			E == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcmpe.f64 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1211

		@assert {

			sz == 0
			E == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcmp.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1212

		@assert {

			sz == 0
			E == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcmpe.f32 swvec_D swvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 0 1 0 1 Vd(4) 1 0 1 sz(1) E(1) 1 0 0 0 0 0 0

	@syntax {

		@subid 1213

		@assert {

			sz == 1
			E == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			zero = Zeros(8)

		}

		@asm vcmp.f64 dwvec_D zero

	}

	@syntax {

		@subid 1214

		@assert {

			sz == 1
			E == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			zero = Zeros(8)

		}

		@asm vcmpe.f64 dwvec_D zero

	}

	@syntax {

		@subid 1215

		@assert {

			sz == 0
			E == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			zero = Zeros(8)

		}

		@asm vcmp.f32 swvec_D zero

	}

	@syntax {

		@subid 1216

		@assert {

			sz == 0
			E == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			zero = Zeros(8)

		}

		@asm vcmpe.f32 swvec_D zero

	}

}

