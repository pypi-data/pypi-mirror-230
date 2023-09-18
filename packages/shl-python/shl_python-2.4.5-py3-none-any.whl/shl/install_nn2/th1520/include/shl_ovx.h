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

#ifndef INCLUDE_SHL_OVX_H_
#define INCLUDE_SHL_OVX_H_
#include "csi_nn.h"
#include "shl_utils.h"

int shl_ovx_conv2d(struct csinn_tensor *input, struct csinn_tensor *output,
                   struct csinn_tensor *kernel, struct csinn_tensor *bias,
                   struct csinn_conv2d_params *params);

int shl_ovx_depthwise_conv2d(struct csinn_tensor *input, struct csinn_tensor *output,
                             struct csinn_tensor *kernel, struct csinn_tensor *bias,
                             struct csinn_conv2d_params *params);

int shl_ovx_group_conv2d(struct csinn_tensor *input, struct csinn_tensor *output,
                         struct csinn_tensor *kernel, struct csinn_tensor *bias,
                         struct csinn_conv2d_params *params);

int shl_ovx_conv2d_relu(struct csinn_tensor *input, struct csinn_tensor *output,
                        struct csinn_tensor *kernel, struct csinn_tensor *bias,
                        struct csinn_conv2d_params *params);

int shl_ovx_deconv2d(struct csinn_tensor *input, struct csinn_tensor *output,
                     struct csinn_tensor *kernel, struct csinn_tensor *bias,
                     struct csinn_conv2d_params *params);

int shl_ovx_depthwise_deconv2d(struct csinn_tensor *input, struct csinn_tensor *output,
                               struct csinn_tensor *kernel, struct csinn_tensor *bias,
                               struct csinn_conv2d_params *params);

int shl_ovx_fullyconnected(struct csinn_tensor *input, struct csinn_tensor *output,
                           struct csinn_tensor *weights, struct csinn_tensor *bias,
                           struct csinn_fc_params *params);

int shl_ovx_fullyconnected_relu(struct csinn_tensor *input, struct csinn_tensor *output,
                                struct csinn_tensor *weights, struct csinn_tensor *bias,
                                struct csinn_fc_params *params);

int shl_ovx_maxpool2d(struct csinn_tensor *input, struct csinn_tensor *output,
                      struct csinn_pool_params *params);

int shl_ovx_avgpool2d(struct csinn_tensor *input, struct csinn_tensor *output,
                      struct csinn_pool_params *params);

int shl_ovx_global_avgpool2d(struct csinn_tensor *input, struct csinn_tensor *output,
                             struct csinn_pool_params *params);

int shl_ovx_global_maxpool2d(struct csinn_tensor *input, struct csinn_tensor *output,
                             struct csinn_pool_params *params);

int shl_ovx_l2pool(struct csinn_tensor *input, struct csinn_tensor *output,
                   struct csinn_pool_params *params);

int shl_ovx_pool_with_argmax(struct csinn_tensor *input, struct csinn_tensor *output,
                             struct csinn_pool_params *params);

int shl_ovx_maxpool2d_locat(struct csinn_tensor *input, struct csinn_tensor *output,
                            struct csinn_pool_params *params);

int shl_ovx_unpooling(struct csinn_tensor *input, struct csinn_tensor *mask,
                      struct csinn_tensor *output, struct csinn_unpooling_params *params);

int shl_ovx_negative(struct csinn_tensor *input, struct csinn_tensor *output,
                     struct csinn_siso_params *params);

int shl_ovx_floor(struct csinn_tensor *input, struct csinn_tensor *output,
                  struct csinn_siso_params *params);

int shl_ovx_ceil(struct csinn_tensor *input, struct csinn_tensor *output,
                 struct csinn_siso_params *params);

int shl_ovx_abs(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_siso_params *params);

int shl_ovx_exp(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_siso_params *params);

int shl_ovx_log(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_siso_params *params);

int shl_ovx_sin(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_siso_params *params);

int shl_ovx_tanh(struct csinn_tensor *input, struct csinn_tensor *output,
                 struct csinn_siso_params *params);

int shl_ovx_sqrt(struct csinn_tensor *input, struct csinn_tensor *output,
                 struct csinn_siso_params *params);

