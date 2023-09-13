import copy
import sys

import onnx

import numpy as np
from intelliw_onnx.common import values
from intelliw_onnx.common import correct_batch
from intelliw_onnx.convert.exit_code import *

from intelliw_onnx.utils.logger import get_logger

logger = get_logger("CONVERT")


def modify_onnx2dynamic(onnx_model):
    for idx in range(len(onnx_model.graph.input)):
        if len(onnx_model.graph.input[idx].type.tensor_type.shape.dim) > 0:
            dim_proto_input = onnx_model.graph.input[idx].type.tensor_type.shape.dim[0]
            # dim_proto_input.dim_param = 'bs'
            dim_proto_input.dim_value = -1

    for idx in range(len(onnx_model.graph.value_info)):
        if len(onnx_model.graph.value_info[idx].type.tensor_type.shape.dim) > 0:
            logger.debug('value info name: {}'.format(onnx_model.graph.value_info[idx].name))
            dim_proto_input = onnx_model.graph.value_info[idx].type.tensor_type.shape.dim[0]
            # dim_proto_input.dim_param = 'bs'
            dim_proto_input.dim_value = -1

    for idx in range(len(onnx_model.graph.output)):
        if len(onnx_model.graph.output[idx].type.tensor_type.shape.dim):
            dim_proto_output = onnx_model.graph.output[idx].type.tensor_type.shape.dim[0]
            # dim_proto_output.dim_param = 'bs'
            dim_proto_output.dim_value = -1

    # for Reshape
    reshape_param = []
    for node_id, node in enumerate(onnx_model.graph.node):
        # print(node_id, ", name:", node.name, ", input:", node.input, ", output:", node.output,  \
        #         ", op:", node.op_type, ', len(input):', len(node.input))
        if node.op_type == 'Reshape':
            logger.debug('Reshape, input: {}'.format(node.input))
            if node.input[1] not in reshape_param:
                reshape_param.append(node.input[1])

    for n in reshape_param:
        for init in onnx_model.graph.initializer:
            logger.info('loop init.name: {}'.format(init.name))
            if n == init.name:
                logger.info('got it in initializer: {} {}'.format(n, init.int64_data))
                # init.int64_data[0] = -1
                dtype = init.data_type
                np_dtype = correct_batch.convert_ort_type_2_np(dtype)
                if init.raw_data:
                    params_list = np.fromstring(init.raw_data, dtype=np_dtype)
                    logger.debug('len(params_list): {}'.format(len(params_list)))
                    adjust = True
                    for val in params_list:
                        if val == -1:
                            adjust = False

                    if adjust and params_list[0] != -1:
                        params_list[0] = -1
                        init.raw_data = params_list.tostring()
                else:
                    data_list = correct_batch.get_data_list(dtype, init)
                    adjust = True
                    logger.debug('len(data_list): {}'.format(len(data_list)))

                    for val in data_list:
                        if val == -1:
                            adjust = False

                    if adjust and len(data_list) > 0 and data_list[0] != -1:
                        data_list[0] = -1

    # for constant node
    for n in reshape_param:
        for node in onnx_model.graph.node:
            if node.op_type == 'Constant':
                if node.output[0] == n:
                    logger.info('got constant output: {}'.format(node.output))
                    attributes = node.attribute
                    for attr in attributes:
                        if attr.name == 'value':
                            v = values.get_tensor_value(attr.t)
                            # print('got type v:', type(v))
                            adjust = True
                            for val in v:
                                if val == -1:
                                    adjust = False
                                    break

                            if adjust:
                                v[0] = -1
                                vv = [v_ for v_ in v]
                                # print('-----new vv:', vv, type(vv))
                                if isinstance(v, np.ndarray):
                                    values.set_tensor_value(attr.t, v)
                                else:
                                    values.set_tensor_value(attr.t, vv)

    # onnx_model = onnx.shape_inference.infer_shapes(onnx_model)
    try:
        onnx.checker.check_model(onnx_model)
    except onnx.checker.ValidationError as e:
        print('*** The model cannot be modified for: %s' % e)
        if 'No Op registered for Mish' in str(e):
            logger.warning('ignore mish warning, continue saving~')
        else:
            logger.error('ERROR: check model failed in modify_onnx2dynamic')
            sys.exit(exit_code_check_modify_onnx2dynamic)
    else:
        logger.info('*** The model is modified!')

    return onnx_model


