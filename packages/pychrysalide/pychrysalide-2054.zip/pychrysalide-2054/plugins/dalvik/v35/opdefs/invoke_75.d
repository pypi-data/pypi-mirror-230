
/* Chrysalide - Outil d'analyse de fichiers binaires
 * ##FILE## - traduction d'instructions Dalvik
 *
 * Copyright (C) 2018 Cyrille Bagard
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


@title invoke-super/range

@id 117

@desc {

    Call the indicated method. See first <b>invoke-<i>kind</i></b> description above for details, caveats, and suggestions.

}

@encoding() {

    @format 3rc | pool_meth

    @syntax {

        @rules {

            call g_arch_instruction_set_flag(AIF_CALL)

        }

    }

    @hooks {

        link = handle_links_between_caller_and_callee

    }

}