int shl_ovx_rsqrt(struct csinn_tensor *input, struct csinn_tensor *output,
                  struct csinn_siso_params *params);

int shl_ovx_square(struct csinn_tensor *input, struct csinn_tensor *output,
                   struct csinn_siso_params *params);

int shl_ovx_sigmoid(struct csinn_tensor *input, struct csinn_tensor *output,
                    struct csinn_sigmoid_params *params);

int shl_ovx_elu(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_relu_params *params);

int shl_ovx_relu(struct csinn_tensor *input, struct csinn_tensor *output,
                 struct csinn_relu_params *params);

int shl_ovx_relu1(struct csinn_tensor *input, struct csinn_tensor *output,
                  struct csinn_relu_params *params);

int shl_ovx_relu6(struct csinn_tensor *input, struct csinn_tensor *output,
                  struct csinn_relu_params *params);

int shl_ovx_relun(struct csinn_tensor *input, struct csinn_tensor *output,
                  struct csinn_relu_params *params);

int shl_ovx_leaky_relu(struct csinn_tensor *input, struct csinn_tensor *output,
                       struct csinn_relu_params *params);

int shl_ovx_softrelu(struct csinn_tensor *input, struct csinn_tensor *output,
                     struct csinn_relu_params *params);

int shl_ovx_prelu(struct csinn_tensor *input, struct csinn_tensor *alpha,
                  struct csinn_tensor *output, struct csinn_prelu_params *params);

int shl_ovx_softplus(struct csinn_tensor *input, struct csinn_tensor *output,
                     struct csinn_siso_params *params);

int shl_ovx_softmax(struct csinn_tensor *input, struct csinn_tensor *output,
                    struct csinn_softmax_params *params);

int shl_ovx_log_softmax(struct csinn_tensor *input, struct csinn_tensor *output,
                        struct csinn_softmax_params *params);

int shl_ovx_batch_normalization(struct csinn_tensor *input, struct csinn_tensor *mean,
                                struct csinn_tensor *variance, struct csinn_tensor *gamma,
                                struct csinn_tensor *beta, struct csinn_tensor *output,
                                struct csinn_bn_params *params);

int shl_ovx_l2_normalization(struct csinn_tensor *input, struct csinn_tensor *output,
                             struct csinn_l2n_params *params);

int shl_ovx_lrn(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_lrn_params *params);

int shl_ovx_matmul(struct csinn_tensor *mat0, struct csinn_tensor *mat1,
                   struct csinn_tensor *output, struct csinn_matmul_params *params);

