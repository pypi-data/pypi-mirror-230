#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "COIN" for configuration "Debug"
set_property(TARGET COIN APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(COIN PROPERTIES
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/libCOIN.so"
  IMPORTED_SONAME_DEBUG "libCOIN.so"
  )

list(APPEND _cmake_import_check_targets COIN )
list(APPEND _cmake_import_check_files_for_COIN "${_IMPORT_PREFIX}/lib/libCOIN.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
