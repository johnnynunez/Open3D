include(FetchContent)

set(filament_LIBRARIES filameshio filament filaflat filabridge geometry backend bluegl bluevk ibl image ktxreader meshoptimizer smol-v utils vkshaders)

if (FILAMENT_PRECOMPILED_ROOT)
    if (EXISTS "${FILAMENT_PRECOMPILED_ROOT}")
        set(FILAMENT_ROOT "${FILAMENT_PRECOMPILED_ROOT}")
    else()
        message(FATAL_ERROR "Filament binaries not found in ${FILAMENT_PRECOMPILED_ROOT}")
    endif()
else()
    # Locate byproducts
    set(lib_dir lib)
    # Setup download links
    if(WIN32)
        set(FILAMENT_URL https://github.com/google/filament/releases/download/v1.62.0/filament-v1.62.0-windows.tgz)
        set(FILAMENT_SHA256 fac5de9542a7d8b101cb80da3f138a31e24ab31dd42d37420d96969b6a8b47da)
        if (STATIC_WINDOWS_RUNTIME)
            string(APPEND lib_dir /x86_64/mt)
        else()
            string(APPEND lib_dir /x86_64/md)
        endif()
    elseif(APPLE)
        set(FILAMENT_URL https://github.com/google/filament/releases/download/v1.62.0/filament-v1.62.0-mac.tgz)
        set(FILAMENT_SHA256 9a5fa38bcd0bdcec47ef91c54e2701c42f0562a48ce10b9f67f6c2c957028885)
    else()
        set(FILAMENT_URL
                https://github.com/google/filament/releases/download/v1.62.0/filament-v1.62.0-linux.tgz)
        set(FILAMENT_SHA256 bd7cfe8daead2cff5ff85533e1d14130ebf65aa6d335d761f89f8a12edb671cc)
        message(STATUS "GLIBC version ${glibc_version} found: Using "
                "Google Filament binary.")
    endif()

    set(lib_byproducts ${filament_LIBRARIES})
    list(TRANSFORM lib_byproducts PREPEND <SOURCE_DIR>/${lib_dir}/${CMAKE_STATIC_LIBRARY_PREFIX})
    list(TRANSFORM lib_byproducts APPEND ${CMAKE_STATIC_LIBRARY_SUFFIX})
    message(STATUS "Filament byproducts: ${lib_byproducts}")

    if(WIN32)
        set(lib_byproducts_debug ${filament_LIBRARIES})
        list(TRANSFORM lib_byproducts_debug PREPEND <SOURCE_DIR>/${lib_dir}d/${CMAKE_STATIC_LIBRARY_PREFIX})
        list(TRANSFORM lib_byproducts_debug APPEND ${CMAKE_STATIC_LIBRARY_SUFFIX})
        list(APPEND lib_byproducts ${lib_byproducts_debug})
    endif()

    # ExternalProject_Add happens at build time.
    ExternalProject_Add(
            ext_filament
            PREFIX filament
            URL ${FILAMENT_URL}
            URL_HASH SHA256=${FILAMENT_SHA256}
            DOWNLOAD_DIR "${OPEN3D_THIRD_PARTY_DOWNLOAD_DIR}/filament"
            UPDATE_COMMAND ""
            CONFIGURE_COMMAND ""
            BUILD_IN_SOURCE ON
            BUILD_COMMAND ""
            INSTALL_COMMAND ""
            BUILD_BYPRODUCTS ${lib_byproducts}
    )
    ExternalProject_Get_Property(ext_filament SOURCE_DIR)
    message(STATUS "Filament source dir is ${SOURCE_DIR}")
    set(FILAMENT_ROOT ${SOURCE_DIR})
endif()

message(STATUS "Filament is located at ${FILAMENT_ROOT}")