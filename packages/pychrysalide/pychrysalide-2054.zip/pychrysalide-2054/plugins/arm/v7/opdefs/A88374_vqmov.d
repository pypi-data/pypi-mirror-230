
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


@title VQMOVN, VQMOVUN

@id 352

@desc {

	Vector Saturating Move and Narrow copies each element of the operand vector to the corresponding element of the destination vector. The operand is a quadword vector. The elements can be any one of: • 16-bit, 32-bit, or 64-bit signed integers • 16-bit, 32-bit, or 64-bit unsigned integers. The result is a doubleword vector. The elements are half the length of the operand vector elements. If the operand is unsigned, the results are unsigned. If the operand is signed, the results can be signed or unsigned. If any of the results overflow, they are saturated. The cumulative saturation bit, FPSCR.QC, is set if saturation occurs. For details see Pseudocode details of saturation on page A2-44. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 0 Vd(4) 0 0 1 0 op(2) M(1) 0 Vm(4)

	@syntax {

		@subid 2743

		@assert {

			op == 1
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovun.s16 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2744

		@assert {

			op == 1
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovun.s32 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2745

		@assert {

			op == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovun.s64 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2746

		@assert {

			op == 10
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.s16 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2747

		@assert {

			op == 10
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.s32 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2748

		@assert {

			op == 10
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.s64 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2749

		@assert {

			op == 11
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.u16 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2750

		@assert {

			op == 11
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.u32 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2751

		@assert {

			op == 11
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.u64 dwvec_D qwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 1 0 Vd(4) 0 0 1 0 op(2) M(1) 0 Vm(4)

	@syntax {

		@subid 2752

		@assert {

			op == 1
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovun.s16 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2753

		@assert {

			op == 1
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovun.s32 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2754

		@assert {

			op == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovun.s64 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2755

		@assert {

			op == 10
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.s16 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2756

		@assert {

			op == 10
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.s32 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2757

		@assert {

			op == 10
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.s64 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2758

		@assert {

			op == 11
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.u16 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2759

		@assert {

			op == 11
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.u32 dwvec_D qwvec_M

	}

	@syntax {

		@subid 2760

		@assert {

			op == 11
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vqmovn.u64 dwvec_D qwvec_M

	}

}

