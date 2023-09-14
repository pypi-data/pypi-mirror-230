
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


@title VTBL, VTBX

@id 379

@desc {

	Vector Table Lookup uses byte indexes in a control vector to look up byte values in a table and generate a new vector. Indexes out of range return 0. Vector Table Extension works in the same way, except that indexes out of range leave the destination element unchanged. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 Vn(4) Vd(4) 1 0 len(2) N(1) op(1) M(1) 0 Vm(4)

	@syntax {

		@subid 3707

		@assert {

			op == 0
			len == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			list = VectorTableDim1(dwvec_N)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbl.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3708

		@assert {

			op == 0
			len == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			list = VectorTableDim2(dwvec_N, dwvec_N_1)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbl.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3709

		@assert {

			op == 0
			len == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			dwvec_N_2 = NextDoubleWordVector(dwvec_N, 2)
			list = VectorTableDim3(dwvec_N, dwvec_N_1, dwvec_N_2)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbl.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3710

		@assert {

			op == 0
			len == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			dwvec_N_2 = NextDoubleWordVector(dwvec_N, 2)
			dwvec_N_3 = NextDoubleWordVector(dwvec_N, 3)
			list = VectorTableDim4(dwvec_N, dwvec_N_1, dwvec_N_2, dwvec_N_3)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbl.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3711

		@assert {

			op == 1
			len == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			list = VectorTableDim1(dwvec_N)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbx.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3712

		@assert {

			op == 1
			len == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			list = VectorTableDim2(dwvec_N, dwvec_N_1)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbx.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3713

		@assert {

			op == 1
			len == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			dwvec_N_2 = NextDoubleWordVector(dwvec_N, 2)
			list = VectorTableDim3(dwvec_N, dwvec_N_1, dwvec_N_2)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbx.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3714

		@assert {

			op == 1
			len == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			dwvec_N_2 = NextDoubleWordVector(dwvec_N, 2)
			dwvec_N_3 = NextDoubleWordVector(dwvec_N, 3)
			list = VectorTableDim4(dwvec_N, dwvec_N_1, dwvec_N_2, dwvec_N_3)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbx.8 dwvec_D list dwvec_M

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 1 1 1 1 D(1) 1 1 Vn(4) Vd(4) 1 0 len(2) N(1) op(1) M(1) 0 Vm(4)

	@syntax {

		@subid 3715

		@assert {

			op == 0
			len == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			list = VectorTableDim1(dwvec_N)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbl.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3716

		@assert {

			op == 0
			len == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			list = VectorTableDim2(dwvec_N, dwvec_N_1)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbl.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3717

		@assert {

			op == 0
			len == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			dwvec_N_2 = NextDoubleWordVector(dwvec_N, 2)
			list = VectorTableDim3(dwvec_N, dwvec_N_1, dwvec_N_2)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbl.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3718

		@assert {

			op == 0
			len == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			dwvec_N_2 = NextDoubleWordVector(dwvec_N, 2)
			dwvec_N_3 = NextDoubleWordVector(dwvec_N, 3)
			list = VectorTableDim4(dwvec_N, dwvec_N_1, dwvec_N_2, dwvec_N_3)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbl.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3719

		@assert {

			op == 1
			len == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			list = VectorTableDim1(dwvec_N)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbx.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3720

		@assert {

			op == 1
			len == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			list = VectorTableDim2(dwvec_N, dwvec_N_1)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbx.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3721

		@assert {

			op == 1
			len == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			dwvec_N_2 = NextDoubleWordVector(dwvec_N, 2)
			list = VectorTableDim3(dwvec_N, dwvec_N_1, dwvec_N_2)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbx.8 dwvec_D list dwvec_M

	}

	@syntax {

		@subid 3722

		@assert {

			op == 1
			len == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_N = DoubleWordVector(N:Vn)
			dwvec_N_1 = NextDoubleWordVector(dwvec_N, 1)
			dwvec_N_2 = NextDoubleWordVector(dwvec_N, 2)
			dwvec_N_3 = NextDoubleWordVector(dwvec_N, 3)
			list = VectorTableDim4(dwvec_N, dwvec_N_1, dwvec_N_2, dwvec_N_3)
			dwvec_M = DoubleWordVector(M:Vm)

		}

		@asm vtbx.8 dwvec_D list dwvec_M

	}

}

