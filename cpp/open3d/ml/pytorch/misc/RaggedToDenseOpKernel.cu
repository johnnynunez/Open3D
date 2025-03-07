// ----------------------------------------------------------------------------
// -                        Open3D: www.open3d.org                            -
// ----------------------------------------------------------------------------
// Copyright (c) 2018-2024 www.open3d.org
// SPDX-License-Identifier: MIT
// ----------------------------------------------------------------------------
//

#include "ATen/cuda/CUDAContext.h"
#include "open3d/ml/impl/misc/RaggedToDense.cuh"
#include "open3d/ml/pytorch/TorchHelper.h"
#include "open3d/ml/pytorch/misc/RaggedToDenseOpKernel.h"
#include "torch/script.h"

template <class T>
torch::Tensor RaggedToDenseCUDA(const torch::Tensor& values,
                                const torch::Tensor& row_splits,
                                const int64_t out_col_size,
                                const torch::Tensor& default_value) {
    auto out_shape = values.sizes().vec();
    out_shape.erase(out_shape.begin());
    out_shape.insert(out_shape.begin(), {row_splits.size(0) - 1, out_col_size});
    auto device = values.device();
    torch::Tensor out = torch::empty(
            out_shape, torch::dtype(ToTorchDtype<T>()).device(device));

    auto stream = at::cuda::getCurrentCUDAStream();

    open3d::ml::impl::RaggedToDenseCUDA(
            stream, values.data_ptr<T>(), row_splits.data_ptr<int64_t>(),
            row_splits.size(0), out_col_size, default_value.data_ptr<T>(),
            default_value.numel(), out.data_ptr<T>());

    return out;
}

#define INSTANTIATE(T)                                                 \
    template torch::Tensor RaggedToDenseCUDA<T>(                       \
            const torch::Tensor&, const torch::Tensor&, const int64_t, \
            const torch::Tensor&);

INSTANTIATE(uint8_t)
INSTANTIATE(int8_t)
INSTANTIATE(int16_t)
INSTANTIATE(int32_t)
INSTANTIATE(int64_t)
INSTANTIATE(float)
INSTANTIATE(double)
