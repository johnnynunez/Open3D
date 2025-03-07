// ----------------------------------------------------------------------------
// -                        Open3D: www.open3d.org                            -
// ----------------------------------------------------------------------------
// Copyright (c) 2018-2024 www.open3d.org
// SPDX-License-Identifier: MIT
// ----------------------------------------------------------------------------

#pragma once

#include "pybind/open3d_pybind.h"

namespace open3d {
namespace t {
namespace pipelines {
namespace slam {

void pybind_slam_declarations(py::module &m);
void pybind_slam_definitions(py::module &m);

}  // namespace slam
}  // namespace pipelines
}  // namespace t
}  // namespace open3d
