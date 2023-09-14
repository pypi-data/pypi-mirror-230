
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


@title VMVN (immediate)

@id 334

@desc {

	Vector Bitwise NOT (immediate) places the bitwise inverse of an immediate integer constant into every element of the destination register. For the range of constants available, see One register and a modified immediate value on page A7-269. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 i(1) 1 1 1 1 1 D(1) 0 0 0 imm3(3) Vd(4) cmode(4) 0 Q(1) 1 1 imm4(4)

	@syntax {

		@subid 2461

		@assert {

			Q == 1
			cmode == 1000

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2462

		@assert {

			Q == 1
			cmode == 1001

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2463

		@assert {

			Q == 1
			cmode == 1010

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2464

		@assert {

			Q == 1
			cmode == 1011

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2465

		@assert {

			Q == 1
			cmode == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2466

		@assert {

			Q == 1
			cmode == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2467

		@assert {

			Q == 1
			cmode == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2468

		@assert {

			Q == 1
			cmode == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2469

		@assert {

			Q == 1
			cmode == 100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2470

		@assert {

			Q == 1
			cmode == 101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2471

		@assert {

			Q == 1
			cmode == 110

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2472

		@assert {

			Q == 1
			cmode == 111

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2473

		@assert {

			Q == 1
			cmode == 1100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2474

		@assert {

			Q == 1
			cmode == 1101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2475

		@assert {

			Q == 0
			cmode == 1000

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2476

		@assert {

			Q == 0
			cmode == 1001

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2477

		@assert {

			Q == 0
			cmode == 1010

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2478

		@assert {

			Q == 0
			cmode == 1011

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2479

		@assert {

			Q == 0
			cmode == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2480

		@assert {

			Q == 0
			cmode == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2481

		@assert {

			Q == 0
			cmode == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2482

		@assert {

			Q == 0
			cmode == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2483

		@assert {

			Q == 0
			cmode == 100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2484

		@assert {

			Q == 0
			cmode == 101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2485

		@assert {

			Q == 0
			cmode == 110

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2486

		@assert {

			Q == 0
			cmode == 111

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2487

		@assert {

			Q == 0
			cmode == 1100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2488

		@assert {

			Q == 0
			cmode == 1101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

}

@encoding (A1) {

	@word 1 1 1 i(1) 1 1 1 1 1 D(1) 0 0 0 imm3(3) Vd(4) cmode(4) 0 Q(1) 1 1 imm4(4)

	@syntax {

		@subid 2489

		@assert {

			Q == 1
			cmode == 1000

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2490

		@assert {

			Q == 1
			cmode == 1001

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2491

		@assert {

			Q == 1
			cmode == 1010

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2492

		@assert {

			Q == 1
			cmode == 1011

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 qwvec_D imm64

	}

	@syntax {

		@subid 2493

		@assert {

			Q == 1
			cmode == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2494

		@assert {

			Q == 1
			cmode == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2495

		@assert {

			Q == 1
			cmode == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2496

		@assert {

			Q == 1
			cmode == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2497

		@assert {

			Q == 1
			cmode == 100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2498

		@assert {

			Q == 1
			cmode == 101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2499

		@assert {

			Q == 1
			cmode == 110

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2500

		@assert {

			Q == 1
			cmode == 111

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2501

		@assert {

			Q == 1
			cmode == 1100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2502

		@assert {

			Q == 1
			cmode == 1101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 qwvec_D imm64

	}

	@syntax {

		@subid 2503

		@assert {

			Q == 0
			cmode == 1000

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2504

		@assert {

			Q == 0
			cmode == 1001

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2505

		@assert {

			Q == 0
			cmode == 1010

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2506

		@assert {

			Q == 0
			cmode == 1011

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i16 dwvec_D imm64

	}

	@syntax {

		@subid 2507

		@assert {

			Q == 0
			cmode == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2508

		@assert {

			Q == 0
			cmode == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2509

		@assert {

			Q == 0
			cmode == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2510

		@assert {

			Q == 0
			cmode == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2511

		@assert {

			Q == 0
			cmode == 100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2512

		@assert {

			Q == 0
			cmode == 101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2513

		@assert {

			Q == 0
			cmode == 110

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2514

		@assert {

			Q == 0
			cmode == 111

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2515

		@assert {

			Q == 0
			cmode == 1100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

	@syntax {

		@subid 2516

		@assert {

			Q == 0
			cmode == 1101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vmvn.i32 dwvec_D imm64

	}

}

