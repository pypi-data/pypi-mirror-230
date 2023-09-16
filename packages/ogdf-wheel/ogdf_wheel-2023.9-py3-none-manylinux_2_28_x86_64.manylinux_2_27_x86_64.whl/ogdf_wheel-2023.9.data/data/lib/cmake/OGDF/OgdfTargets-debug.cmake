#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "OGDF" for configuration "Debug"
set_property(TARGET OGDF APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(OGDF PROPERTIES
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/libOGDF.so"
  IMPORTED_SONAME_DEBUG "libOGDF.so"
  )

list(APPEND _cmake_import_check_targets OGDF )
list(APPEND _cmake_import_check_files_for_OGDF "${_IMPORT_PREFIX}/lib/libOGDF.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
