cmake_minimum_required(VERSION 3.15)
project(gemmi_program_wheel)

# The actual source code will be fetched from git.
# We want to package this target:
set(target gemmi_prog)
# and use this options when building:
set(GEMMI_VERSION_INFO "from wheel")

include(FetchContent)
FetchContent_Declare(
  gemmi
  GIT_REPOSITORY https://github.com/project-gemmi/gemmi.git
  GIT_TAG        28b5670ec176c6df7dbb765aab0a1c12698a5d23 # v0.6.3
)

# We don't want to install all gemmi files.
# https://stackoverflow.com/questions/65527126/disable-install-for-fetchcontent
FetchContent_GetProperties(gemmi)
if (NOT gemmi_POPULATED)
  FetchContent_Populate(gemmi)
  add_subdirectory(${gemmi_SOURCE_DIR} ${gemmi_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()

# Because of EXCLUDE_FROM_ALL the build needs to be triggered
add_custom_target(trigger ALL DEPENDS ${target})

install(TARGETS ${target} DESTINATION ${SKBUILD_SCRIPTS_DIR})
