
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


@title VBIF, VBIT, VBSL

@id 285

@desc {

	VBIF (Vector Bitwise Insert if False), VBIT (Vector Bitwise Insert if True), and VBSL (Vector Bitwise Select) perform bitwise selection under the control of a mask, and place the results in the destination register. The registers can be either quadword or doubleword, and must all be the same size. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 0 D(1) op(2) Vn(4) Vd(4) 0 0 0 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 1013

		@assert {

			Q == 1
			op == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vbif ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1014

		@assert {

			Q == 1
			op == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vbit ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1015

		@assert {

			Q == 1
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vbsl ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1016

		@assert {

			Q == 0
			op == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vbif ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1017

		@assert {

			Q == 0
			op == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vbit ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1018

		@assert {

			Q == 0
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vbsl ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 0 D(1) op(2) Vn(4) Vd(4) 0 0 0 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 1019

		@assert {

			Q == 1
			op == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vbif ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1020

		@assert {

			Q == 1
			op == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vbit ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1021

		@assert {

			Q == 1
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vbsl ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1022

		@assert {

			Q == 0
			op == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vbif ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1023

		@assert {

			Q == 0
			op == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vbit ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1024

		@assert {

			Q == 0
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vbsl ?dwvec_D dwvec_N dwvec_M

	}

}

