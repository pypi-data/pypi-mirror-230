
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


@title VMOVN

@id 329

@desc {

	Vector Move and Narrow copies the least significant half of each element of a quadword vector into the corresponding elements of a doubleword vector. The operand vector elements can be any one of 16-bit, 32-bit, or 64-bit integers. There is no distinction between signed and unsigned integers. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 0 Vd(4) 0 0 1 0 0 0 M(1) 0 Vm(4)

	@syntax {

		@subid 2401

		@assert {

			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmovn.i16 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2402

		@assert {

			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmovn.i32 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2403

		@assert {

			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmovn.i64 dwvec_D qwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 0 Vd(4) 0 0 1 0 0 0 M(1) 0 Vm(4)

	@syntax {

		@subid 2404

		@assert {

			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmovn.i16 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2405

		@assert {

			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmovn.i32 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2406

		@assert {

			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vmovn.i64 dwvec_D qwvec_M

	}

}

