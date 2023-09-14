
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


@title VABD, VABDL (integer)

@id 273

@desc {

	Vector Absolute Difference {Long} (integer) subtracts the elements of one vector from the corresponding elements of another vector, and places the absolute values of the results in the elements of the destination vector. Operand and result elements are either all integers of the same length, or optionally the results can be double the length of the operands. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction that is not also available as a VFP instruction, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 1 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 843

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

		@asm vabd.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 844

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

		@asm vabd.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 845

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

		@asm vabd.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 846

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

		@asm vabd.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 847

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

		@asm vabd.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 848

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

		@asm vabd.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 849

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

		@asm vabd.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 850

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

		@asm vabd.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 851

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

		@asm vabd.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 852

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

		@asm vabd.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 853

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

		@asm vabd.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 854

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

		@asm vabd.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 0 1 1 1 N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 855

		@assert {

			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 856

		@assert {

			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 857

		@assert {

			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 858

		@assert {

			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 859

		@assert {

			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 860

		@assert {

			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.u32 qwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 1 1 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 861

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

		@asm vabd.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 862

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

		@asm vabd.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 863

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

		@asm vabd.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 864

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

		@asm vabd.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 865

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

		@asm vabd.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 866

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

		@asm vabd.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 867

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

		@asm vabd.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 868

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

		@asm vabd.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 869

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

		@asm vabd.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 870

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

		@asm vabd.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 871

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

		@asm vabd.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 872

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

		@asm vabd.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 0 1 1 1 N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 873

		@assert {

			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 874

		@assert {

			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 875

		@assert {

			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 876

		@assert {

			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 877

		@assert {

			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 878

		@assert {

			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabdl.u32 qwvec_D dwvec_N dwvec_M

	}

}

