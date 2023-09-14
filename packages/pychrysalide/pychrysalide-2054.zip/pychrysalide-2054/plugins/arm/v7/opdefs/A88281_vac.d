
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


@title VACGE, VACGT, VACLE, VACLT

@id 276

@desc {

	VACGE (Vector Absolute Compare Greater Than or Equal) and VACGT (Vector Absolute Compare Greater Than) take the absolute value of each element in a vector, and compare it with the absolute value of the corresponding element of a second vector. If the condition is true, the corresponding element in the destination vector is set to all ones. Otherwise, it is set to all zeros. VACLE (Vector Absolute Compare Less Than or Equal) is a pseudo-instruction, equivalent to a VACGE instruction with the operands reversed. Disassembly produces the VACGE instruction. VACLT (Vector Absolute Compare Less Than) is a pseudo-instruction, equivalent to a VACGT instruction with the operands reversed. Disassembly produces the VACGT instruction. The operands and result can be quadword or doubleword vectors. They must all be the same size. The operand vector elements must be 32-bit floating-point numbers. The result vector elements are 32-bit fields. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction that is not also available as a VFP instruction, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 0 D(1) op(1) sz(1) Vn(4) Vd(4) 1 1 1 0 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 895

		@assert {

			Q == 1
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vacge.f32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 896

		@assert {

			Q == 1
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vacgt.f32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 897

		@assert {

			Q == 0
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vacge.f32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 898

		@assert {

			Q == 0
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vacgt.f32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 0 D(1) op(1) sz(1) Vn(4) Vd(4) 1 1 1 0 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 899

		@assert {

			Q == 1
			op == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vacge.f32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 900

		@assert {

			Q == 1
			op == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vacgt.f32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 901

		@assert {

			Q == 0
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vacge.f32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 902

		@assert {

			Q == 0
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vacgt.f32 ?dwvec_D dwvec_N dwvec_M

	}

}

