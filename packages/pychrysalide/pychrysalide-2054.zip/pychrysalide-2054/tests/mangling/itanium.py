#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


# Tests validant le décodage des types et des routines pour le format Itanium


from chrysacase import ChrysalideTestCase
from pychrysalide.mangling import ItaniumDemangler


class TestItaniumMangling(ChrysalideTestCase):
    """TestCase for pychrysalide.mangling.ItaniumDemangler."""

    def check_demangling(self, got, expected):
        """Check a given demangling result."""

        self.assertEqual(str(got), expected)


    def testItaniumTypeMangling(self):
        """Check Itanium type demangling with specifications samples."""

        # https://itanium-cxx-abi.github.io/cxx-abi/abi-examples.html#mangling

        demangler = ItaniumDemangler()

        demangled = demangler.decode_type('_ZN3FooIA4_iE3barE')
        self.check_demangling(demangled, 'Foo<int[4]>::bar')

        demangled = demangler.decode_type('_ZN1N1fE')
        self.check_demangling(demangled, 'N::f')

        demangled = demangler.decode_type('_ZN5Arena5levelE')
        self.check_demangling(demangled, 'Arena::level')

        demangled = demangler.decode_type('_ZN5StackIiiE5levelE')
        self.check_demangling(demangled, 'Stack<int, int>::level')


    def testItaniumRoutineMangling(self):
        """Check Itanium routine demangling with specifications samples."""

        # https://itanium-cxx-abi.github.io/cxx-abi/abi-examples.html#mangling

        demangler = ItaniumDemangler()

        demangled = demangler.decode_routine('_Z1fv')
        self.check_demangling(demangled, '??? f(void)')

        demangled = demangler.decode_routine('_Z1fi')
        self.check_demangling(demangled, '??? f(int)')

        demangled = demangler.decode_routine('_Z3foo3bar')
        self.check_demangling(demangled, '??? foo(bar)')

        demangled = demangler.decode_routine('_Zrm1XS_')
        self.check_demangling(demangled, '??? operator%(X, X)')

        demangled = demangler.decode_routine('_ZplR1XS0_')
        self.check_demangling(demangled, '??? operator+(X &, X &)')

        demangled = demangler.decode_routine('_ZlsRK1XS1_')
        self.check_demangling(demangled, '??? operator<<(const X &, const X &)')

        demangled = demangler.decode_routine('_Z1fIiEvi')
        self.check_demangling(demangled, 'void f<int>(int)')

        demangled = demangler.decode_routine('_Z5firstI3DuoEvS0_')
        self.check_demangling(demangled, 'void first<Duo>(Duo)')

        demangled = demangler.decode_routine('_Z5firstI3DuoEvT_')
        self.check_demangling(demangled, 'void first<Duo>(Duo)')

        demangled = demangler.decode_routine('_Z3fooIiPFidEiEvv')
        self.check_demangling(demangled, 'void foo<int, int (*) (double), int>(void)')

        demangled = demangler.decode_routine('_ZN6System5Sound4beepEv')
        self.check_demangling(demangled, '??? System::Sound::beep(void)')

        demangled = demangler.decode_routine('_Z1fI1XEvPVN1AIT_E1TE')
        self.check_demangling(demangled, 'void f<X>(volatile A<X>::T *)')

        demangled = demangler.decode_routine('_ZngILi42EEvN1AIXplT_Li2EEE1TE')
        self.check_demangling(demangled, 'void operator-<42>(A<42+2>::T)')

        demangled = demangler.decode_routine('_Z4makeI7FactoryiET_IT0_Ev')
        self.check_demangling(demangled, 'Factory<int> make<Factory, int>(void)')

        demangled = demangler.decode_routine('_Z3foo5Hello5WorldS0_S_')
        self.check_demangling(demangled, '??? foo(Hello, World, World, Hello)')

        demangled = demangler.decode_routine('_ZlsRSoRKSs')
        self.check_demangling(demangled, '??? operator<<(std::ostream &, const std::string &)')


    def testItaniumRoutineManglingInside(self):
        """Check Itanium routine demangling examples within the specifications."""

        # http://refspecs.linuxbase.org/cxxabi-1.83.html#linkage

        demangler = ItaniumDemangler()

        demangled = demangler.decode_routine('_Z1fM1AKFvvE')
        self.check_demangling(demangled, '??? f(const void (A::*) (void))')

        demangled = demangler.decode_routine('_Z1fPFvvEM1SFvvE')
        self.check_demangling(demangled, '??? f(void (*) (void), void (S::*) (void))')

        demangled = demangler.decode_routine('_ZN1N1TIiiE2mfES0_IddE')
        self.check_demangling(demangled, '??? N::T<int, int>::mf(N::T<double, double>)')


    def testItaniumRoutineManglingExtra(self):
        """Check extra Itanium routine demangling cases."""

        # http://refspecs.linuxbase.org/cxxabi-1.83.html#linkage

        demangler = ItaniumDemangler()

        # A la lecture, il s'agit d'une référence sur un tableau, et non
        # d'un tableau de références.
        demangled = demangler.decode_routine('_Z3fooILi2EEvRAplT_Li1E_i')
        self.check_demangling(demangled, 'void foo<2>(int[2+1] &)')


    def testAFL(self):
        """Tests from AFL."""

        demangler = ItaniumDemangler()

        demangled = demangler.decode_routine('_Z4makeI7FactoryiET_IT')
        self.assertIsNone(demangled)

        demangled = demangler.decode_routine('_Z4makeN7FactoryiET_IT0_Ev')
        self.assertIsNone(demangled)

        demangled = demangler.decode_routine('_Z4makeI7FactoryiET_I4makeIMGaptoryiET_T0_Ev')
        #self.assertIsNone(demangled)

        demangled = demangler.decode_routine('_Z4maktoryiaS_ILNd')
        self.assertIsNone(demangled)

        # ?!
        demangled = demangler.decode_routine('_Z4makeMVFactoryiES_')
        self.assertIsNotNone(demangled)


    def testOldRealWorldDemanglings(self):
        """Check real world demangling cases from previous code."""

        demangler = ItaniumDemangler()

        demangled = demangler.decode_routine('_ZNSt6vectorItSaItEE6insertEN9__gnu_cxx17__normal_iteratorIPtS1_EERKt')
        self.check_demangling(demangled, '??? std::vector<unsigned short, std::allocator<unsigned short>>::insert(__gnu_cxx::__normal_iterator<unsigned short *, std::vector<unsigned short, std::allocator<unsigned short>>>, const unsigned short &)')

        demangled = demangler.decode_routine('_ZSt26__uninitialized_fill_n_auxIP15CProfStringListiS0_ET_S2_T0_RKT1_12__false_type')
        self.check_demangling(demangled, 'CProfStringList *std::__uninitialized_fill_n_aux<CProfStringList *, int, CProfStringList>(CProfStringList *, int, const CProfStringList &, __false_type)')


        demangled = demangler.decode_routine('_ZN21IUDFSettingsValidator15IdNotIllegalStdEN13UDFParameters12UDF_STANDARDES1_')
        self.check_demangling(demangled, '??? IUDFSettingsValidator::IdNotIllegalStd(UDFParameters::UDF_STANDARD, UDFParameters::UDF_STANDARD)')

        demangled = demangler.decode_routine('_ZNSbI26NeroMediumFeatureSpecifierSt11char_traitsIS_ESaIS_EE4_Rep10_M_destroyERKS2_')
        self.check_demangling(demangled, '??? std::basic_string<NeroMediumFeatureSpecifier, std::char_traits<NeroMediumFeatureSpecifier>, std::allocator<NeroMediumFeatureSpecifier>>::_Rep::_M_destroy(const std::allocator<NeroMediumFeatureSpecifier> &)')

        demangled = demangler.decode_routine('_ZNSt6vectorIlSaIlEE6insertEN9__gnu_cxx17__normal_iteratorIPlS1_EERKl')
        self.check_demangling(demangled, '??? std::vector<long, std::allocator<long>>::insert(__gnu_cxx::__normal_iterator<long *, std::vector<long, std::allocator<long>>>, const long &)')

        demangled = demangler.decode_routine('_ZSt22__merge_without_bufferIN9__gnu_cxx17__normal_iteratorIP15CProfStringListSt6vectorIS2_SaIS2_EEEEiEvT_S8_S8_T0_S9_')
        self.check_demangling(demangled, 'void std::__merge_without_buffer<__gnu_cxx::__normal_iterator<CProfStringList *, std::vector<CProfStringList, std::allocator<CProfStringList>>>, int>(__gnu_cxx::__normal_iterator<CProfStringList *, std::vector<CProfStringList, std::allocator<CProfStringList>>>, __gnu_cxx::__normal_iterator<CProfStringList *, std::vector<CProfStringList, std::allocator<CProfStringList>>>, __gnu_cxx::__normal_iterator<CProfStringList *, std::vector<CProfStringList, std::allocator<CProfStringList>>>, int, int)')

        demangled = demangler.decode_routine('_ZSt11__push_heapIN9__gnu_cxx17__normal_iteratorIP8DRIVE_IDSt6vectorIS2_SaIS2_EEEEiS2_EvT_T0_S9_T1_')
        self.check_demangling(demangled, 'void std::__push_heap<__gnu_cxx::__normal_iterator<DRIVE_ID *, std::vector<DRIVE_ID, std::allocator<DRIVE_ID>>>, int, DRIVE_ID>(__gnu_cxx::__normal_iterator<DRIVE_ID *, std::vector<DRIVE_ID, std::allocator<DRIVE_ID>>>, int, int, DRIVE_ID)')

        demangled = demangler.decode_routine('_ZSt12partial_sortIN9__gnu_cxx17__normal_iteratorIP28CPR_MAI_ADPTY_SectorSequenceSt6vectorIS2_SaIS2_EEEEEvT_S8_S8_')
        self.check_demangling(demangled, 'void std::partial_sort<__gnu_cxx::__normal_iterator<CPR_MAI_ADPTY_SectorSequence *, std::vector<CPR_MAI_ADPTY_SectorSequence, std::allocator<CPR_MAI_ADPTY_SectorSequence>>>>(__gnu_cxx::__normal_iterator<CPR_MAI_ADPTY_SectorSequence *, std::vector<CPR_MAI_ADPTY_SectorSequence, std::allocator<CPR_MAI_ADPTY_SectorSequence>>>, __gnu_cxx::__normal_iterator<CPR_MAI_ADPTY_SectorSequence *, std::vector<CPR_MAI_ADPTY_SectorSequence, std::allocator<CPR_MAI_ADPTY_SectorSequence>>>, __gnu_cxx::__normal_iterator<CPR_MAI_ADPTY_SectorSequence *, std::vector<CPR_MAI_ADPTY_SectorSequence, std::allocator<CPR_MAI_ADPTY_SectorSequence>>>)')


    def testPrefixLoop(self):
        """Handle the loop between prefixes defined in the specifications."""

        demangler = ItaniumDemangler()

        demangled = demangler.decode_routine('_ZN2aaIN4ccccIfEEE5dddddEj')
        self.check_demangling(demangled, '??? aa<cccc<float>>::ddddd(unsigned int)')

        demangled = demangler.decode_routine('_ZN2aaIN4cccc4xxxxIfEEE5dddddEj')
        self.check_demangling(demangled, '??? aa<cccc::xxxx<float>>::ddddd(unsigned int)')

        demangled = demangler.decode_routine('_ZN3zzz2aaIN4cccc4xxxxIfEEE5dddddEj')
        self.check_demangling(demangled, '??? zzz::aa<cccc::xxxx<float>>::ddddd(unsigned int)')

        demangled = demangler.decode_routine('_ZN3aaa3bbbINS_3cccIfEEE3dddEj')
        self.check_demangling(demangled, '??? aaa::bbb<aaa::ccc<float>>::ddd(unsigned int)')


    def testAndroidSystem(self):
        """Check Itanium routine demangling from Android system cases."""

        demangler = ItaniumDemangler()

        demangled = demangler.decode_routine('_ZN7android7String8D1Ev')
        self.check_demangling(demangled, 'void android::String8::~String8(void)')

        demangled = demangler.decode_routine('_ZN6icu_556LocaleaSERKS0_')
        self.check_demangling(demangled, '??? icu_55::Locale::operator=(const icu_55::Locale &)')

        demangled = demangler.decode_routine('_ZNSt3__16vectorIfNS_9allocatorIfEEE8__appendEj')
        self.check_demangling(demangled, '??? std::__1::vector<float, std::__1::allocator<float>>::__append(unsigned int)')

        demangled = demangler.decode_routine('_ZN7android7String8C1EPKDsj')
        self.check_demangling(demangled, 'android::String8 *android::String8::String8(const char16_t *, unsigned int)')

        demangled = demangler.decode_routine('_ZNSt3__111__tree_nextIPNS_16__tree_node_baseIPvEEEET_S5_')
        self.check_demangling(demangled, 'std::__1::__tree_node_base<void *> *std::__1::__tree_next<std::__1::__tree_node_base<void *> *>(std::__1::__tree_node_base<void *> *)')

        demangled = demangler.decode_routine('_ZNSt3__110shared_ptrIN7android14CameraMetadataEE11make_sharedIJRKS2_EEES3_DpOT_')
        self.check_demangling(demangled, 'std::__1::shared_ptr<android::CameraMetadata> std::__1::shared_ptr<android::CameraMetadata>::make_shared<const android::CameraMetadata &>(const android::CameraMetadata &&&)')
