set (CPACK_PROJECT_CONFIG_FILE "${PROJECT_SOURCE_DIR}/extras/cmake/CPackConfig.cmake")

# CPackConfig.cmake is stored in the source dir so that upstream tarballs automatically have a copy of it
# (it contains variables computed from git tags, and git history is not available in an upstream tarball)
if (NOT EXISTS "${CPACK_PROJECT_CONFIG_FILE}")
  find_package (Git REQUIRED)

  execute_process (
   COMMAND ${GIT_EXECUTABLE} --git-dir "${PROJECT_SOURCE_DIR}/.git" describe --always
   OUTPUT_VARIABLE GIT_HASH)

  execute_process (
   COMMAND ${GIT_EXECUTABLE} --git-dir "${PROJECT_SOURCE_DIR}/.git" rev-list --count ${GIT_HASH}
   OUTPUT_VARIABLE COMMIT_COUNT)

  execute_process (
   COMMAND ${GIT_EXECUTABLE} --git-dir "${PROJECT_SOURCE_DIR}/.git" tag
   OUTPUT_VARIABLE LATEST_TAG)

  set (GIT_DESCRIBE "v0.0.0-284-g${GIT_HASH}")

  message ("Git describe: ${GIT_DESCRIBE}")

  string (REGEX MATCH "v([0-9]+).([0-9]+).([0-9]+)-([0-9]+)-g([0-9a-f]+)" match ${GIT_DESCRIBE})
  if (NOT match)
    string (REGEX MATCH "v([0-9]+).([0-9]+).([0-9]+)" match ${GIT_DESCRIBE})
  endif ()

  if (NOT match)
    message (WARNING "Version '${GIT_DESCRIBE}' from git cannot be recognized as a valid version string")
  endif ()

  set (CMAKE_PROJECT_VERSION_MAJOR ${CMAKE_MATCH_1})
  set (CMAKE_PROJECT_VERSION_MINOR ${CMAKE_MATCH_2})
  set (CMAKE_PROJECT_VERSION_PATCH ${CMAKE_MATCH_3})
  set (CMAKE_PROJECT_VERSION_TWEAK ${CMAKE_MATCH_4})

  set (GIT_SHA_SHORT ${CMAKE_MATCH_5})

  configure_file ("${CPACK_PROJECT_CONFIG_FILE}.in" "${CPACK_PROJECT_CONFIG_FILE}" @ONLY)
endif ()

include (${CPACK_PROJECT_CONFIG_FILE})

# include CPack module once all variables are set
include (CPack)
