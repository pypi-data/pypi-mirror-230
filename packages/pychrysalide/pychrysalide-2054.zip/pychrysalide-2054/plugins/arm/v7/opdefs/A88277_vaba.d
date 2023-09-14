
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


@title VABA, VABAL

@id 272

@desc {

	Vector Absolute Difference and Accumulate {Long} subtracts the elements of one vector from the corresponding elements of another vector, and accumulates the absolute values of the results into the elements of the destination vector. Operand and result elements are either all integers of the same length, or optionally the results can be double the length of the operands. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction that is not also available as a VFP instruction, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 1 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 807

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

		@asm vaba.s8 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 808

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

		@asm vaba.s16 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 809

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

		@asm vaba.s32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 810

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

		@asm vaba.u8 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 811

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

		@asm vaba.u16 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 812

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

		@asm vaba.u32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 813

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

		@asm vaba.s8 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 814

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

		@asm vaba.s16 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 815

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

		@asm vaba.s32 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 816

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

		@asm vaba.u8 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 817

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

		@asm vaba.u16 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 818

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

		@asm vaba.u32 dwvec_D dwvec_N dwvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 0 1 0 1 N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 819

		@assert {

			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 820

		@assert {

			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 821

		@assert {

			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 822

		@assert {

			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 823

		@assert {

			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 824

		@assert {

			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.u32 qwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 1 1 N(1) Q(1) M(1) 1 Vm(4)

	@syntax {

		@subid 825

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

		@asm vaba.s8 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 826

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

		@asm vaba.s16 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 827

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

		@asm vaba.s32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 828

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

		@asm vaba.u8 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 829

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

		@asm vaba.u16 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 830

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

		@asm vaba.u32 qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 831

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

		@asm vaba.s8 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 832

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

		@asm vaba.s16 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 833

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

		@asm vaba.s32 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 834

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

		@asm vaba.u8 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 835

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

		@asm vaba.u16 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 836

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

		@asm vaba.u32 dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 U(1) 1 1 1 1 1 D(1) size(2) Vn(4) Vd(4) 0 1 0 1 N(1) 0 M(1) 0 Vm(4)

	@syntax {

		@subid 837

		@assert {

			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.s8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 838

		@assert {

			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.s16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 839

		@assert {

			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.s32 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 840

		@assert {

			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.u8 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 841

		@assert {

			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.u16 qwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 842

		@assert {

			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vabal.u32 qwvec_D dwvec_N dwvec_M

	}

}

