import importlib
import importlib.util
import os
import sys
import subprocess
from intelliw_onnx.utils.logger import get_logger

logger = get_logger("CONVERT")

try:
    import paddle
except Exception as e:
    logger.error(
        f"\033[33mError: {e}, Please install paddle(pip install paddlepaddle)\033[0m")
    sys.exit(-1)

paddle.disable_signal_handler()


def get_paddle_files(model_path):
    items = os.listdir(model_path)
    has_model = False
    has_params = False
    pd_model = ''
    pd_params = ''

    for f in items:
        if f.endswith(".pdmodel"):
            has_model = True
            pd_model = f
        elif f.endswith(".pdiparams"):
            has_params = True
            pd_params = f

        if has_model and has_params:
            if model_path.endswith("/"):
                pd_model = model_path + pd_model
                pd_params = model_path + pd_params
            else:
                pd_model = model_path + '/' + pd_model
                pd_params = model_path + '/' + pd_params

            logger.info('got pdmodel:{}, pdiparams:{}'.format(pd_model, pd_params))

            break

    return pd_model, pd_params


def convert_pd_static2onnx(model_path, output, op_set):
    try:
        subprocess.check_output(["paddle2onnx", "-v"])
    except Exception as e:
        logger.error(
            f"\033[33mError: {e}, Please install paddle2onnx(pip install paddle2onnx)\033[0m")
        sys.exit(-1)

    logger.info('Begin converting static paddle to onnx...')
    if model_path.startswith('./'):
        cwd = os.getcwd()
        model_path = cwd + model_path[1:]
    elif not model_path.startswith('/'):
        cwd = os.getcwd()
        model_path = cwd + '/' + model_path

    pd_model, pd_params = get_paddle_files(model_path)

    cmd = 'paddle2onnx --model_dir ' + model_path + ' --opset_version ' + str(op_set) + ' --save_file ' + output \
          + ' --model_filename ' + pd_model + ' --params_filename ' + pd_params

    logger.info('convert_paddle2onnx: {}'.format(cmd))

    os.system(cmd)


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
        logger.warn("Module: {} can be imported".format(module_name))
        return module_spec


def convert_pd_dynamic2onnx(model_path, output, op_set, input_shape_list,
                            model_def_file, model_class_name, model_input_type, model_weights_file):
    logger.info('Begin converting dynamic paddle to onnx...')

    if model_def_file != '':
        index = model_def_file.rindex('/')
        dir_path = model_def_file[:index]
        sys.path.append(dir_path)

    for idx, input_shape in enumerate(input_shape_list):
        input_shape = input_shape.strip('[').strip(']').split(',')
        input_shape_list[idx] = [int(s) for s in input_shape]

    logger.info('convert_pd_dynamic2onnx, got input_shape_list_int: {}'.format(input_shape_list))

    input_type_list = []
    if model_input_type != '':
        input_type_list = model_input_type.split(',')

    logger.info('convert_pd_dynamic2onnx, input_type_list: {}'.format(input_type_list))

    if len(input_type_list) > 0 and len(input_type_list) != len(input_shape_list):
        logger.error('Error, len of input_type_list != len of input_shape_list')
        sys.exit(-1)

    input_spec_list = []

    for idx, input_shape in enumerate(input_shape_list):
        data_type = 'float32'
        if len(input_type_list) > 0:
            data_type = input_type_list[idx]

        input_spec = paddle.static.InputSpec(shape=input_shape, dtype=data_type, name='input_' + str(idx))
        input_spec_list.append(input_spec)

    out = output.split('.onnx')[-2]
    logger.info('out is {}'.format(out))

    target_module = ''

    if '.' in model_class_name:
        n = model_class_name.rindex('.')
        target_module = model_class_name[:n]
        model_class_name = model_class_name.split('.')[-1]
    else:
        target_module = model_def_file.split('/')[-1]
        target_module = target_module.split('.')[-2]

    logger.info('convert_pd_dynamic2onnx, target_module: {}'.format(target_module))

    module_find = check_module(target_module)
    if module_find is not None:
        logger.info('----get module: {}'.format(module_find))
        module = importlib.import_module(target_module)
        cls = getattr(module, model_class_name, None)
        setattr(sys.modules['__main__'], model_class_name, cls)
        if cls is not None:
            model = cls()
            model.set_dict(paddle.load(model_weights_file))
            model.eval()
            paddle.onnx.export(model, out, input_spec=input_spec_list, opset_version=op_set)
        else:
            logger.warn('There is no {} in {}'.format(model_class_name, model_def_file))
    else:
        logger.warn('Can not find {}'.format(model_def_file))


def is_dynamic_paddle(input_shape_list, model_def_file, model_class_name, model_weights_file):
    if model_class_name != '' and '.' not in model_class_name:
        return input_shape_list != '' and model_def_file != '' and model_weights_file != ''
    elif model_class_name != '' and '.' in model_class_name:
        return input_shape_list != '' and model_weights_file != ''
    else:
        return False


def convert_pd2onnx(model_path, output, op_set, input_shape_list, model_def_file, model_class_name, model_input_type,
                    model_weights_file):
    if is_dynamic_paddle(input_shape_list, model_def_file, model_class_name, model_weights_file):
        convert_pd_dynamic2onnx(model_path, output, op_set, input_shape_list, model_def_file, model_class_name,
                                model_input_type, model_weights_file)
    else:
        convert_pd_static2onnx(model_path, output, op_set)
