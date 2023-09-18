/*
 * Copyright (C) 2016-2023 T-Head Semiconductor Co., Ltd. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the License); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an AS IS BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef INCLUDE_SHL_C920V2_H_
#define INCLUDE_SHL_C920V2_H_

#include "csi_nn.h"
#include "shl_gref.h"
#include "shl_ref.h"
#include "shl_thead_rvv.h"

#ifdef __cplusplus
extern "C" {
#endif

/*********************************** initialization ***********************************/
int shl_c920v2_conv2d_init_fp32(struct csinn_tensor *input, struct csinn_tensor *output,
                                struct csinn_tensor *kernel, struct csinn_tensor *bias,
                                struct csinn_conv2d_params *params);
int shl_c920v2_conv2d_init_fp16(struct csinn_tensor *input, struct csinn_tensor *output,
                                struct csinn_tensor *kernel, struct csinn_tensor *bias,
                                struct csinn_conv2d_params *params);
int shl_c920v2_conv2d_init_int8(struct csinn_tensor *input, struct csinn_tensor *output,
                                struct csinn_tensor *kernel, struct csinn_tensor *bias,
                                struct csinn_conv2d_params *params);

#ifdef __cplusplus
}
#endif

#endif  // INCLUDE_SHL_C920V2_H_
