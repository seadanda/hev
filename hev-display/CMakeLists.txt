cmake_minimum_required (VERSION 3.1.0)

project (hev-display)

configure_file (
 ${PROJECT_SOURCE_DIR}/extras/cmake/cmake_uninstall.cmake.in
 ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake @ONLY)

add_custom_target (uninstall
 COMMAND ${CMAKE_COMMAND} -P "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake")

# Configure packaging
set (CPACK_PACKAGE_DESCRIPTION_SUMMARY "HEV native display")
set (CPACK_PACKAGE_VENDOR "CERN, Riga Technical University and University of Liverpool")
set (CPACK_PACKAGE_CONTACT "The High Energy Ventilator Project <https://hev.web.cern.ch/>")
set (CPACK_STRIP_FILES "hev-display")
set (CPACK_PACKAGE_EXECUTABLES "hev-display")

# Calculate version identifiers from git tags
include (${PROJECT_SOURCE_DIR}/extras/cmake/CPackGit.cmake)

add_definitions (-DVERSION="${CPACK_PACKAGE_VERSION}")

# Configure Qt
set (CMAKE_AUTOMOC ON)
set (CMAKE_AUTORCC ON)
set (CMAKE_AUTOUIC ON)

if (CMAKE_VERSION VERSION_LESS "3.7.0")
  set (CMAKE_INCLUDE_CURRENT_DIR ON)
endif ()

find_package (Qt5 5.12 COMPONENTS Core Quick QuickControls2 Svg Charts Network Concurrent LinguistTools REQUIRED)

set (SOURCES sources/main.cpp sources/datasource.cpp sources/localization.cpp)
set (RESOURCES assets/resources.qrc languages/translations.qrc)

set (TS_FILES 
        languages/translation-qml_en.ts 
        languages/translation-qml_es.ts 
        languages/translation-qml_fr.ts 
        languages/translation-qml_de.ts 
        languages/translation-qml_lv.ts 
        languages/translation-qml_it.ts 
        languages/translation-qml_sk.ts
        )

set_source_files_properties (${TS_FILES} PROPERTIES OUTPUT_LOCATION ${CMAKE_SOURCE_DIR}/languages)
qt5_add_translation (QM_FILES ${TS_FILES})

# Main executable
add_executable (hev-display
  ${SOURCES}
  ${RESOURCES}
  ${QM_FILES}
)

target_link_libraries (hev-display Qt5::Core Qt5::Quick Qt5::QuickControls2 Qt5::Svg Qt5::Charts Qt5::Network Qt5::Concurrent)

install (TARGETS hev-display RUNTIME DESTINATION bin)

# Raspbian-specific packaging
if (CPACK_SYSTEM_NAME MATCHES "raspbian.*")
  # QT5_BASEDIR must match the path Qt was compiled to use, RPATH adjustments do not help as
  # Qt will still look for plugins and qml modules in the location configured initially
  set (QT5_BASEDIR "/usr/local/qt5pi")
  get_target_property (qt5_core_location Qt5::Core LOCATION)
  get_filename_component (qt5_lib_dir ${qt5_core_location} DIRECTORY)
  file (GLOB qt5_sos "${qt5_lib_dir}/lib*.so*")
  foreach (qt5_so ${qt5_sos})
    install (FILES "${qt5_so}" DESTINATION "${QT5_BASEDIR}/lib")
  endforeach ()
  install (DIRECTORY "${qt5_lib_dir}/../plugins" DESTINATION "${QT5_BASEDIR}/")
  install (DIRECTORY "${qt5_lib_dir}/../qml" DESTINATION "${QT5_BASEDIR}/")
  # Not all libraries autodetect the host rpath, RPATH still required for libQt5Core and a few others
  set_target_properties (hev-display PROPERTIES INSTALL_RPATH "${QT5_BASEDIR}/lib:/opt/vc/lib:")
endif ()
