
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


@title VREV16, VREV32, VREV64

@id 360

@desc {

	VREV16 (Vector Reverse in halfwords) reverses the order of 8-bit elements in each halfword of the vector, and places the result in the corresponding destination vector. VREV32 (Vector Reverse in words) reverses the order of 8-bit or 16-bit elements in each word of the vector, and places the result in the corresponding destination vector. VREV64 (Vector Reverse in doublewords) reverses the order of 8-bit, 16-bit, or 32-bit elements in each doubleword of the vector, and places the result in the corresponding destination vector. There is no distinction between data types, other than size. Figure A8-6 shows two examples of the operation of VREV. VREV64.8, doubleword VREV64.32, quadword Dm Qm Dd Qm Figure A8-6 VREV operation examples Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 0 Vd(4) 0 0 0 op(2) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2887

		@assert {

			Q == 1
			op == 10
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev16.8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2888

		@assert {

			Q == 1
			op == 10
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev16.16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2889

		@assert {

			Q == 1
			op == 10
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev16.32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2890

		@assert {

			Q == 1
			op == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev32.8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2891

		@assert {

			Q == 1
			op == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev32.16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2892

		@assert {

			Q == 1
			op == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev32.32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2893

		@assert {

			Q == 1
			op == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev64.8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2894

		@assert {

			Q == 1
			op == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev64.16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2895

		@assert {

			Q == 1
			op == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev64.32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2896

		@assert {

			Q == 0
			op == 10
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev16.8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2897

		@assert {

			Q == 0
			op == 10
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev16.16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2898

		@assert {

			Q == 0
			op == 10
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev16.32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2899

		@assert {

			Q == 0
			op == 1
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev32.8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2900

		@assert {

			Q == 0
			op == 1
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev32.16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2901

		@assert {

			Q == 0
			op == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev32.32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2902

		@assert {

			Q == 0
			op == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev64.8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2903

		@assert {

			Q == 0
			op == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev64.16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2904

		@assert {

			Q == 0
			op == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev64.32 dwvec_D dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 size(2) 0 0 Vd(4) 0 0 0 op(2) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2905

		@assert {

			Q == 1
			op == 10
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev16.8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2906

		@assert {

			Q == 1
			op == 10
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev16.16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2907

		@assert {

			Q == 1
			op == 10
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev16.32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2908

		@assert {

			Q == 1
			op == 1
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev32.8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2909

		@assert {

			Q == 1
			op == 1
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev32.16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2910

		@assert {

			Q == 1
			op == 1
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev32.32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2911

		@assert {

			Q == 1
			op == 0
			size == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev64.8 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2912

		@assert {

			Q == 1
			op == 0
			size == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev64.16 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2913

		@assert {

			Q == 1
			op == 0
			size == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vrev64.32 qwvec_D qwvec_M

	}

	@syntax {

		@subid 2914

		@assert {

			Q == 0
			op == 10
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev16.8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2915

		@assert {

			Q == 0
			op == 10
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev16.16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2916

		@assert {

			Q == 0
			op == 10
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev16.32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2917

		@assert {

			Q == 0
			op == 1
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev32.8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2918

		@assert {

			Q == 0
			op == 1
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev32.16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2919

		@assert {

			Q == 0
			op == 1
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev32.32 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2920

		@assert {

			Q == 0
			op == 0
			size == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev64.8 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2921

		@assert {

			Q == 0
			op == 0
			size == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev64.16 dwvec_D dwvec_M

	}

	@syntax {

		@subid 2922

		@assert {

			Q == 0
			op == 0
			size == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vrev64.32 dwvec_D dwvec_M

	}

}

