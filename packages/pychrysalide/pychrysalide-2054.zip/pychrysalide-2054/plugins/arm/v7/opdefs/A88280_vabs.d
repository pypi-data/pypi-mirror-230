
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


@title VABS

@id 275

@desc {

	Vector Absolute takes the absolute value of each element in a vector, and places the results in a second vector. The floating-point version only clears the sign bit. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 and Summary of access controls for Advanced SIMD functionality on page B1-1232 summarize these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction that is not also available as a VFP instruction, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 1 Vd(4) 0 F(1) 1 1 0 Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 883

		@assert {

			size == 0
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vabs.s8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 884

		@assert {

			size == 1
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vabs.s16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 885

		@assert {

			size == 10
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vabs.s32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 886

		@assert {

			size == 10
			F == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vabs.f32 qwvec_D qwvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 0 0 0 0 Vd(4) 1 0 1 sz(1) 1 1 M(1) 0 Vm(4)

	@syntax {

		@subid 887

		@assert {

			sz == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vabs.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 888

		@assert {

			sz == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabs.f64 dwvec_D dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 1 Vd(4) 0 F(1) 1 1 0 Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 889

		@assert {

			size == 0
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vabs.s8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 890

		@assert {

			size == 1
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vabs.s16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 891

		@assert {

			size == 10
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vabs.s32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 892

		@assert {

			size == 10
			F == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vabs.f32 qwvec_D qwvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 1 1 0 0 0 0 Vd(4) 1 0 1 sz(1) 1 1 M(1) 0 Vm(4)

	@syntax {

		@subid 893

		@assert {

			sz == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vabs.f32 swvec_D swvec_M

	}

	@syntax {

		@subid 894

		@assert {

			sz == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabs.f64 dwvec_D dwvec_M

	}

}