int shl_ovx_add(struct csinn_tensor *input0, struct csinn_tensor *input1,
                struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_sub(struct csinn_tensor *input0, struct csinn_tensor *input1,
                struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_mul(struct csinn_tensor *input0, struct csinn_tensor *input1,
                struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_div(struct csinn_tensor *input0, struct csinn_tensor *input1,
                struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_floor_divide(struct csinn_tensor *input0, struct csinn_tensor *input1,
                         struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_maximum(struct csinn_tensor *input0, struct csinn_tensor *input1,
                    struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_minimum(struct csinn_tensor *input0, struct csinn_tensor *input1,
                    struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_power(struct csinn_tensor *input0, struct csinn_tensor *input1,
                  struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_greater(struct csinn_tensor *input0, struct csinn_tensor *input1,
                    struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_less(struct csinn_tensor *input0, struct csinn_tensor *input1,
                 struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_equal(struct csinn_tensor *input0, struct csinn_tensor *input1,
                  struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_not_equal(struct csinn_tensor *input0, struct csinn_tensor *input1,
                      struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_greater_equal(struct csinn_tensor *input0, struct csinn_tensor *input1,
                          struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_less_equal(struct csinn_tensor *input0, struct csinn_tensor *input1,
                       struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_select(struct csinn_tensor *condition, struct csinn_tensor *input0,
                   struct csinn_tensor *input1, struct csinn_tensor *output,
                   struct csinn_diso_params *params);

int shl_ovx_and(struct csinn_tensor *input0, struct csinn_tensor *input1,
                struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_or(struct csinn_tensor *input0, struct csinn_tensor *input1,
               struct csinn_tensor *output, struct csinn_diso_params *params);

int shl_ovx_pad(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_pad_params *params);

int shl_ovx_resize(struct csinn_tensor *input, struct csinn_tensor *output,
                   struct csinn_resize_params *params);

int shl_ovx_concat(struct csinn_tensor **input, struct csinn_tensor *output,
                   struct csinn_concat_params *params);

int shl_ovx_proposal(struct csinn_tensor *cls_prob, struct csinn_tensor *bbox_pred,
                     struct csinn_tensor *im_info, struct csinn_tensor *output,
                     struct csinn_proposal_params *params);

int shl_ovx_psroipooling(struct csinn_tensor *data, struct csinn_tensor *rois,
                         struct csinn_tensor *output, struct csinn_psroipooling_params *params);

int shl_ovx_roipool(struct csinn_tensor *data, struct csinn_tensor *rois,
                    struct csinn_tensor *output, struct csinn_roi_pool_params *params);

int shl_ovx_roi_align(struct csinn_tensor *input, struct csinn_tensor *rois,
                      struct csinn_tensor *output, struct csinn_roi_align_params *params);

int shl_ovx_transpose(struct csinn_tensor *input, struct csinn_tensor *output,
                      struct csinn_transpose_params *params);

int shl_ovx_reshape(struct csinn_tensor *input, struct csinn_tensor *output,
                    struct csinn_reshape_params *params);

int shl_ovx_reshape_tail(struct csinn_tensor *input, struct csinn_tensor *output,
                         struct csinn_reshape_params *params);

int shl_ovx_shape(struct csinn_tensor *input, struct csinn_tensor *output,
                  struct csinn_shape_params *params);

int shl_ovx_expand_dims_f32(struct csinn_tensor *input, struct csinn_tensor *output,
                            struct csinn_expand_dims_params *params);

int shl_ovx_expand_dims_u8(struct csinn_tensor *input, struct csinn_tensor *output,
                           struct csinn_expand_dims_params *params);

int shl_ovx_reverse(struct csinn_tensor *input, struct csinn_tensor *output,
                    struct csinn_reverse_params *params);

int shl_ovx_flatten(struct csinn_tensor *input, struct csinn_tensor *output,
                    struct csinn_flatten_params *params);

int shl_ovx_flatten_tail(struct csinn_tensor *input, struct csinn_tensor *output,
                         struct csinn_flatten_params *params);

int shl_ovx_crop(struct csinn_tensor *input, struct csinn_tensor *output,
                 struct csinn_crop_params *params);

int shl_ovx_slice(struct csinn_tensor *input, struct csinn_tensor *output,
                  struct csinn_slice_params *params);

int shl_ovx_slice_tail(struct csinn_tensor *input, struct csinn_tensor *output,
                       struct csinn_slice_params *params);

int shl_ovx_strided_slice(struct csinn_tensor *input, struct csinn_tensor *output,
                          struct csinn_strided_slice_params *params);

int shl_ovx_split(struct csinn_tensor *input, struct csinn_tensor **output,
                  struct csinn_split_params *params);

int shl_ovx_stack(struct csinn_tensor **inputs, struct csinn_tensor *output,
                  struct csinn_stack_params *params);

int shl_ovx_tile(struct csinn_tensor *inputs, struct csinn_tensor *output,
                 struct csinn_tile_params *params);

int shl_ovx_arange(struct csinn_tensor *output, struct csinn_arange_params *params);

int shl_ovx_where(struct csinn_tensor *condition, struct csinn_tensor *x, struct csinn_tensor *y,
                  struct csinn_tensor *output, struct csinn_where_params *params);

int shl_ovx_unstack(struct csinn_tensor *input, struct csinn_tensor **outputs,
                    struct csinn_unstack_params *params);

int shl_ovx_gather(struct csinn_tensor *input, struct csinn_tensor *indices,
                   struct csinn_tensor *output, struct csinn_gather_params *params);

int shl_ovx_gather_nd(struct csinn_tensor *input, struct csinn_tensor *indices,
                      struct csinn_tensor *output, struct csinn_gather_nd_params *params);

int shl_ovx_squeeze(struct csinn_tensor *input, struct csinn_tensor *output,
                    struct csinn_squeeze_params *params);

int shl_ovx_squeeze_tail(struct csinn_tensor *input, struct csinn_tensor *output,
                         struct csinn_squeeze_params *params);

int shl_ovx_ndarray_size(struct csinn_tensor *input, struct csinn_tensor *output,
                         struct csinn_ndarray_size_params *params);

int shl_ovx_space_to_batch(struct csinn_tensor *input, struct csinn_tensor *output,
                           struct csinn_space_to_batch_params *params);

int shl_ovx_batch_to_space(struct csinn_tensor *input, struct csinn_tensor *output,
                           struct csinn_batch_to_space_params *params);

int shl_ovx_space_to_depth(struct csinn_tensor *input, struct csinn_tensor *output,
                           struct csinn_space_to_depth_params *params);

int shl_ovx_depth_to_space(struct csinn_tensor *input, struct csinn_tensor *output,
                           struct csinn_depth_to_space_params *params);

int shl_ovx_one_hot(struct csinn_tensor *input, struct csinn_tensor *output,
                    struct csinn_one_hot_params *params);

int shl_ovx_sequence_mask(struct csinn_tensor *input0, struct csinn_tensor *input1,
                          struct csinn_tensor *output, struct csinn_sequence_mask_params *params);

int shl_ovx_im2col(struct csinn_tensor *input, struct csinn_tensor *output,
                   struct csinn_tensor *kernel, struct csinn_im2col_params *params);

int shl_ovx_col2im(struct csinn_tensor *input, struct csinn_tensor *output,
                   struct csinn_tensor *kernel, struct csinn_col2im_params *params);

int shl_ovx_sum(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_reduce_params *params);

int shl_ovx_mean(struct csinn_tensor *input, struct csinn_tensor *output,
                 struct csinn_reduce_params *params);

int shl_ovx_max(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_reduce_params *params);

int shl_ovx_min(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_reduce_params *params);

int shl_ovx_prod(struct csinn_tensor *input, struct csinn_tensor *output,
                 struct csinn_reduce_params *params);

int shl_ovx_argmin(struct csinn_tensor *input, struct csinn_tensor *output,
                   struct csinn_reduce_params *params);

int shl_ovx_argmax(struct csinn_tensor *input, struct csinn_tensor *output,
                   struct csinn_reduce_params *params);

int shl_ovx_all(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_reduce_params *params);

int shl_ovx_any(struct csinn_tensor *input, struct csinn_tensor *output,
                struct csinn_reduce_params *params);

int shl_ovx_reorg(struct csinn_tensor *input, struct csinn_tensor *output,
                  struct csinn_reorg_params *params);

int shl_ovx_topk(struct csinn_tensor *input, struct csinn_tensor *output0,
                 struct csinn_tensor *output1, struct csinn_topk_params *params);

int shl_ovx_clip(struct csinn_tensor *input, struct csinn_tensor *output,
                 struct csinn_clip_params *params);

int shl_ovx_shuffle_channel(struct csinn_tensor *input, struct csinn_tensor *output,
                            struct csinn_shuffle_channel_params *params);

int32_t shl_get_ceil_mode_fix(int32_t input, int32_t kernel, int32_t stride, int32_t pad);

struct shl_ovx_target_data {
    void *graph;
};

void *shl_ovx_get_graph(struct csinn_session *sess);

uint8_t *shl_ovx_input_f32_to_u8(uint32_t idx, float *data, struct csinn_session *sess);
int shl_ovx_get_tensor(int index, struct csinn_tensor *ret, struct csinn_session *sess);
void shl_ovx_save_output(int index, const char *filename, struct csinn_session *sess);
void shl_ovx_show_top5(int index, struct csinn_session *sess);
void shl_ovx_set_graph_attribute(struct csinn_session *sess, int device_index);
int shl_ovx_get_device_number();
int shl_ovx_set_tensor(struct csinn_tensor *tensor, struct csinn_session *sess);

#endif  // INCLUDE_SHL_OVX_H_
