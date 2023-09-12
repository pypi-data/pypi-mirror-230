#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/int.hpp>
#include <pythonic/include/types/uint32.hpp>
#include <pythonic/include/types/ndarray.hpp>
#include <pythonic/include/types/numpy_texpr.hpp>
#include <pythonic/types/uint32.hpp>
#include <pythonic/types/ndarray.hpp>
#include <pythonic/types/int.hpp>
#include <pythonic/types/numpy_texpr.hpp>
#include <pythonic/include/builtins/getattr.hpp>
#include <pythonic/include/builtins/len.hpp>
#include <pythonic/include/builtins/list.hpp>
#include <pythonic/include/builtins/range.hpp>
#include <pythonic/include/builtins/tuple.hpp>
#include <pythonic/include/numpy/ndarray/reshape.hpp>
#include <pythonic/include/numpy/ravel.hpp>
#include <pythonic/include/numpy/square.hpp>
#include <pythonic/include/numpy/stack.hpp>
#include <pythonic/include/numpy/uint32.hpp>
#include <pythonic/include/numpy/zeros.hpp>
#include <pythonic/include/operator_/add.hpp>
#include <pythonic/include/operator_/iadd.hpp>
#include <pythonic/include/operator_/mul.hpp>
#include <pythonic/include/operator_/neg.hpp>
#include <pythonic/include/operator_/sub.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/builtins/getattr.hpp>
#include <pythonic/builtins/len.hpp>
#include <pythonic/builtins/list.hpp>
#include <pythonic/builtins/range.hpp>
#include <pythonic/builtins/tuple.hpp>
#include <pythonic/numpy/ndarray/reshape.hpp>
#include <pythonic/numpy/ravel.hpp>
#include <pythonic/numpy/square.hpp>
#include <pythonic/numpy/stack.hpp>
#include <pythonic/numpy/uint32.hpp>
#include <pythonic/numpy/zeros.hpp>
#include <pythonic/operator_/add.hpp>
#include <pythonic/operator_/iadd.hpp>
#include <pythonic/operator_/mul.hpp>
#include <pythonic/operator_/neg.hpp>
#include <pythonic/operator_/sub.hpp>
#include <pythonic/types/str.hpp>
namespace 
{
  namespace __pythran_landscape
  {
    struct __transonic__
    {
      typedef void callable;
      typedef void pure;
      struct type
      {
        typedef pythonic::types::str __type0;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type0>())) __type1;
        typedef typename pythonic::returnable<__type1>::type __type2;
        typedef __type2 result_type;
      }  ;
      inline
      typename type::result_type operator()() const;
      ;
    }  ;
    struct ADJ_ARR_DTYPE
    {
      typedef void callable;
      typedef void pure;
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::uint32{})>::type>::type __type0;
        typedef typename pythonic::returnable<__type0>::type __type1;
        typedef __type1 result_type;
      }  ;
      inline
      typename type::result_type operator()() const;
      ;
    }  ;
    struct compute_adjacency_arr
    {
      typedef void callable;
      ;
      template <typename argument_type0 , typename argument_type1 >
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::ndarray::functor::reshape{})>::type>::type __type0;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::stack{})>::type>::type __type1;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::zeros{})>::type>::type __type2;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::square{})>::type>::type __type3;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type4;
        typedef __type4 __type5;
        typedef long __type6;
        typedef decltype(pythonic::operator_::add(std::declval<__type5>(), std::declval<__type6>())) __type7;
        typedef typename pythonic::assignable<__type7>::type __type8;
        typedef __type8 __type9;
        typedef decltype(std::declval<__type3>()(std::declval<__type9>())) __type10;
        typedef ADJ_ARR_DTYPE __type11;
        typedef decltype(std::declval<__type11>()()) __type12;
        typedef decltype(std::declval<__type2>()(std::declval<__type10>(), std::declval<__type12>())) __type13;
        typedef typename pythonic::assignable<__type13>::type __type14;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::ravel{})>::type>::type __type15;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type16;
        typedef __type16 __type17;
        typedef decltype(std::declval<__type15>()(std::declval<__type17>())) __type18;
        typedef typename pythonic::assignable<__type18>::type __type19;
        typedef __type19 __type20;
        typedef decltype(pythonic::types::as_const(std::declval<__type20>())) __type21;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::range{})>::type>::type __type22;
        typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, std::declval<__type17>())) __type24;
        typedef decltype(pythonic::types::as_const(std::declval<__type24>())) __type25;
        typedef typename std::tuple_element<1,typename std::remove_reference<__type25>::type>::type __type26;
        typedef typename pythonic::assignable<__type26>::type __type27;
        typedef __type27 __type28;
        typedef decltype(pythonic::operator_::add(std::declval<__type28>(), std::declval<__type6>())) __type29;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::len{})>::type>::type __type30;
        typedef decltype(std::declval<__type30>()(std::declval<__type20>())) __type32;
        typedef decltype(pythonic::operator_::sub(std::declval<__type32>(), std::declval<__type29>())) __type33;
        typedef typename pythonic::lazy<__type33>::type __type34;
        typedef __type34 __type35;
        typedef decltype(std::declval<__type22>()(std::declval<__type29>(), std::declval<__type35>())) __type36;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type36>::type::iterator>::value_type>::type __type37;
        typedef __type37 __type38;
        typedef decltype(std::declval<__type21>()[std::declval<__type38>()]) __type39;
        typedef typename pythonic::lazy<__type39>::type __type40;
        typedef __type40 __type41;
        typedef container<typename std::remove_reference<__type39>::type> __type43;
        typedef typename __combined<__type19,__type43>::type __type44;
        typedef __type44 __type45;
        typedef decltype(pythonic::types::as_const(std::declval<__type45>())) __type46;
        typedef pythonic::types::list<typename std::remove_reference<__type6>::type> __type48;
        typedef typename pythonic::lazy<__type48>::type __type49;
        typedef __type49 __type50;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type50>::type::iterator>::value_type>::type __type51;
        typedef __type51 __type52;
        typedef decltype(pythonic::operator_::add(std::declval<__type38>(), std::declval<__type52>())) __type53;
        typedef decltype(std::declval<__type46>()[std::declval<__type53>()]) __type54;
        typedef decltype(pythonic::operator_::mul(std::declval<__type9>(), std::declval<__type54>())) __type55;
        typedef decltype(pythonic::operator_::add(std::declval<__type41>(), std::declval<__type55>())) __type56;
        typedef indexable<__type56> __type57;
        typedef container<typename std::remove_reference<__type6>::type> __type58;
        typedef typename __combined<__type14,__type57,__type58>::type __type59;
        typedef __type59 __type60;
        typedef pythonic::types::list<typename std::remove_reference<__type28>::type> __type71;
        typedef decltype(pythonic::operator_::neg(std::declval<__type28>())) __type73;
        typedef pythonic::types::list<typename std::remove_reference<__type73>::type> __type74;
        typedef typename __combined<__type71,__type74>::type __type75;
        typedef typename pythonic::lazy<__type75>::type __type76;
        typedef __type76 __type77;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type77>::type::iterator>::value_type>::type __type78;
        typedef __type78 __type79;
        typedef decltype(pythonic::operator_::add(std::declval<__type38>(), std::declval<__type79>())) __type80;
        typedef decltype(std::declval<__type46>()[std::declval<__type80>()]) __type81;
        typedef decltype(pythonic::operator_::mul(std::declval<__type9>(), std::declval<__type81>())) __type82;
        typedef decltype(pythonic::operator_::add(std::declval<__type41>(), std::declval<__type82>())) __type83;
        typedef indexable<__type83> __type84;
        typedef typename __combined<__type14,__type84,__type58>::type __type85;
        typedef __type85 __type86;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type60>(), std::declval<__type86>())) __type87;
        typedef decltype(std::declval<__type1>()(std::declval<__type87>())) __type88;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type6>(), std::declval<__type9>(), std::declval<__type9>())) __type91;
        typedef decltype(std::declval<__type0>()(std::declval<__type88>(), std::declval<__type91>())) __type92;
        typedef typename pythonic::returnable<__type92>::type __type93;
        typedef __type93 result_type;
      }  
      ;
      template <typename argument_type0 , typename argument_type1 >
      inline
      typename type<argument_type0, argument_type1>::result_type operator()(argument_type0 padded_arr, argument_type1 num_classes) const
      ;
    }  ;
    inline
    typename __transonic__::type::result_type __transonic__::operator()() const
    {
      {
        static typename __transonic__::type::result_type tmp_global = pythonic::types::make_tuple(pythonic::types::str("0.5.3"));
        return tmp_global;
      }
    }
    inline
    typename ADJ_ARR_DTYPE::type::result_type ADJ_ARR_DTYPE::operator()() const
    {
      {
        static typename ADJ_ARR_DTYPE::type::result_type tmp_global = pythonic::numpy::functor::uint32{};
        return tmp_global;
      }
    }
    template <typename argument_type0 , typename argument_type1 >
    inline
    typename compute_adjacency_arr::type<argument_type0, argument_type1>::result_type compute_adjacency_arr::operator()(argument_type0 padded_arr, argument_type1 num_classes) const
    {
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::zeros{})>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::square{})>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type2;
      typedef __type2 __type3;
      typedef long __type4;
      typedef decltype(pythonic::operator_::add(std::declval<__type3>(), std::declval<__type4>())) __type5;
      typedef typename pythonic::assignable<__type5>::type __type6;
      typedef __type6 __type7;
      typedef decltype(std::declval<__type1>()(std::declval<__type7>())) __type8;
      typedef ADJ_ARR_DTYPE __type9;
      typedef decltype(std::declval<__type9>()()) __type10;
      typedef decltype(std::declval<__type0>()(std::declval<__type8>(), std::declval<__type10>())) __type11;
      typedef typename pythonic::assignable<__type11>::type __type12;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::ravel{})>::type>::type __type13;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type14;
      typedef __type14 __type15;
      typedef decltype(std::declval<__type13>()(std::declval<__type15>())) __type16;
      typedef typename pythonic::assignable<__type16>::type __type17;
      typedef __type17 __type18;
      typedef decltype(pythonic::types::as_const(std::declval<__type18>())) __type19;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::range{})>::type>::type __type20;
      typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, std::declval<__type15>())) __type22;
      typedef decltype(pythonic::types::as_const(std::declval<__type22>())) __type23;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type23>::type>::type __type24;
      typedef typename pythonic::assignable<__type24>::type __type25;
      typedef __type25 __type26;
      typedef pythonic::types::list<typename std::remove_reference<__type26>::type> __type27;
      typedef decltype(pythonic::operator_::neg(std::declval<__type26>())) __type29;
      typedef pythonic::types::list<typename std::remove_reference<__type29>::type> __type30;
      typedef typename __combined<__type27,__type30>::type __type31;
      typedef typename pythonic::lazy<__type31>::type __type32;
      typedef __type32 __type33;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type33>::type::iterator>::value_type>::type __type34;
      typedef typename __combined<__type25,__type34>::type __type35;
      typedef __type35 __type36;
      typedef decltype(pythonic::operator_::add(std::declval<__type36>(), std::declval<__type4>())) __type37;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::len{})>::type>::type __type38;
      typedef decltype(std::declval<__type38>()(std::declval<__type18>())) __type40;
      typedef decltype(pythonic::operator_::sub(std::declval<__type40>(), std::declval<__type37>())) __type41;
      typedef typename pythonic::lazy<__type41>::type __type42;
      typedef __type42 __type43;
      typedef decltype(std::declval<__type20>()(std::declval<__type37>(), std::declval<__type43>())) __type44;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type44>::type::iterator>::value_type>::type __type45;
      typedef __type45 __type46;
      typedef decltype(std::declval<__type19>()[std::declval<__type46>()]) __type47;
      typedef container<typename std::remove_reference<__type47>::type> __type48;
      typedef typename __combined<__type17,__type48>::type __type49;
      typedef typename pythonic::lazy<__type47>::type __type50;
      typedef __type50 __type51;
      typedef __type49 __type53;
      typedef decltype(pythonic::types::as_const(std::declval<__type53>())) __type54;
      typedef pythonic::types::list<typename std::remove_reference<__type4>::type> __type56;
      typedef typename pythonic::lazy<__type56>::type __type57;
      typedef __type57 __type58;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type58>::type::iterator>::value_type>::type __type59;
      typedef __type59 __type60;
      typedef decltype(pythonic::operator_::add(std::declval<__type46>(), std::declval<__type60>())) __type61;
      typedef decltype(std::declval<__type54>()[std::declval<__type61>()]) __type62;
      typedef decltype(pythonic::operator_::mul(std::declval<__type7>(), std::declval<__type62>())) __type63;
      typedef decltype(pythonic::operator_::add(std::declval<__type51>(), std::declval<__type63>())) __type64;
      typedef indexable<__type64> __type65;
      typedef container<typename std::remove_reference<__type4>::type> __type66;
      typedef typename __combined<__type12,__type65,__type66>::type __type67;
      typedef typename pythonic::assignable<__type67>::type __type68;
      typedef __type34 __type78;
      typedef decltype(pythonic::operator_::add(std::declval<__type46>(), std::declval<__type78>())) __type79;
      typedef decltype(std::declval<__type54>()[std::declval<__type79>()]) __type80;
      typedef decltype(pythonic::operator_::mul(std::declval<__type7>(), std::declval<__type80>())) __type81;
      typedef decltype(pythonic::operator_::add(std::declval<__type51>(), std::declval<__type81>())) __type82;
      typedef indexable<__type82> __type83;
      typedef typename __combined<__type12,__type83,__type66>::type __type84;
      typedef typename pythonic::assignable<__type84>::type __type85;
      typedef typename pythonic::assignable<__type35>::type __type86;
      typedef typename pythonic::assignable<__type49>::type __type87;
      typedef typename pythonic::assignable<__type56>::type __type88;
      typedef typename pythonic::assignable<__type31>::type __type89;
      typedef typename pythonic::lazy<__type32>::type __type90;
      typename pythonic::assignable_noescape<decltype(pythonic::operator_::add(num_classes, 1L))>::type num_cols_adjacency = pythonic::operator_::add(num_classes, 1L);
      __type68 horizontal_adjacency_arr = pythonic::numpy::functor::zeros{}(pythonic::numpy::functor::square{}(num_cols_adjacency), ADJ_ARR_DTYPE()());
      __type85 vertical_adjacency_arr = pythonic::numpy::functor::zeros{}(pythonic::numpy::functor::square{}(num_cols_adjacency), ADJ_ARR_DTYPE()());
      __type86 num_cols_pixel = std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, padded_arr)));
      __type87 flat_arr = pythonic::numpy::functor::ravel{}(padded_arr);
      typename pythonic::lazy<decltype(__type88({1L, -1L}))>::type horizontal_neighbors = __type88({1L, -1L});
      __type90 vertical_neighbors = __type89({num_cols_pixel, pythonic::operator_::neg(num_cols_pixel)});
      typename pythonic::lazy<decltype(pythonic::operator_::sub(pythonic::builtins::functor::len{}(flat_arr), pythonic::operator_::add(num_cols_pixel, 1L)))>::type end = pythonic::operator_::sub(pythonic::builtins::functor::len{}(flat_arr), pythonic::operator_::add(num_cols_pixel, 1L));
      {
        long  __target140629636323824 = end;
        for (long  i=pythonic::operator_::add(num_cols_pixel, 1L); i < __target140629636323824; i += 1L)
        {
          typename pythonic::lazy<decltype(pythonic::types::as_const(flat_arr).fast(i))>::type class_i = pythonic::types::as_const(flat_arr).fast(i);
          {
            for (auto&& neighbor: horizontal_neighbors)
            {
              pythonic::types::as_const(horizontal_adjacency_arr)[pythonic::operator_::add(class_i, pythonic::operator_::mul(num_cols_adjacency, pythonic::types::as_const(flat_arr)[pythonic::operator_::add(i, neighbor)]))] += 1L;
            }
          }
          {
            for (auto&& neighbor_: vertical_neighbors)
            {
              pythonic::types::as_const(vertical_adjacency_arr)[pythonic::operator_::add(class_i, pythonic::operator_::mul(num_cols_adjacency, pythonic::types::as_const(flat_arr)[pythonic::operator_::add(i, neighbor_)]))] += 1L;
            }
          }
        }
      }
      return pythonic::numpy::ndarray::functor::reshape{}(pythonic::numpy::functor::stack{}(pythonic::types::make_tuple(horizontal_adjacency_arr, vertical_adjacency_arr)), pythonic::types::make_tuple(2L, num_cols_adjacency, num_cols_adjacency));
    }
  }
}
#include <pythonic/python/exception_handler.hpp>
#ifdef ENABLE_PYTHON_MODULE
static PyObject* __transonic__ = to_python(__pythran_landscape::__transonic__()());
inline
typename __pythran_landscape::compute_adjacency_arr::type<pythonic::types::ndarray<npy_uint32,pythonic::types::pshape<long,long>>, long>::result_type compute_adjacency_arr0(pythonic::types::ndarray<npy_uint32,pythonic::types::pshape<long,long>>&& padded_arr, long&& num_classes) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_landscape::compute_adjacency_arr()(padded_arr, num_classes);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
inline
typename __pythran_landscape::compute_adjacency_arr::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<npy_uint32,pythonic::types::pshape<long,long>>>, long>::result_type compute_adjacency_arr1(pythonic::types::numpy_texpr<pythonic::types::ndarray<npy_uint32,pythonic::types::pshape<long,long>>>&& padded_arr, long&& num_classes) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_landscape::compute_adjacency_arr()(padded_arr, num_classes);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}

