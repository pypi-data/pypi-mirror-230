
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


@title VCGT (immediate #0)

@id 291

@desc {

	VCGT #0 (Vector Compare Greater Than Zero) take each element in a vector, and compares it with zero. If it is greater than zero, the corresponding element in the destination vector is set to all ones. Otherwise, it is set to all zeros. The operand vector elements can be any one of: • 8-bit, 16-bit, or 32-bit signed integers • 32-bit floating-point numbers. The result vector elements are fields the same size as the operand vector elements. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 1 Vd(4) 0 F(1) 0 0 0 Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1129

		@assert {

			Q == 1
			size == 0
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s8 ?qwvec_D qwvec_M zero

	}

	@syntax {

		@subid 1130

		@assert {

			Q == 1
			size == 1
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s16 ?qwvec_D qwvec_M zero

	}

	@syntax {

		@subid 1131

		@assert {

			Q == 1
			size == 10
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s32 ?qwvec_D qwvec_M zero

	}

	@syntax {

		@subid 1132

		@assert {

			Q == 1
			size == 10
			F == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.f32 ?qwvec_D qwvec_M zero

	}

	@syntax {

		@subid 1133

		@assert {

			Q == 0
			size == 0
			F == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s8 ?dwvec_D dwvec_M zero

	}

	@syntax {

		@subid 1134

		@assert {

			Q == 0
			size == 1
			F == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s16 ?dwvec_D dwvec_M zero

	}

	@syntax {

		@subid 1135

		@assert {

			Q == 0
			size == 10
			F == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s32 ?dwvec_D dwvec_M zero

	}

	@syntax {

		@subid 1136

		@assert {

			Q == 0
			size == 10
			F == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.f32 ?dwvec_D dwvec_M zero

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 1 Vd(4) 0 F(1) 0 0 0 Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1137

		@assert {

			Q == 1
			size == 0
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s8 ?qwvec_D qwvec_M zero

	}

	@syntax {

		@subid 1138

		@assert {

			Q == 1
			size == 1
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s16 ?qwvec_D qwvec_M zero

	}

	@syntax {

		@subid 1139

		@assert {

			Q == 1
			size == 10
			F == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s32 ?qwvec_D qwvec_M zero

	}

	@syntax {

		@subid 1140

		@assert {

			Q == 1
			size == 10
			F == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.f32 ?qwvec_D qwvec_M zero

	}

	@syntax {

		@subid 1141

		@assert {

			Q == 0
			size == 0
			F == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s8 ?dwvec_D dwvec_M zero

	}

	@syntax {

		@subid 1142

		@assert {

			Q == 0
			size == 1
			F == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s16 ?dwvec_D dwvec_M zero

	}

	@syntax {

		@subid 1143

		@assert {

			Q == 0
			size == 10
			F == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.s32 ?dwvec_D dwvec_M zero

	}

	@syntax {

		@subid 1144

		@assert {

			Q == 0
			size == 10
			F == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)
			zero = Zeros(8)

		}

		@asm vcgt.f32 ?dwvec_D dwvec_M zero

	}

}

