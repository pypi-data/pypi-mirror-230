
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


@title VADDL, VADDW

@id 280

@desc {

	VADDL (Vector Add Long) adds corresponding elements in two doubleword vectors, and places the results in a quadword vector. Before adding, it sign-extends or zero-extends the elements of both operands. VADDW (Vector Add Wide) adds corresponding elements in one quadword and one doubleword vector, and places the results in a quadword vector. Before adding, it sign-extends or zero-extends the elements of the doubleword operand. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 0 0 0 op(1) N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 925

		@assert {

			op == 0
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 926

		@assert {

			op == 0
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 927

		@assert {

			op == 0
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 928

		@assert {

			op == 0
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 929

		@assert {

			op == 0
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 930

		@assert {

			op == 0
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.u32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 931

		@assert {

			op == 1
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.s8 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 932

		@assert {

			op == 1
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.s16 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 933

		@assert {

			op == 1
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.s32 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 934

		@assert {

			op == 1
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.u8 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 935

		@assert {

			op == 1
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.u16 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 936

		@assert {

			op == 1
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.u32 ?qwvec_D qwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 0 0 0 op(1) N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 937

		@assert {

			op == 0
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 938

		@assert {

			op == 0
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 939

		@assert {

			op == 0
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 940

		@assert {

			op == 0
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 941

		@assert {

			op == 0
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 942

		@assert {

			op == 0
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddl.u32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 943

		@assert {

			op == 1
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.s8 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 944

		@assert {

			op == 1
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.s16 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 945

		@assert {

			op == 1
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.s32 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 946

		@assert {

			op == 1
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.u8 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 947

		@assert {

			op == 1
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.u16 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 948

		@assert {

			op == 1
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vaddw.u32 ?qwvec_D qwvec_N dwvec_M

	}

}

