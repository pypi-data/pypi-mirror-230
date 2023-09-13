import os
import sys
import importlib
import importlib.util
import numpy as np
from intelliw_onnx.utils.logger import get_logger

logger = get_logger("CONVERT")

try:
    import torch
except Exception as e:
    logger.error(
        f"\033[33mError: {e}, Please install torch(pip install torch)\033[0m")
    sys.exit(-1)

try:
    import torchvision
except Exception as e:
    logger.warning(
        f"\033[33mWaring: {e}, If you need torchvision, please install it (pip install torchvision)\033[0m")


def convert_to_np_type(data_type):
    types = {
        'float': np.float32,
        'float32': np.float32,
        'uint8': np.uint8,
        'int8': np.int8,
        'uint16': np.uint16,
        'int16': np.int16,
        'int32': np.int32,
        'int64': np.int64,
        'string': np.object_,
        'bool': np.bool_,
        'float16': np.float16,
        'float64': np.float64,
        'uint32': np.uint32,
        'uint64': np.uint64,
        'complex64': np.complex64,
        'complex': np.complex_,
        'null': ""
    }

    return types.get(data_type, np.float32)


def check_module(module_name):
    """
    Checks if module can be imported without actually
    importing it
    """
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        logger.warn("Module: {} not found".format(module_name))
        return None
    else:
        logger.info("Module: {} can be imported".format(module_name))
        return module_spec


def set_module(model_def_file):
    if model_def_file == "":
        logger.error('Can not find model_def_file: {}'.format(model_def_file))
        exit(-1)
    # 把整个存放定义文件的目录加进系统变量中
    directory_path = os.path.dirname(os.path.abspath(model_def_file))
    sys.path.append(directory_path)


def find_module(model_class_name, model_def_file):
    if model_class_name:
        if '.' in model_class_name:
            n = model_class_name.rindex('.')
            target_module = model_class_name[:n]
            model_class_name = model_class_name.split('.')[-1]
        else:
            target_module = model_def_file.split('/')[-1]
            target_module = target_module.split('.')[-2]
    else:
        logger.error('Can not find model_class_name: {}'.format(model_class_name))
        exit(-1)

    module_find = check_module(target_module)
    if module_find is not None:
        logger.info('get module: {}'.format(module_find))
        module = importlib.import_module(target_module)

        cls = getattr(module, model_class_name, None)

        if cls is not None:
            return cls
        else:
            logger.error('There is no {} in {}'.format(model_class_name, model_def_file))
            exit(-1)
    else:
        logger.info('Can not find {}'.format(model_def_file))
        exit(-1)


def get_params(params_file):
    params = {}
    if params_file != '':
        params_file_module, _ = os.path.basename(params_file).split('.')
        module_find = check_module(params_file_module)
        if module_find is not None:
            logger.info('get module: {}'.format(module_find))
            module = importlib.import_module(params_file_module)
            obj = getattr(module, 'param_dict', None)
            if obj is not None:
                params = obj
            else:
                logger.error('Cannot get params[param_dict] from file: {}'.format(params_file))
                sys.exit(-1)
        else:
            logger.error('Cannot load params file: {}'.format(params_file))
            sys.exit(-1)
    return params


def format_input_type(model_input_type, input_shape_list, output_num):
    input_type_list = []
    if model_input_type != '':
        input_type_list = model_input_type.split(',')

    logger.info('got input_type_list: {}'.format(input_type_list))

    for idx, input_shape in enumerate(input_shape_list):
        input_shape = input_shape.strip('[').strip(']').split(',')
        input_shape_list[idx] = [int(s) for s in input_shape]

    logger.info('got input_shape_list: {}'.format(input_shape_list))
    if len(input_type_list) > 0 and len(input_type_list) != len(input_shape_list):
        logger.error('Error: len of input_type_list != len of input_shape_list')
        sys.exit(-1)

    input_tensor_list = []
    input_name_list = []
    output_name_list = []

    for i in range(output_num):
        if output_num == 1:
            output_name = 'output'
        else:
            output_name = 'output_' + str(i)
        output_name_list.append(output_name)

    for idx, input_shape in enumerate(input_shape_list):
        data_type = np.float32
        if len(input_type_list) > 0:
            data_type = convert_to_np_type(input_type_list[idx])
            logger.info('get data_type: {}'.format(data_type))

        data_array = np.array(np.random.random(input_shape), dtype=data_type)
        input_tensor_list.append(torch.from_numpy(data_array))

        if len(input_shape_list) == 1:
            input_name = 'input'
        else:
            input_name = 'input_' + str(idx)
        input_name_list.append(input_name)

    input_tensor_tuple = tuple(input_tensor_list)

    logger.info('input_name_list: {}, output_name_list: {}'.format(input_name_list, output_name_list))
    return input_name_list, input_tensor_tuple, output_name_list


def convert_pt2onnx(model_path, output, op_set, input_shape_list,
                    model_def_file, model_class_name, model_weights_file, output_num,
                    model_input_type, keep_batch, params_file):
    set_module(model_def_file)
    """
    :argument
    """

    params = get_params(params_file)

    input_name_list, input_tensor_tuple, output_name_list = format_input_type(
        model_input_type, input_shape_list, output_num
    )

    dynamic_axes_dict = {}
    if keep_batch == 0:
        for input_name in input_name_list:
            dynamic_axes_dict[input_name] = {0: '-1'}

        for output_name in output_name_list:
            dynamic_axes_dict[output_name] = {0: '-1'}

    cls = find_module(model_class_name, model_def_file)

    setattr(sys.modules['__main__'], model_class_name, cls)
    if len(params) > 0:
        m = cls(**params)
    else:
        m = cls()

    if model_weights_file == '':
        m = torch.load(model_path, map_location=torch.device('cpu'))
    else:
        m.load_state_dict(torch.load(model_weights_file, map_location=torch.device('cpu')))

    try:
        m = m.cpu()  # cuda()
    except AttributeError as ae:
        logger.error(
            f"\nError msg {ae}, \nMaybe the model file is not a model file but a model weight file\n"
            f"try to use argument model_weights_file and set model_path = ''")
        exit(-1)

    torch.onnx.export(
        m,
        input_tensor_tuple,  # x,
        output,
        opset_version=op_set,
        do_constant_folding=True,  # 是否执行常量折叠优化
        input_names=input_name_list,  # ["input"],    # 模型输入名
        output_names=output_name_list,  # ["output"],  # 模型输出名
        dynamic_axes=dynamic_axes_dict  # {'input':{0:'-1'}, 'output':{0:'-1'}}
    )
