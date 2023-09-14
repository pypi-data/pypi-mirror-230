
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


@title VMAX, VMIN (integer)

@id 321

@desc {

	Vector Maximum compares corresponding elements in two vectors, and copies the larger of each pair into the corresponding element in the destination vector. Vector Minimum compares corresponding elements in two vectors, and copies the smaller of each pair into the corresponding element in the destination vector. The operand vector elements can be any one of: • 8-bit, 16-bit, or 32-bit signed integers • 8-bit, 16-bit, or 32-bit unsigned integers. The result vector elements are the same size as the operand vector elements. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 1 0 N(1) Q(1) M(1) op(1) Vm(4)

	@syntax {

		@subid 2257

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

		@asm vmax.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2258

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

		@asm vmax.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2259

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

		@asm vmax.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2260

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

		@asm vmax.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2261

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

		@asm vmax.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2262

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

		@asm vmax.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2263

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

		@asm vmin.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2264

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

		@asm vmin.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2265

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

		@asm vmin.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2266

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

		@asm vmin.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2267

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

		@asm vmin.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2268

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

		@asm vmin.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2269

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

		@asm vmax.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2270

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

		@asm vmax.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2271

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

		@asm vmax.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2272

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

		@asm vmax.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2273

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

		@asm vmax.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2274

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

		@asm vmax.u32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2275

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

		@asm vmin.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2276

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

		@asm vmin.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2277

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

		@asm vmin.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2278

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

		@asm vmin.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2279

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

		@asm vmin.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2280

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

		@asm vmin.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 U(1) 1 1 1 1 0 D(1) size(2) Vn(4) Vd(4) 0 1 1 0 N(1) Q(1) M(1) op(1) Vm(4)

	@syntax {

		@subid 2281

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

		@asm vmax.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2282

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

		@asm vmax.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2283

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

		@asm vmax.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2284

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

		@asm vmax.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2285

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

		@asm vmax.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2286

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

		@asm vmax.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2287

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

		@asm vmin.s8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2288

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

		@asm vmin.s16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2289

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

		@asm vmin.s32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2290

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

		@asm vmin.u8 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2291

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

		@asm vmin.u16 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2292

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

		@asm vmin.u32 ?qwvec_D qwvec_N qwvec_M

	}

	@syntax {

		@subid 2293

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

		@asm vmax.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2294

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

		@asm vmax.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2295

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

		@asm vmax.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2296

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

		@asm vmax.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2297

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

		@asm vmax.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2298

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

		@asm vmax.u32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2299

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

		@asm vmin.s8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2300

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

		@asm vmin.s16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2301

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

		@asm vmin.s32 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2302

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

		@asm vmin.u8 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2303

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

		@asm vmin.u16 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2304

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

		@asm vmin.u32 ?dwvec_D dwvec_N dwvec_M

	}

}

