
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


@title VORR (immediate)

@id 340

@desc {

	This instruction takes the contents of the destination vector, performs a bitwise OR with an immediate constant, and returns the result into the destination vector. For the range of constants available, see One register and a modified immediate value on page A7-269. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 i(1) 1 1 1 1 1 D(1) 0 0 0 imm3(3) Vd(4) cmode(4) 0 Q(1) 0 1 imm4(4)

	@syntax {

		@subid 2547

		@assert {

			Q == 1
			cmode == 1000

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2548

		@assert {

			Q == 1
			cmode == 1001

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2549

		@assert {

			Q == 1
			cmode == 1010

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2550

		@assert {

			Q == 1
			cmode == 1011

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2551

		@assert {

			Q == 1
			cmode == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2552

		@assert {

			Q == 1
			cmode == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2553

		@assert {

			Q == 1
			cmode == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2554

		@assert {

			Q == 1
			cmode == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2555

		@assert {

			Q == 1
			cmode == 100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2556

		@assert {

			Q == 1
			cmode == 101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2557

		@assert {

			Q == 1
			cmode == 110

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2558

		@assert {

			Q == 1
			cmode == 111

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2559

		@assert {

			Q == 1
			cmode == 1100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2560

		@assert {

			Q == 1
			cmode == 1101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2561

		@assert {

			Q == 0
			cmode == 1000

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2562

		@assert {

			Q == 0
			cmode == 1001

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2563

		@assert {

			Q == 0
			cmode == 1010

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2564

		@assert {

			Q == 0
			cmode == 1011

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2565

		@assert {

			Q == 0
			cmode == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2566

		@assert {

			Q == 0
			cmode == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2567

		@assert {

			Q == 0
			cmode == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2568

		@assert {

			Q == 0
			cmode == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2569

		@assert {

			Q == 0
			cmode == 100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2570

		@assert {

			Q == 0
			cmode == 101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2571

		@assert {

			Q == 0
			cmode == 110

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2572

		@assert {

			Q == 0
			cmode == 111

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2573

		@assert {

			Q == 0
			cmode == 1100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2574

		@assert {

			Q == 0
			cmode == 1101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

}

@encoding (A1) {

	@word 1 1 1 i(1) 1 1 1 1 1 D(1) 0 0 0 imm3(3) Vd(4) cmode(4) 0 Q(1) 0 1 imm4(4)

	@syntax {

		@subid 2575

		@assert {

			Q == 1
			cmode == 1000

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2576

		@assert {

			Q == 1
			cmode == 1001

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2577

		@assert {

			Q == 1
			cmode == 1010

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2578

		@assert {

			Q == 1
			cmode == 1011

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2579

		@assert {

			Q == 1
			cmode == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2580

		@assert {

			Q == 1
			cmode == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2581

		@assert {

			Q == 1
			cmode == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2582

		@assert {

			Q == 1
			cmode == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2583

		@assert {

			Q == 1
			cmode == 100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2584

		@assert {

			Q == 1
			cmode == 101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2585

		@assert {

			Q == 1
			cmode == 110

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2586

		@assert {

			Q == 1
			cmode == 111

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2587

		@assert {

			Q == 1
			cmode == 1100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2588

		@assert {

			Q == 1
			cmode == 1101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2589

		@assert {

			Q == 0
			cmode == 1000

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2590

		@assert {

			Q == 0
			cmode == 1001

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2591

		@assert {

			Q == 0
			cmode == 1010

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2592

		@assert {

			Q == 0
			cmode == 1011

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2593

		@assert {

			Q == 0
			cmode == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2594

		@assert {

			Q == 0
			cmode == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2595

		@assert {

			Q == 0
			cmode == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2596

		@assert {

			Q == 0
			cmode == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2597

		@assert {

			Q == 0
			cmode == 100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2598

		@assert {

			Q == 0
			cmode == 101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2599

		@assert {

			Q == 0
			cmode == 110

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2600

		@assert {

			Q == 0
			cmode == 111

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2601

		@assert {

			Q == 0
			cmode == 1100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2602

		@assert {

			Q == 0
			cmode == 1101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('0', cmode, i:imm3:imm4)

		}

		@asm vorr.i32 dwvec_D imm64

	}

}

