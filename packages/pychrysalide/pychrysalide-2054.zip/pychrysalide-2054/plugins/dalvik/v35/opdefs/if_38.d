
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


@title if-eqz

@id 56

@desc {

    Branch to the given destination if the given register's value compares with 0 as specified.

<b>Note:</b> The branch offset must not be <b>0</b>. (A spin loop may be legally constructed either by branching around a backward <b>goto</b> or by including a <b>nop</b> as a target before the branch.)

}

@encoding() {

    @format 21t

    @hooks {

        fetch = help_fetching_with_dalvik_ifz_instruction
        link = handle_dalvik_ifz_branch_as_link
        post = post_process_dalvik_ifz_target_resolution

    }

}