def model_simplify(onnx_model, simplify_model, simplify_hw):
    from onnxsim.onnx_simplifier import simplify
    # onnx_model = onnx.load(model_path)
    is_dynamic_input_shape = False

    init_list = []
    input_shapes_ = {}

    for init in onnx_model.graph.initializer:
        init_list.append(init.name)

    h = -1
    w = -1

    for input_ in onnx_model.graph.input:
        # print('graph_input_name:', input_.name)
        if input_.name not in init_list:
            if len(input_.type.tensor_type.shape.dim) > 0:
                input_shape = input_.type.tensor_type.shape.dim
                input_shape = [x.dim_value for x in input_shape]

                if len(input_shape) < 2:
                    continue

                h = input_shape[-2]
                w = input_shape[-1]

                if any(d == -1 or d == 0 for d in input_shape):
                    is_dynamic_input_shape = True
                    logger.info('The model input is dynamic, input: {} {}'.format(input_.name, input_shape))
                    input_shape[0] = 1
                    if simplify_hw != '':
                        hw_list = simplify_hw.split(',')
                        input_shape[-1] = int(hw_list[1])
                        input_shape[-2] = int(hw_list[0])
                        logger.debug('input_shape: {}'.format(input_shape))

                input_shapes_[input_.name] = input_shape
                logger.info('----- input_shapes_: {}'.format(input_shapes_))

    skip_constant_folding_ = False
    if h <= 0 or w <= 0:
        skip_constant_folding_ = True

    if simplify_model == 2:
        if is_dynamic_input_shape:
            model_simp, check = simplify(onnx_model, input_shapes=input_shapes_,
                                         skip_constant_folding=skip_constant_folding_)
            if simplify_hw == '':
                # correct_batch_for_opset_convert(model_simp)
                correct_output_shape(model_simp)
                try:
                    model_simp = reset_model_value_info(model_simp)
                except Exception as e:
                    logger.warning('Cannot do reset_value operation~ %s' % e)
        else:
            model_simp, check = simplify(onnx_model, dynamic_input_shape=False)
    else:
        model_simp, check = simplify(onnx_model, dynamic_input_shape=is_dynamic_input_shape,
                                     skip_constant_folding=skip_constant_folding_)

    # onnx.save(model_simp, model_path)
    if model_simp.producer_version != '':
        model_simp.producer_version = model_simp.producer_version + '(simplified by macaConverter)'
    else:
        model_simp.producer_name = model_simp.producer_name + '(simplified by macaConverter)'

    return model_simp


def correct_output_shape(model):
    for output in model.graph.output:
        if len(output.type.tensor_type.shape.dim) > 0:
            output_shape = output.type.tensor_type.shape.dim
            output_shape = [x.dim_value for x in output_shape]

            if any(d == -1 or d == 0 for d in output_shape):
                logger.info('The model output is dynamic, output: {} {}'.format(output.name, output_shape))
                output.type.tensor_type.shape.dim[0].dim_value = 1

    for output in model.graph.output:
        if len(output.type.tensor_type.shape.dim) > 0:
            output_shape = output.type.tensor_type.shape.dim
            output_shape = [x.dim_value for x in output_shape]
            logger.debug('The model output is dynamic, output_shape: {}'.format(output_shape))


def reset_model_value_info(model):
    model_bak = copy.deepcopy(model)

    del model_bak.graph.value_info[:]

    try:
        new_model = onnx.shape_inference.infer_shapes(model_bak)
        new_model = onnx.shape_inference.infer_shapes(new_model)
        return new_model
    except BaseException as e:
        logger.warning('reset_model_value_info, the model cannot be inference for: {}'.format(e))
        return model
