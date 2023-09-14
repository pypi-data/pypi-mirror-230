
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


@title VNMLA, VNMLS, VNMUL

@id 337

@desc {

	VNMLA multiplies together two floating-point register values, adds the negation of the floating-point value in the destination register to the negation of the product, and writes the result back to the destination register. VNMLS multiplies together two floating-point register values, adds the negation of the floating-point value in the destination register to the product, and writes the result back to the destination register. VNMUL multiplies together two floating-point register values, and writes the negation of the result to the destination register. Note ARM recommends that software does not use the VNMLA instruction in the Round towards Plus Infinity and Round towards Minus Infinity rounding modes, because the rounding of the product and of the sum can change the result of the instruction in opposite directions, defeating the purpose of these rounding modes. Depending on settings in the CPACR, NSACR, HCPTR, and FPEXC registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of general controls of CP10 and CP11 functionality on page B1-1230 summarizes these controls.

}

@encoding (T1) {

	@word 1 1 1 0 1 1 1 0 0 D(1) 0 1 Vn(4) Vd(4) 1 0 1 sz(1) N(1) op(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2531

		@assert {

			sz == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vnmla.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2532

		@assert {

			sz == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vnmls.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2533

		@assert {

			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vnmla.f32 swvec_D swvec_N swvec_M

	}

	@syntax {

		@subid 2534

		@assert {

			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vnmls.f32 swvec_D swvec_N swvec_M

	}

}

@encoding (T2) {

	@word 1 1 1 0 1 1 1 0 0 D(1) 1 0 Vn(4) Vd(4) 1 0 1 sz(1) N(1) 1 M(1) 0 Vm(4)

	@syntax {

		@subid 2535

		@assert {

			sz == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vnmul.f64 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2536

		@assert {

			sz == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vnmul.f32 ?swvec_D swvec_N swvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 0 1 1 1 0 0 D(1) 0 1 Vn(4) Vd(4) 1 0 1 sz(1) N(1) op(1) M(1) 0 Vm(4)

	@syntax {

		@subid 2537

		@assert {

			sz == 1
			op == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vnmla.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2538

		@assert {

			sz == 1
			op == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vnmls.f64 dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2539

		@assert {

			sz == 0
			op == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vnmla.f32 swvec_D swvec_N swvec_M

	}

	@syntax {

		@subid 2540

		@assert {

			sz == 0
			op == 1

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vnmls.f32 swvec_D swvec_N swvec_M

	}

}

@encoding (A2) {

	@word 1 1 1 0 1 1 1 0 0 D(1) 1 0 Vn(4) Vd(4) 1 0 1 sz(1) N(1) 1 M(1) 0 Vm(4)

	@syntax {

		@subid 2541

		@assert {

			sz == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vnmul.f64 ?dwvec_D dwvec_N dwvec_M

	}

	@syntax {

		@subid 2542

		@assert {

			sz == 0

		}

		@conv {

			swvec_D = SingleWordVector(Vd:D)
			swvec_N = SingleWordVector(Vn:N)
			swvec_M = SingleWordVector(Vm:M)

		}

		@asm vnmul.f32 ?swvec_D swvec_N swvec_M

	}

}

