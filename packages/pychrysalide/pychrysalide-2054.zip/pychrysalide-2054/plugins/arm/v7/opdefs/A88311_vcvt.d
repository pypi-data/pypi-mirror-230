
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


@title VCVTB, VCVTT

@id 304

@desc {

	Vector Convert Bottom and Vector Convert Top do one of the following: • convert the half-precision value in the top or bottom half of a single-precision register to single-precision and write the result to a single-precision register • convert the value in a single-precision register to half-precision and write the result into the top or bottom half of a single-precision register, preserving the other half of the target register. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 summarizes these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 0 0 1 op(1) Vd(4) 1 0 1 0 T(1) 1 M(1) 0 Vm(4)

	@syntax {

		@subid 1269

		@assert {

			op == 0
			T == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtb.f32.f16 swvec_D swvec_M

	}

	@syntax {

		@subid 1270

		@assert {

			op == 0
			T == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtt.f32.f16 swvec_D swvec_M

	}

	@syntax {

		@subid 1271

		@assert {

			op == 1
			T == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtb.f16.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1272

		@assert {

			op == 1
			T == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtt.f16.f32 swvec_D swvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 0 0 1 op(1) Vd(4) 1 0 1 0 T(1) 1 M(1) 0 Vm(4)

	@syntax {

		@subid 1273

		@assert {

			op == 0
			T == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtb.f32.f16 swvec_D swvec_M

	}

	@syntax {

		@subid 1274

		@assert {

			op == 0
			T == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtt.f32.f16 swvec_D swvec_M

	}

	@syntax {

		@subid 1275

		@assert {

			op == 1
			T == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtb.f16.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 1276

		@assert {

			op == 1
			T == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vcvtt.f16.f32 swvec_D swvec_M

	}

}

