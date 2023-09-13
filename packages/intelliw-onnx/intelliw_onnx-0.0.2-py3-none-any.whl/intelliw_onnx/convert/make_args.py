from dataclasses import dataclass


@dataclass
class ConvertArgs:
    """生成转换参数
    :argument
        model_path: [required]  Input path(model file or folder)
        model_type: [required]  Input model type(ex: paddle/pytorch)
        output:     [required]  Output path(ex: ./output.onnx)

        op_set:             Set op_set version(default: 11)
        input_shape:        [pytorch/paddle required]  Input shape for pytorch/paddle(ex: [1,3,224,224] or [1,3,224,224]/[1,3,56,56])
        model_def_file:      [pytorch/paddle required]  Paddle/pytorch model definition file location(ex: --model_def_file ./cnn.py)
        model_class_name:   [pytorch/paddle required]  Paddle/pytorch model class name(ex: --model_class_name CNN)
        model_weights_file:  Paddle/pytorch model weights file location(ex: --model_weights_file ./0.99667.pth)
        model_input_type:   Paddle/pytorch input type(default float, choice is ['float', 'float32', 'float16', 'uint8', 'int8', 'uint16', 'int16', 'uint32', 'int32', 'uint64', 'int64', 'bool'])
        params_file:         Paddle/pytorch params declaration file location(ex: --params_file ./params.py)
        output_num:         If output num of pytorch model > 1, you can specify it by --output_num
        keep_batch:         For pytorch, if set 1, the tool will keep model batch size(if 0, set it to dynamic(-1))"
        dynamic_batch:      If set 1, the tool will convert batch size to -1
        simplify:           Simplify the model(0:no simplify;1:do simplify; 2:for dynamic model)
        simplify_hw:        When h/w is -1, you can specify h/w as you expected(together with --simplify 2)
        force_simplify:     Force simplify the model(0:no simplify;1:do simplify; 2:for dynamic model)

    :return
        args object
    """
    model_path: str
    model_type: str
    output: str

    op_set: int = 11
    model_def_file: str = ''
    model_weights_file: str = ''
    model_class_name: str = ''
    input_shape: str = ''
    model_input_type: str = ''
    params_file: str = ''
    output_num: int = 1
    keep_batch: int = 1
    dynamic_batch: int = 0
        
    simplify: int = 0
    simplify_hw: str = ''
    force_simplify: int = 0

    version: bool = False
