#define OGDF_MEMORY_POOL_TS

#if 0 == 0 || !defined(NDEBUG)
	#define OGDF_DEBUG
#endif

#ifdef OGDF_DEBUG
/* #undef OGDF_HEAVY_DEBUG */
	#define OGDF_USE_ASSERT_EXCEPTIONS
	#ifdef OGDF_USE_ASSERT_EXCEPTIONS
		#define OGDF_FUNCTION_NAME __PRETTY_FUNCTION__
	#endif
	#if 0
		#define OGDF_USE_ASSERT_EXCEPTIONS_WITH_STACKTRACE
		#define BACKWARD_HAS_DW 0
		#define BACKWARD_HAS_BFD 0
		#define BACKWARD_HAS_UNWIND 0
	#endif
#endif

#define OGDF_DLL

//! The size of a pointer
//! @ingroup macros
#define OGDF_SIZEOF_POINTER 8

#define COIN_OSI_CLP

#if 0
	#define OSI_CLP
#endif

#define OGDF_SSE3_EXTENSIONS <pmmintrin.h>
/* #undef OGDF_HAS_LINUX_CPU_MACROS */
/* #undef OGDF_HAS_MALLINFO2 */
/* #undef OGDF_INCLUDE_CGAL */
