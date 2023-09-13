# -*- coding: utf-8 -*-

import os
import onnx
import time
from onnx import version_converter
from intelliw_onnx.common import correct_batch, operation
from intelliw_onnx.utils.logger import get_logger
from intelliw_onnx.convert.utils import modify_onnx2dynamic
from intelliw_onnx.convert.exit_code import *

logger = get_logger("CONVERT")


class ONNXConvert:
    valid_model_type = ['pytorch', 'paddle']

    def __init__(self, params):
        self.model_path = params.model_path
        self.model_type = params.model_type
        self.output = params.output
        self.op_set = params.op_set
        self.input_shape_list = params.input_shape.split('/')
        self.model_def_file = params.model_def_file
        self.model_class_name = params.model_class_name
        self.model_input_type = params.model_input_type
        self.model_weights_file = params.model_weights_file
        self.output_num = params.output_num
        self.keep_batch = params.keep_batch
        self.params_file = params.params_file
        self.input_shape = params.input_shape
        self.dynamic_batch = params.dynamic_batch

        self.simplify_model = params.simplify
        self.simplify_hw = params.simplify_hw
        self.force_simplify = params.force_simplify

        self.init_params()

    def init_params(self):

        if self.model_path is None or self.model_type is None or self.output is None:
            logger.error('WARNING: model_path/model_type/output COULD NOT be None')
            exit(-1)

        logger.info('model_path:{}, model_type:{}, output:{}'.format(self.model_path, self.model_type, self.output))
        logger.info('input_shape_list: {}'.format(self.input_shape_list))

        dynamic_paddle = False
        if self.model_type == 'paddle':
            from pd2onnx import is_dynamic_paddle
            dynamic_paddle = is_dynamic_paddle(self.input_shape_list, self.model_def_file, self.model_class_name,
                                               self.model_weights_file)

        can_ignore_model_path = False
        if self.model_type == 'pytorch':
            if self.model_weights_file != '':
                can_ignore_model_path = True

        if not dynamic_paddle and not can_ignore_model_path and not os.path.exists(self.model_path):
            logger.error('ERROR: {} is not exist'.format(self.model_path))
            exit(exit_code_model_not_exist)

        if self.model_type not in ONNXConvert.valid_model_type:
            logger.error('Valid mode type is {}'.format(ONNXConvert.valid_model_type))
            logger.error('ERROR: {} is not valid mode type'.format(self.model_type))
            exit(exit_code_invalid_model_type)

        if self.model_type == 'pytorch' and self.input_shape == '':
            logger.warning(
                'when converting pytorch model, you must tell the input shape(ex: --input_shape [1, 3, 32, 32]) \n'
                'also, you should provide model definition file')
            exit(exit_code_pytorch_no_input_shape)

    def convert(self):
        logger.info('begin convert..')
        begin_time = time.time()

        op_set_default = 11
        if self.op_set is not None and self.op_set < op_set_default:
            op_set_default = self.op_set

        if self.model_type == 'pytorch':
            from intelliw_onnx.convert.pt2onnx import convert_pt2onnx
            convert_pt2onnx(self.model_path, self.output, op_set_default, self.input_shape_list,
                            self.model_def_file, self.model_class_name, self.model_weights_file, self.output_num,
                            self.model_input_type,
                            self.keep_batch,
                            self.params_file)

        if self.model_type == 'paddle':
            from intelliw_onnx.convert.pd2onnx import convert_pd2onnx
            convert_pd2onnx(self.model_path, self.output, op_set_default, self.input_shape_list, self.model_def_file,
                            self.model_class_name,
                            self.model_input_type, self.model_weights_file)

        convert_end_time = time.time()
        logger.info('finish convert, it cost {} seconds'.format(convert_end_time - begin_time))

        model = onnx.load(self.output)

        if self.op_set is not None:
            if self.model_type == 'onnx':
                logger.info('ONNX, add_value_info_for_constants...')
                correct_batch.correct_batch_for_opset_convert(model)
                operation.add_value_info_for_constants(model)
                model = version_converter.convert_version(model, self.op_set)
            elif self.op_set != op_set_default:
                correct_batch.correct_batch_for_opset_convert(model)
                operation.add_value_info_for_constants(model)
                model = version_converter.convert_version(model, self.op_set)

            operation.eliminate_unused_input_initializer(model)

        new_model = model
        try:
            new_model = onnx.shape_inference.infer_shapes(model)
        except Exception as e:
            logger.error('The model cannot be inference for: %s' % e)
            new_model = model
        else:
            logger.info('Inference success')

        try:
            onnx.checker.check_model(new_model)
        except Exception as e:
            logger.warning('ignore warning(check_model), continue saving~, %s' % e)
        else:
            logger.info('Begin saving model...')

        if self.dynamic_batch == 1:
            logger.info('modify model to dynamic batch...')
            new_model = modify_onnx2dynamic(new_model)

        saving_end_time = time.time()

        logger.info('generate inference shape model, it cost {} seconds'.format(saving_end_time - convert_end_time))

        if self.simplify_model in (1, 2):
            from intelliw_onnx.convert.utils import model_simplify
            logger.info('begin doing simplify...')

            producer_name = new_model.producer_name
            producer_version = new_model.producer_version
            simplify_flag = '(simplified by macaConverter)'
            if simplify_flag not in producer_name and simplify_flag not in producer_version:
                new_model = model_simplify(new_model, self.simplify_model, self.simplify_hw)
            else:
                if self.force_simplify != 0:
                    new_model = model_simplify(new_model, self.force_simplify, self.simplify_hw)
                else:
                    logger.info('The model has been simplified by macaConverter, ignore this operation~~')

        delete = operation.eliminate_redundant_reshape(new_model)
        while delete:
            delete = operation.eliminate_redundant_reshape(new_model)

        operation.eliminate_unused_input_initializer(new_model)
        operation.eliminate_unused_constant_node(new_model)
        operation.remove_unused_initializer(new_model)

        onnx.save(new_model, self.output)

        end_time = time.time()

        logger.info('The whole progress cost {} seconds'.format(end_time - begin_time))
        logger.critical('Convert Success!')