static PyObject *
__pythran_wrap_compute_adjacency_arr0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"padded_arr", "num_classes",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<npy_uint32,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<long>(args_obj[1]))
        return to_python(compute_adjacency_arr0(from_python<pythonic::types::ndarray<npy_uint32,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<long>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_adjacency_arr1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"padded_arr", "num_classes",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<npy_uint32,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<long>(args_obj[1]))
        return to_python(compute_adjacency_arr1(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<npy_uint32,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<long>(args_obj[1])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall_compute_adjacency_arr(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_compute_adjacency_arr0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_adjacency_arr1(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "compute_adjacency_arr", "\n""    - compute_adjacency_arr(uint32[:,:], int)", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "compute_adjacency_arr",
    (PyCFunction)__pythran_wrapall_compute_adjacency_arr,
    METH_VARARGS | METH_KEYWORDS,
    "Supported prototypes:\n""\n""    - compute_adjacency_arr(uint32[:,:], int)"},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "landscape",            /* m_name */
    "",         /* m_doc */
    -1,                  /* m_size */
    Methods,             /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
  };
#define PYTHRAN_RETURN return theModule
#define PYTHRAN_MODULE_INIT(s) PyInit_##s
#else
#define PYTHRAN_RETURN return
#define PYTHRAN_MODULE_INIT(s) init##s
#endif
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(landscape)(void)
#ifndef _WIN32
__attribute__ ((visibility("default")))
#if defined(GNUC) && !defined(__clang__)
__attribute__ ((externally_visible))
#endif
#endif
;
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(landscape)(void) {
    import_array()
    #if PY_MAJOR_VERSION >= 3
    PyObject* theModule = PyModule_Create(&moduledef);
    #else
    PyObject* theModule = Py_InitModule3("landscape",
                                         Methods,
                                         ""
    );
    #endif
    if(! theModule)
        PYTHRAN_RETURN;
    PyObject * theDoc = Py_BuildValue("(ss)",
                                      "0.14.0",
                                      "8c020df956122206354571a751342102e62061a2edc5ce5aff2daabbd8b872d9");
    if(! theDoc)
        PYTHRAN_RETURN;
    PyModule_AddObject(theModule,
                       "__pythran__",
                       theDoc);

    PyModule_AddObject(theModule, "__transonic__", __transonic__);
    PYTHRAN_RETURN;
}

#endif