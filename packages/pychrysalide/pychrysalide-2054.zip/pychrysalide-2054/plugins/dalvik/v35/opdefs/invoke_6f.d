
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


@title invoke-super

@id 111

@desc {

    Call the indicated method. The result (if any) may be stored with an appropriate <b>move-result*</b> variant as the immediately subsequent instruction.

<b>invoke-virtual</b> is used to invoke a normal virtual method (a method that is not <b>private</b>, <b>static</b>, or <b>final</b>, and is also not a constructor).

When the <b>method_id</b> references a method of a non-interface class, <b>invoke-super</b> is used to invoke the closest superclass's virtual method (as opposed to the one with the same <b>method_id</b> in the calling class). The same method restrictions hold as for <b>invoke-virtual</b>.

In Dex files version <b>037</b> or later, if the <b>method_id</b> refers to an interface method, <b>invoke-super</b> is used to invoke the most specific, non-overridden version of that method defined on that interface. The same method restrictions hold as for <b>invoke-virtual</b>. In Dex files prior to version <b>037</b>, having an interface <b>method_id</b> is illegal and undefined.

<b>invoke-direct</b> is used to invoke a non-<b>static</b> direct method (that is, an instance method that is by its nature non-overridable, namely either a <b>private</b> instance method or a constructor).

<b>invoke-static</b> is used to invoke a <b>static</b> method (which is always considered a direct method).

<b>invoke-interface</b> is used to invoke an <b>interface</b> method, that is, on an object whose concrete class isn't known, using a <b>method_id</b> that refers to an <b>interface</b>.

<b>Note:</b> These opbs are reasonable candidates for static linking, altering the method argument to be a more direct offset (or pair thereof).

}

@encoding() {

    @format 35c | pool_meth

    @syntax {

        @rules {

            call g_arch_instruction_set_flag(AIF_CALL)

        }

    }

    @hooks {

        link = handle_links_between_caller_and_callee

    }

}
