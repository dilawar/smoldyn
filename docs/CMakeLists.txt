cmake_minimum_required(VERSION 3.12)
project(smoldyn-doc LANGUAGES)

find_package(Python3 COMPONENTS Interpreter REQUIRED)

#
# A target to convert odt and tex files in documentations format to rst format
# convert ../documentation/Smoldyn/SmoldynUsersManual.odt to rst
#
set(USER_MANUAL_ODT
    ${CMAKE_CURRENT_SOURCE_DIR}/../documentation/Smoldyn/SmoldynUsersManual.odt)
set(USER_MANUAL_RST_AUTO
    ${CMAKE_CURRENT_SOURCE_DIR}/../docs/user/user_manual.rst)

add_custom_command(OUTPUT ${USER_MANUAL_RST_AUTO}
    COMMAND pandoc -f odt ${USER_MANUAL_ODT} -o ${USER_MANUAL_RST_AUTO}
    MAIN_DEPENDENCY ${USER_MANUAL_ODT}
    COMMENT "Converting ${USER_MANUAL_ODT} -> ${USER_MANUAL_RST_AUTO}"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    VERBATIM)
add_custom_target(gen_user_manual DEPENDS ${USER_MANUAL_RST_AUTO})

# install dependencies
add_custom_command(TARGET gen_user_manual PRE_BUILD
    COMMAND ${Python3_EXECUTABLE} -m pip install -r 
        ${CMAKE_CURRENT_SOURCE_DIR}/requirements.txt
    COMMENT "Installing dependencies." VERBATIM)

#
# Convert all tex files to rst 
# 
set(DOC_TEX_FILES 
    ${CMAKE_CURRENT_SOURCE_DIR}/../documentation/Smoldyn/LibsmoldynManual.tex
    ${CMAKE_CURRENT_SOURCE_DIR}/../documentation/Smoldyn/SmoldynCodeDoc.tex
    )
foreach(_tex_file ${DOC_TEX_FILES})
    get_filename_component(_name_file ${_tex_file} NAME_WE)
    set(_output_rst_file "${CMAKE_CURRENT_SOURCE_DIR}/developer/${_name_file}.rst")
    add_custom_command(OUTPUT ${_output_rst_file}
        COMMAND pandoc -f latex ${_tex_file} -o ${_output_rst_file}
        MAIN_DEPENDENCY ${_tex_file}
        COMMENT "  [doc] converting ${_tex_file} to ${_output_rst_file}"
        VERBATIM)
    add_custom_target(${_name_file} ALL DEPENDS ${_output_rst_file})
endforeach()



#
# This is based on an excellent tutorial by Sy Brand
# https://devblogs.microsoft.com/cppblog/clear-functional-c-documentation-with-sphinx-breathe-doxygen-cmake/
#
set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../cmake)

find_package(Perl REQUIRED)
find_package(Doxygen REQUIRED)
find_package(Sphinx REQUIRED)

# Find all the public headers
file(GLOB_RECURSE SMOLDYN_PUBLIC_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/../source/*.h)

# These are used in Doxygen.in file.
set(DOXYGEN_INPUT_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/../source/)
set(DOXYGEN_OUTPUT_DIR ${CMAKE_BINARY_DIR}/doxygen)
set(DOXYGEN_INDEX_FILE ${DOXYGEN_OUTPUT_DIR}/xml/index.xml)

set(DOXYGEN_IN ${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in)
set(DOXYGEN_OUT ${CMAKE_BINARY_DIR}/Doxyfile)
configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT})

# Only regenerate when headers and Doxyfile changes.
add_custom_command(OUTPUT ${DOXYGEN_INDEX_FILE}
    COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
    DEPENDS ${SMOLDYN_PUBLIC_HEADERS}
    MAIN_DEPENDENCY ${DOXYGEN_OUT} ${DOXYGEN_IN}
    COMMENT "Generating docs"
    VERBATIM)

# Nice named target so we can run the job easily
add_custom_target(Doxygen ALL DEPENDS ${DOXYGEN_INDEX_FILE})

set(SPHINX_SOURCE ${CMAKE_CURRENT_SOURCE_DIR})
set(SPHINX_BUILD ${CMAKE_BINARY_DIR}/sphinx)
set(SPHINX_INDEX_FILE ${SPHINX_BUILD}/index.html)

file(GLOB_RECURSE SMOLDYN_RST_SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/../docs/*.rst)
# Only regenerate Sphinx when:
# - Doxygen has rerun
# - Our doc files have been updated
# - The Sphinx config has been updated
add_custom_command(OUTPUT ${SPHINX_INDEX_FILE}
    COMMAND ${SPHINX_EXECUTABLE} -b html 
        # Tell Breathe where to find the Doxygen output
        -Dbreathe_projects.smoldyn=${DOXYGEN_OUTPUT_DIR}/xml 
        ${SPHINX_SOURCE} ${SPHINX_BUILD}
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    DEPENDS ${SMOLDYN_RST_SOURCES}
    # Other docs files you want to track should go here (or in some variable)
        ${CMAKE_CURRENT_SOURCE_DIR}/index.rst
    ${DOXYGEN_INDEX_FILE}
    MAIN_DEPENDENCY ${SPHINX_SOURCE}/conf.py
    COMMENT "Generating documentation with Sphinx")

# Generate doc using Sphinx and doxygen.
add_custom_target(docs ALL 
    DEPENDS _smoldyn gen_user_manual
    COMMAND READTHEDOCS=True ${SPHINX_EXECUTABLE} -b html
        ${SPHINX_SOURCE} ${SPHINX_BUILD}
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMENT "Generating documentation with Sphinx and doxygen")

# Nice named target so we can run the job easily
add_custom_target(Sphinx ALL DEPENDS ${SPHINX_INDEX_FILE})

##
## Convert example scripts to rst
##
#add_custom_command(TARGET docs PRE_BUILD
#    COMMAND sphinx-apidoc -o ${CMAKE_CURRENT_SOURCE_DIR}/examples
#        ${CMAKE_CURRENT_SOURCE_DIR}/../examples/S15_python
#    COMMENT "Generating rst files from example files"
#    VERBATIM)

# LiveHTML (for developer and document writer)
add_custom_target(doc_livehtml
    COMMAND sphinx-autobuild -p 0 -H 0.0.0.0 -B --delay 1 
        -b html
        ${SMOLDYN_DOC_SOURCE_DIR} ${CMAKE_BINARY_DIR}/livehtml
    COMMENT "Genrating live HTML"
    VERBATIM)

# Add an install target to install the docs
include(GNUInstallDirs)
install(DIRECTORY ${SPHINX_BUILD} DESTINATION ${CMAKE_INSTALL_DOCDIR})
