
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


@title VBIC (immediate)

@id 283

@desc {

	Vector Bitwise Bit Clear (immediate) performs a bitwise AND between a register value and the complement of an immediate value, and returns the result into the destination vector. For the range of constants available, see One register and a modified immediate value on page A7-269. Depending on settings in the CPACR, NSACR, and HCPTR registers, and the security state and mode in which the instruction is executed, an attempt to execute the instruction might be UNDEFINED, or trapped to Hyp mode. Summary of access controls for Advanced SIMD functionality on page B1-1232 summarizes these controls. ARM deprecates the conditional execution of any Advanced SIMD instruction encoding that is not also available as a VFP instruction encoding, see Conditional execution on page A8-288.

}

@encoding (T1) {

	@word 1 1 1 i(1) 1 1 1 1 1 D(1) 0 0 0 imm3(3) Vd(4) cmode(4) 0 Q(1) 1 1 imm4(4)

	@syntax {

		@subid 953

		@assert {

			Q == 1
			cmode == 1000

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 qwvec_D imm64

	}

	@syntax {

		@subid 954

		@assert {

			Q == 1
			cmode == 1001

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 qwvec_D imm64

	}

	@syntax {

		@subid 955

		@assert {

			Q == 1
			cmode == 1010

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 qwvec_D imm64

	}

	@syntax {

		@subid 956

		@assert {

			Q == 1
			cmode == 1011

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 qwvec_D imm64

	}

	@syntax {

		@subid 957

		@assert {

			Q == 1
			cmode == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 958

		@assert {

			Q == 1
			cmode == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 959

		@assert {

			Q == 1
			cmode == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 960

		@assert {

			Q == 1
			cmode == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 961

		@assert {

			Q == 1
			cmode == 100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 962

		@assert {

			Q == 1
			cmode == 101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 963

		@assert {

			Q == 1
			cmode == 110

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 964

		@assert {

			Q == 1
			cmode == 111

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 965

		@assert {

			Q == 1
			cmode == 1100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 966

		@assert {

			Q == 1
			cmode == 1101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 967

		@assert {

			Q == 0
			cmode == 1000

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 dwvec_D imm64

	}

	@syntax {

		@subid 968

		@assert {

			Q == 0
			cmode == 1001

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 dwvec_D imm64

	}

	@syntax {

		@subid 969

		@assert {

			Q == 0
			cmode == 1010

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 dwvec_D imm64

	}

	@syntax {

		@subid 970

		@assert {

			Q == 0
			cmode == 1011

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 dwvec_D imm64

	}

	@syntax {

		@subid 971

		@assert {

			Q == 0
			cmode == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 972

		@assert {

			Q == 0
			cmode == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 973

		@assert {

			Q == 0
			cmode == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 974

		@assert {

			Q == 0
			cmode == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 975

		@assert {

			Q == 0
			cmode == 100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 976

		@assert {

			Q == 0
			cmode == 101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 977

		@assert {

			Q == 0
			cmode == 110

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 978

		@assert {

			Q == 0
			cmode == 111

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 979

		@assert {

			Q == 0
			cmode == 1100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 980

		@assert {

			Q == 0
			cmode == 1101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

}

@encoding (A1) {

	@word 1 1 1 i(1) 1 1 1 1 1 D(1) 0 0 0 imm3(3) Vd(4) cmode(4) 0 Q(1) 1 1 imm4(4)

	@syntax {

		@subid 981

		@assert {

			Q == 1
			cmode == 1000

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 qwvec_D imm64

	}

	@syntax {

		@subid 982

		@assert {

			Q == 1
			cmode == 1001

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 qwvec_D imm64

	}

	@syntax {

		@subid 983

		@assert {

			Q == 1
			cmode == 1010

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 qwvec_D imm64

	}

	@syntax {

		@subid 984

		@assert {

			Q == 1
			cmode == 1011

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 qwvec_D imm64

	}

	@syntax {

		@subid 985

		@assert {

			Q == 1
			cmode == 0

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 986

		@assert {

			Q == 1
			cmode == 1

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 987

		@assert {

			Q == 1
			cmode == 10

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 988

		@assert {

			Q == 1
			cmode == 11

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 989

		@assert {

			Q == 1
			cmode == 100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 990

		@assert {

			Q == 1
			cmode == 101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 991

		@assert {

			Q == 1
			cmode == 110

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 992

		@assert {

			Q == 1
			cmode == 111

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 993

		@assert {

			Q == 1
			cmode == 1100

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 994

		@assert {

			Q == 1
			cmode == 1101

		}

		@conv {

			qwvec_D = QuadWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 qwvec_D imm64

	}

	@syntax {

		@subid 995

		@assert {

			Q == 0
			cmode == 1000

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 dwvec_D imm64

	}

	@syntax {

		@subid 996

		@assert {

			Q == 0
			cmode == 1001

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 dwvec_D imm64

	}

	@syntax {

		@subid 997

		@assert {

			Q == 0
			cmode == 1010

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 dwvec_D imm64

	}

	@syntax {

		@subid 998

		@assert {

			Q == 0
			cmode == 1011

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i16 dwvec_D imm64

	}

	@syntax {

		@subid 999

		@assert {

			Q == 0
			cmode == 0

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 1000

		@assert {

			Q == 0
			cmode == 1

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 1001

		@assert {

			Q == 0
			cmode == 10

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 1002

		@assert {

			Q == 0
			cmode == 11

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 1003

		@assert {

			Q == 0
			cmode == 100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 1004

		@assert {

			Q == 0
			cmode == 101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 1005

		@assert {

			Q == 0
			cmode == 110

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 1006

		@assert {

			Q == 0
			cmode == 111

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 1007

		@assert {

			Q == 0
			cmode == 1100

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

	@syntax {

		@subid 1008

		@assert {

			Q == 0
			cmode == 1101

		}

		@conv {

			dwvec_D = DoubleWordVector(D:Vd)
			imm64 = AdvSIMDExpandImm('1', cmode, i:imm3:imm4)

		}

		@asm vbic.i32 dwvec_D imm64

	}

}

