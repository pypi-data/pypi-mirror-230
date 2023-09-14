# SPDX-FileCopyrightText: 2012-2021 Istituto Italiano di Tecnologia (IIT)
# SPDX-License-Identifier: BSD-3-Clause

#[=======================================================================[.rst:
FindReadline
------------

Try to find GNU Readline, a library for easy editing of command lines.
Once done this will define the following variables::

 Readline_FOUND         - System has GNU Readline
 Readline_INCLUDE_DIRS  - GNU Readline include directory
 Readline_LIBRARIES     - GNU Readline libraries
 Readline_DEFINITIONS   - Additional compiler flags for GNU Readline
 Readline_VERSION       - GNU Readline version
 Readline_MAJOR_VERSION - GNU Readline major version
 Readline_MINOR_VERSION - GNU Readline minor version

Environment variables used to locate the GNU Readline library::

 READLINE_DIR - Readline root directory

Cached variables used to locate the GNU Readline library::

 Readline_INCLUDE_DIR - the Readline include directory
 Readline_LIBRARY_RELEASE - GNU Readline library (release)
 Readline_LIBRARY_DEBUG - GNU Readline library (debug)
#]=======================================================================]

include(SelectLibraryConfigurations)
include(FindPackageHandleStandardArgs)

# Include directories
find_path(Readline_INCLUDE_DIR
          NAMES readline/readline.h
          HINTS ENV Readline_DIR
          PATH_SUFFIXES include)
mark_as_advanced(Readline_INCLUDE_DIR)
set(Readline_INCLUDE_DIRS ${Readline_INCLUDE_DIR})


# Libraries
find_library(Readline_LIBRARY_RELEASE
             NAMES readline
             HINTS ENV Readline_DIR
             PATH_SUFFIXES lib)
find_library(Readline_LIBRARY_DEBUG
             NAMES readlined
             HINTS ENV Readline_DIR
             PATH_SUFFIXES lib)
mark_as_advanced(Readline_LIBRARY_RELEASE
                 READ_LIBRARY_DEBUG)
select_library_configurations(Readline)


# Version
set(Readline_VERSION Readline_VERSION-NOTFOUND)
if (Readline_INCLUDE_DIR)
  if(EXISTS "${Readline_INCLUDE_DIR}/readline/readline.h")
    file(STRINGS "${Readline_INCLUDE_DIR}/readline/readline.h" _Readline_HEADER_CONTENTS REGEX "#define RL_VERSION_[A-Z]+")
    string(REGEX REPLACE ".*#define RL_VERSION_MAJOR[ \t]+([0-9]+).*" "\\1" Readline_VERSION_MAJOR "${_Readline_HEADER_CONTENTS}")
    string(REGEX REPLACE ".*#define RL_VERSION_MINOR[ \t]+([0-9]+).*" "\\1" Readline_VERSION_MINOR "${_Readline_HEADER_CONTENTS}")
    set(Readline_VERSION ${Readline_VERSION_MAJOR}.${Readline_VERSION_MINOR})
    unset(_Readline_HEADER_CONTENTS)
  endif()
endif()


# Check required variables
find_package_handle_standard_args(Readline FOUND_VAR Readline_FOUND
                                           REQUIRED_VARS Readline_LIBRARY Readline_INCLUDE_DIR
                                           VERSION_VAR Readline_VERSION)

# Set package properties if FeatureSummary was included
if(COMMAND set_package_properties)
    set_package_properties(Readline PROPERTIES DESCRIPTION "A software library that provides line-editing and history capabilities"
                                               URL "http://cnswww.cns.cwru.edu/php/chet/readline/rltop.html")
endif()
