
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


@title VMOVL

@id 328

@desc {

	Vector Move Long takes each element in a doubleword vector, sign or zero-extends them to twice their original length, and places the results in a quadword vector. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) imm3(3) 0 0 0 Vd(4) 1 0 1 0 0 0 M(1) 1 Vm(4)

	@syntax {

		@subid 2389

		@assert {

			U == 0
			imm3 == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.s8 qwvec_D dwvec_M

	}

	@syntax {

		@subid 2390

		@assert {

			U == 0
			imm3 == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.s16 qwvec_D dwvec_M

	}

	@syntax {

		@subid 2391

		@assert {

			U == 0
			imm3 == 100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.s32 qwvec_D dwvec_M

	}

	@syntax {

		@subid 2392

		@assert {

			U == 1
			imm3 == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.u8 qwvec_D dwvec_M

	}

	@syntax {

		@subid 2393

		@assert {

			U == 1
			imm3 == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.u16 qwvec_D dwvec_M

	}

	@syntax {

		@subid 2394

		@assert {

			U == 1
			imm3 == 100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.u32 qwvec_D dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) imm3(3) 0 0 0 Vd(4) 1 0 1 0 0 0 M(1) 1 Vm(4)

	@syntax {

		@subid 2395

		@assert {

			U == 0
			imm3 == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.s8 qwvec_D dwvec_M

	}

	@syntax {

		@subid 2396

		@assert {

			U == 0
			imm3 == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.s16 qwvec_D dwvec_M

	}

	@syntax {

		@subid 2397

		@assert {

			U == 0
			imm3 == 100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.s32 qwvec_D dwvec_M

	}

	@syntax {

		@subid 2398

		@assert {

			U == 1
			imm3 == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.u8 qwvec_D dwvec_M

	}

	@syntax {

		@subid 2399

		@assert {

			U == 1
			imm3 == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.u16 qwvec_D dwvec_M

	}

	@syntax {

		@subid 2400

		@assert {

			U == 1
			imm3 == 100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vmovl.u32 qwvec_D dwvec_M

	}

}

