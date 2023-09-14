
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


@title VCGT (register)

@id 290

@desc {

	VCGT (Vector Compare Greater Than) takes each element in a vector, and compares it with the corresponding element of a second vector. If the first is greater than the second, the corresponding element in the destination vector is set to all ones. Otherwise, it is set to all zeros. The operand vector elements can be any one of: • 8-bit, 16-bit, or 32-bit signed integers • 8-bit, 16-bit, or 32-bit unsigned integers • 32-bit floating-point numbers. The result vector elements are fields the same size as the operand vector elements. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 0 1 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1101

		@assert {

			Q == 1
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1102

		@assert {

			Q == 1
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1103

		@assert {

			Q == 1
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1104

		@assert {

			Q == 1
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1105

		@assert {

			Q == 1
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1106

		@assert {

			Q == 1
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1107

		@assert {

			Q == 0
			size == 0
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1108

		@assert {

			Q == 0
			size == 1
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1109

		@assert {

			Q == 0
			size == 10
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1110

		@assert {

			Q == 0
			size == 0
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1111

		@assert {

			Q == 0
			size == 1
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1112

		@assert {

			Q == 0
			size == 10
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 1 1 1 1 1 0 D(1) 1 sz(1) Vn(4) Vd(4) 1 1 1 0 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1113

		@assert {

			Q == 1
			sz == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.f32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1114

		@assert {

			Q == 0
			sz == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.f32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 0 1 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1115

		@assert {

			Q == 1
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1116

		@assert {

			Q == 1
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1117

		@assert {

			Q == 1
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1118

		@assert {

			Q == 1
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1119

		@assert {

			Q == 1
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1120

		@assert {

			Q == 1
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1121

		@assert {

			Q == 0
			size == 0
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1122

		@assert {

			Q == 0
			size == 1
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1123

		@assert {

			Q == 0
			size == 10
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1124

		@assert {

			Q == 0
			size == 0
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1125

		@assert {

			Q == 0
			size == 1
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1126

		@assert {

			Q == 0
			size == 10
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 1 1 1 1 1 0 D(1) 1 sz(1) Vn(4) Vd(4) 1 1 1 0 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1127

		@assert {

			Q == 1
			sz == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vcgt.f32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1128

		@assert {

			Q == 0
			sz == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vcgt.f32 ?dwvec_D dwvec_N dwvec_M

	}

}

