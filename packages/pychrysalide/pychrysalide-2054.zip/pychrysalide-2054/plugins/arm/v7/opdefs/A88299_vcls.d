
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


@title VCLS

@id 294

@desc {

	Vector Count Leading Sign Bits counts the number of consecutive bits following the topmost bit, that are the same as the topmost bit, in each element in a vector, and places the results in a second vector. The count does not include the topmost bit itself. The operand vector elements can be any one of 8-bit, 16-bit, or 32-bit signed integers. The result vector elements are the same data type as the operand vector elements. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 0 Vd(4) 0 1 0 0 0 Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1161

		@assert {

			Q == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcls.s8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1162

		@assert {

			Q == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcls.s16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1163

		@assert {

			Q == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcls.s32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1164

		@assert {

			Q == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcls.s8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1165

		@assert {

			Q == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcls.s16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1166

		@assert {

			Q == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcls.s32 dwvec_D dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 0 Vd(4) 0 1 0 0 0 Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1167

		@assert {

			Q == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcls.s8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1168

		@assert {

			Q == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcls.s16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1169

		@assert {

			Q == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcls.s32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 1170

		@assert {

			Q == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcls.s8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1171

		@assert {

			Q == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcls.s16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 1172

		@assert {

			Q == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcls.s32 dwvec_D dwvec_M

	}

}

