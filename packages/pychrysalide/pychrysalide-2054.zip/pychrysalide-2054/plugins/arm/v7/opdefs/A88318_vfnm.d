
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


@title VFNMA, VFNMS

@id 310

@desc {

	Vector Fused Negate Multiply Accumulate negates one floating-point register value and multiplies it by another floating-point register value, adds the negation of the floating-point value in the destination register to the product, and writes the result back to the destination register. The instruction does not round the result of the multiply before the addition. Vector Fused Negate Multiply Subtract multiplies together two floating-point register values, adds the negation of the floating-point value in the destination register to the product, and writes the result back to the destination register. The instruction does not round the result of the multiply before the addition. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 summarizes these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 0 1 Vn(4) Vd(4) 1 0 1 sz(1) N(1) op(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1317

		@assert {

			sz == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vfnma.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1318

		@assert {

			sz == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vfnms.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1319

		@assert {

			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vfnma.f32 swvec_D swvec_N swvec_M

	}

	@syntax {

		@subid 1320

		@assert {

			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vfnms.f32 swvec_D swvec_N swvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 1 D(1) 0 1 Vn(4) Vd(4) 1 0 1 sz(1) N(1) op(1) M(1) 0 Vm(4)

	@syntax {

		@subid 1321

		@assert {

			sz == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vfnma.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1322

		@assert {

			sz == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vfnms.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 1323

		@assert {

			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vfnma.f32 swvec_D swvec_N swvec_M

	}

	@syntax {

		@subid 1324

		@assert {

			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vfnms.f32 swvec_D swvec_N swvec_M

	}

}

