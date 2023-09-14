
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


@title VLD3 (single 3-element structure to all lanes)

@id 317

@desc {

	This instruction loads one 3-element structure from memory into all lanes of three registers. For details of the addressing mode see Advanced SIMD addressing mode on page A7-277. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 1 1 0 0 1 1 D(1) 1 0 Rn(4) Vd(4) 1 1 1 0 size(2) T(1) a(1) Rm(4)

	@syntax {

		@subid 1973

		@assert {

			Rm == 1111
			size == 0
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1974

		@assert {

			Rm == 1111
			size == 0
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1975

		@assert {

			Rm == 1111
			size == 1
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1976

		@assert {

			Rm == 1111
			size == 1
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1977

		@assert {

			Rm == 1111
			size == 10
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1978

		@assert {

			Rm == 1111
			size == 10
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1979

		@assert {

			Rm == 1101
			size == 0
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1980

		@assert {

			Rm == 1101
			size == 0
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1981

		@assert {

			Rm == 1101
			size == 1
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1982

		@assert {

			Rm == 1101
			size == 1
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1983

		@assert {

			Rm == 1101
			size == 10
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1984

		@assert {

			Rm == 1101
			size == 10
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1985

		@assert {

			Rm != 11x1
			size == 0
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1986

		@assert {

			Rm != 11x1
			size == 0
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1987

		@assert {

			Rm != 11x1
			size == 1
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1988

		@assert {

			Rm != 11x1
			size == 1
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1989

		@assert {

			Rm != 11x1
			size == 10
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1990

		@assert {

			Rm != 11x1
			size == 10
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.32 list maccess

	}

}

@encoding (A1) {

	@word 1 1 1 1 1 0 0 1 1 D(1) 1 0 Rn(4) Vd(4) 1 1 1 0 size(2) T(1) a(1) Rm(4)

	@syntax {

		@subid 1991

		@assert {

			Rm == 1111
			size == 0
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1992

		@assert {

			Rm == 1111
			size == 0
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1993

		@assert {

			Rm == 1111
			size == 1
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1994

		@assert {

			Rm == 1111
			size == 1
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 1995

		@assert {

			Rm == 1111
			size == 10
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1996

		@assert {

			Rm == 1111
			size == 10
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessOffset(reg_N, NULL)

		}

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 1997

		@assert {

			Rm == 1101
			size == 0
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1998

		@assert {

			Rm == 1101
			size == 0
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 1999

		@assert {

			Rm == 1101
			size == 1
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 2000

		@assert {

			Rm == 1101
			size == 1
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 2001

		@assert {

			Rm == 1101
			size == 10
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 2002

		@assert {

			Rm == 1101
			size == 10
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			maccess = MemAccessPreIndexed(reg_N, NULL)

		}

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 2003

		@assert {

			Rm != 11x1
			size == 0
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 2004

		@assert {

			Rm != 11x1
			size == 0
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.8 list maccess

	}

	@syntax {

		@subid 2005

		@assert {

			Rm != 11x1
			size == 1
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 2006

		@assert {

			Rm != 11x1
			size == 1
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.16 list maccess

	}

	@syntax {

		@subid 2007

		@assert {

			Rm != 11x1
			size == 10
			T == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_1 = NextDoubleWordVector(dwvec_D, 1)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			list = VectorTableDim3(dwvec_D, dwvec_D_1, dwvec_D_2)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.32 list maccess

	}

	@syntax {

		@subid 2008

		@assert {

			Rm != 11x1
			size == 10
			T == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			dwvec_D_2 = NextDoubleWordVector(dwvec_D, 2)
			dwvec_D_4 = NextDoubleWordVector(dwvec_D, 4)
			list = VectorTableDim3(dwvec_D, dwvec_D_2, dwvec_D_4)
			reg_N = Register(Rn)
			reg_M = Register(Rm)
			maccess = MemAccessPostIndexed(reg_N, reg_M)

		}

		@asm vld3.32 list maccess

	}

}

