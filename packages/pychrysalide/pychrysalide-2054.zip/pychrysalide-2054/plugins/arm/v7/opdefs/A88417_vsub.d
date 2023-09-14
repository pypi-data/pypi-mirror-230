
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


@title VSUBL, VSUBW

@id 377

@desc {

	Vector Subtract Long subtracts the elements of one doubleword vector from the corresponding elements of another doubleword vector, and places the results in a quadword vector. Before subtracting, it sign-extends or zero-extends the elements of both operands. Vector Subtract Wide subtracts the elements of a doubleword vector from the corresponding elements of a quadword vector, and places the results in another quadword vector. Before subtracting, it sign-extends or zero-extends the elements of the doubleword operand. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 0 0 1 op(1) N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 3679

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

		@asm vsubl.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3680

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

		@asm vsubl.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3681

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

		@asm vsubl.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3682

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

		@asm vsubl.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3683

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

		@asm vsubl.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3684

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

		@asm vsubl.u32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3685

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

		@asm vsubw.s8 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 3686

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

		@asm vsubw.s16 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 3687

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

		@asm vsubw.s32 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 3688

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

		@asm vsubw.u8 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 3689

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

		@asm vsubw.u16 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 3690

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

		@asm vsubw.u32 ?qwvec_D qwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 0 0 1 op(1) N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 3691

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

		@asm vsubl.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3692

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

		@asm vsubl.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3693

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

		@asm vsubl.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3694

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

		@asm vsubl.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3695

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

		@asm vsubl.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3696

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

		@asm vsubl.u32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 3697

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

		@asm vsubw.s8 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 3698

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

		@asm vsubw.s16 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 3699

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

		@asm vsubw.s32 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 3700

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

		@asm vsubw.u8 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 3701

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

		@asm vsubw.u16 ?qwvec_D qwvec_N dwvec_M

	}

	@syntax {

		@subid 3702

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

		@asm vsubw.u32 ?qwvec_D qwvec_N dwvec_M

	}

}

