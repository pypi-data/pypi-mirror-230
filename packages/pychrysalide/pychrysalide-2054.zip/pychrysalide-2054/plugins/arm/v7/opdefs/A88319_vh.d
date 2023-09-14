
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


@title VHADD, VHSUB

@id 311

@desc {

	Vector Halving Add adds corresponding elements in two vectors of integers, shifts each result right one bit, and places the final results in the destination vector. The results of the halving operations are truncated (for rounded results see VRHADD on page A8-1030). Vector Halving Subtract subtracts the elements of the second operand from the corresponding elements of the first operand, shifts each result right one bit, and places the final results in the destination vector. The results of the halving operations are truncated (there is no rounding version). The operand and result elements are all the same type, and can be any one of: • 8-bit, 16-bit, or 32-bit signed integers • 8-bit, 16-bit, or 32-bit unsigned integers. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 0 op(1) 0 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1325

		@assert {

			Q == 1
			op == 0
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1326

		@assert {

			Q == 1
			op == 0
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1327

		@assert {

			Q == 1
			op == 0
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1328

		@assert {

			Q == 1
			op == 0
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1329

		@assert {

			Q == 1
			op == 0
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1330

		@assert {

			Q == 1
			op == 0
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1331

		@assert {

			Q == 1
			op == 1
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1332

		@assert {

			Q == 1
			op == 1
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1333

		@assert {

			Q == 1
			op == 1
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1334

		@assert {

			Q == 1
			op == 1
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1335

		@assert {

			Q == 1
			op == 1
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1336

		@assert {

			Q == 1
			op == 1
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1337

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

		@asm vhadd.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1338

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

		@asm vhadd.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1339

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

		@asm vhadd.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1340

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

		@asm vhadd.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1341

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

		@asm vhadd.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1342

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

		@asm vhadd.u32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1343

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

		@asm vhsub.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1344

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

		@asm vhsub.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1345

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

		@asm vhsub.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1346

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

		@asm vhsub.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1347

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

		@asm vhsub.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1348

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

		@asm vhsub.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 0 op(1) 0 N(1) Q(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1349

		@assert {

			Q == 1
			op == 0
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1350

		@assert {

			Q == 1
			op == 0
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1351

		@assert {

			Q == 1
			op == 0
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1352

		@assert {

			Q == 1
			op == 0
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1353

		@assert {

			Q == 1
			op == 0
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1354

		@assert {

			Q == 1
			op == 0
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhadd.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1355

		@assert {

			Q == 1
			op == 1
			size == 0
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1356

		@assert {

			Q == 1
			op == 1
			size == 1
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1357

		@assert {

			Q == 1
			op == 1
			size == 10
			U == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1358

		@assert {

			Q == 1
			op == 1
			size == 0
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1359

		@assert {

			Q == 1
			op == 1
			size == 1
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1360

		@assert {

			Q == 1
			op == 1
			size == 10
			U == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			qwvec_N = QuadWordVector(N:Vn)
			qwvec_M = QuadWordVector(M:Vm)

		}

		@asm vhsub.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 1361

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

		@asm vhadd.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1362

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

		@asm vhadd.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1363

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

		@asm vhadd.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1364

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

		@asm vhadd.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1365

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

		@asm vhadd.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1366

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

		@asm vhadd.u32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1367

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

		@asm vhsub.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1368

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

		@asm vhsub.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1369

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

		@asm vhsub.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1370

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

		@asm vhsub.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1371

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

		@asm vhsub.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1372

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

		@asm vhsub.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

