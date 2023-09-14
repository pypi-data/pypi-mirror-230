
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


@title VDUP (ARM core register)

@id 306

@desc {

	This instruction duplicates an element from an ARM core register into every element of the destination vector. The destination vector elements can be 8-bit, 16-bit, or 32-bit fields. The source element is the least significant 8, 16, or 32 bits of the ARM core register. There is no distinction between data types. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 1 B(1) Q(1) 0 Vd(4) Rt(4) 1 0 1 1 D(1) 0 E(1) 1 0 0 0 0

	@syntax {

		@subid 1281

		@assert {

			Q == 1
			B == 1
			E == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.8 qwvec_D reg_T

	}

	@syntax {

		@subid 1282

		@assert {

			Q == 1
			B == 0
			E == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.16 qwvec_D reg_T

	}

	@syntax {

		@subid 1283

		@assert {

			Q == 1
			B == 0
			E == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.32 qwvec_D reg_T

	}

	@syntax {

		@subid 1284

		@assert {

			Q == 0
			B == 1
			E == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.8 dwvec_D reg_T

	}

	@syntax {

		@subid 1285

		@assert {

			Q == 0
			B == 0
			E == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.16 dwvec_D reg_T

	}

	@syntax {

		@subid 1286

		@assert {

			Q == 0
			B == 0
			E == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.32 dwvec_D reg_T

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 1 B(1) Q(1) 0 Vd(4) Rt(4) 1 0 1 1 D(1) 0 E(1) 1 0 0 0 0

	@syntax {

		@subid 1287

		@assert {

			Q == 1
			B == 1
			E == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.8 qwvec_D reg_T

	}

	@syntax {

		@subid 1288

		@assert {

			Q == 1
			B == 0
			E == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.16 qwvec_D reg_T

	}

	@syntax {

		@subid 1289

		@assert {

			Q == 1
			B == 0
			E == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.32 qwvec_D reg_T

	}

	@syntax {

		@subid 1290

		@assert {

			Q == 0
			B == 1
			E == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.8 dwvec_D reg_T

	}

	@syntax {

		@subid 1291

		@assert {

			Q == 0
			B == 0
			E == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.16 dwvec_D reg_T

	}

	@syntax {

		@subid 1292

		@assert {

			Q == 0
			B == 0
			E == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			reg_T = Register(Rt)

		}

		@asm vdup.32 dwvec_D reg_T

	}

}

