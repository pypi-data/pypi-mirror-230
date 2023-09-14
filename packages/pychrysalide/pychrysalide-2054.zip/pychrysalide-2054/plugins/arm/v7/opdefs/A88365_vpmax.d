
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


@title VPMAX, VPMIN (integer)

@id 346

@desc {

	Vector Pairwise Maximum compares adjacent pairs of elements in two doubleword vectors, and copies the larger of each pair into the corresponding element in the destination doubleword vector. Vector Pairwise Minimum compares adjacent pairs of elements in two doubleword vectors, and copies the smaller of each pair into the corresponding element in the destination doubleword vector. Figure A8-5 shows an example of the operation of VPMAX. Dm Dn max max max max Dd Figure A8-5 VPMAX operation for data type S16 or U16 Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 1 0 1 0 N(1) Q(1) M(1) op(1) Vm(4)

	@syntax {

		@subid 2663

		@assert {

			Q == 0
			op == 0
			size == 0
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2664

		@assert {

			Q == 0
			op == 0
			size == 1
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2665

		@assert {

			Q == 0
			op == 0
			size == 10
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2666

		@assert {

			Q == 0
			op == 0
			size == 0
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2667

		@assert {

			Q == 0
			op == 0
			size == 1
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2668

		@assert {

			Q == 0
			op == 0
			size == 10
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.u32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2669

		@assert {

			Q == 0
			op == 1
			size == 0
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2670

		@assert {

			Q == 0
			op == 1
			size == 1
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2671

		@assert {

			Q == 0
			op == 1
			size == 10
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2672

		@assert {

			Q == 0
			op == 1
			size == 0
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2673

		@assert {

			Q == 0
			op == 1
			size == 1
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2674

		@assert {

			Q == 0
			op == 1
			size == 10
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 1 0 1 0 N(1) Q(1) M(1) op(1) Vm(4)

	@syntax {

		@subid 2675

		@assert {

			Q == 0
			op == 0
			size == 0
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2676

		@assert {

			Q == 0
			op == 0
			size == 1
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2677

		@assert {

			Q == 0
			op == 0
			size == 10
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2678

		@assert {

			Q == 0
			op == 0
			size == 0
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2679

		@assert {

			Q == 0
			op == 0
			size == 1
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2680

		@assert {

			Q == 0
			op == 0
			size == 10
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmax.u32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2681

		@assert {

			Q == 0
			op == 1
			size == 0
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2682

		@assert {

			Q == 0
			op == 1
			size == 1
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2683

		@assert {

			Q == 0
			op == 1
			size == 10
			U == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2684

		@assert {

			Q == 0
			op == 1
			size == 0
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2685

		@assert {

			Q == 0
			op == 1
			size == 1
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2686

		@assert {

			Q == 0
			op == 1
			size == 10
			U == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vpmin.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

