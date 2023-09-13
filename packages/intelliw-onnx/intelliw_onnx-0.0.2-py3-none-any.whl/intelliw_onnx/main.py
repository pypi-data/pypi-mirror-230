import argparse
from intelliw_onnx.convert.convert import ONNXConvert


def handle_convert(args):
    ONNXConvert(args).convert()


def handle_default(args):
    if args.version:
        exit(0)


def main():
    parser = argparse.ArgumentParser()
    # parser #
    parser.set_defaults(func=handle_default)
    # show package version
    parser.add_argument('--version', '-v',
                        action='store_true',
                        default=False,
                        help='Show intelliw-onnx version')
    subparsers = parser.add_subparsers(help='commands')

    # convert #
    convert_parser = subparsers.add_parser(name='convert', help='Convert torch/paddle model to ONNX.')

    convert_parser.add_argument("--model_path",
                                type=str,
                                help="Input path(model file or folder)")
    convert_parser.add_argument("--model_type",
                                type=str,
                                help="Input model type(ex: paddle/pytorch)")
    convert_parser.add_argument("--output",
                                type=str,
                                help="Output path(ex: ./output.onnx)")
    convert_parser.add_argument("--op_set",
                                type=int, required=False,
                                help="Set op_set version(default: 11)")
    # for pytorch/dynamic_paddle
    convert_parser.add_argument("--input_shape",
                                type=str,
                                required=False,
                                default='',
                                help="Input shape for pytorch/paddle(ex: [1,3,224,224] or [1,3,224,224]/[1,3,56,56])")
    # for paddle dynamic model or pytorch
    convert_parser.add_argument("--model_def_file",
                                type=str,
                                required=False,
                                default='',
                                help="Paddle/pytorch model definition file location(ex: --model_def_file ./cnn.py)")

    convert_parser.add_argument("--model_weights_file",
                                type=str,
                                required=False,
                                default='',
                                help="Paddle/pytorch model weights file location(ex: --model_weights_file ./0.99667.pth)")

    convert_parser.add_argument("--model_class_name",
                                type=str,
                                required=False,
                                default='',
                                help="Paddle/pytorch model class name(ex: --model_class_name CNN)")

    convert_parser.add_argument("--model_input_type",
                                type=str,
                                required=False,
                                default='',
                                help="Paddle/pytorch input type(default float, choice is ['float', 'float32', 'float16', 'uint8', 'int8', 'uint16', 'int16', 'uint32', 'int32', 'uint64', 'int64', 'bool'])")

    convert_parser.add_argument("--params_file",
                                type=str,
                                required=False,
                                default='',
                                help="Paddle/pytorch params declaration file location(ex: --params_file ./params.py)")

    # for pytorch/paddle
    convert_parser.add_argument("--output_num",
                                type=int,
                                required=False,
                                default=1,
                                help="If output num of pytorch model > 1, you can specify it by --output_num")

    # for pytorch
    convert_parser.add_argument("--keep_batch",
                                type=int,
                                choices=[0, 1],
                                required=False,
                                default=1,
                                help="For pytorch, if set 1, the tool will keep model batch size(if 0, set it to dynamic(-1))")

    # for dynamic batch size
    convert_parser.add_argument("--dynamic_batch",
                                type=int,
                                required=False,
                                default=0,
                                choices=[0, 1],
                                help="If set 1, the tool will convert batch size to -1")

    # for simplify
    convert_parser.add_argument("--simplify",
                                type=int, required=False,
                                choices=[0, 1, 2],
                                default=0,
                                help="Simplify the model(0:no simplify;1:do simplify; 2:for dynamic model)")

    convert_parser.add_argument("--simplify_hw",
                                type=str,
                                required=False,
                                default='',
                                help="When h/w is -1, you can specify h/w as you expected(together with --simplify 2)")

    # force simplify
    convert_parser.add_argument("--force_simplify",
                                type=int, required=False,
                                choices=[0, 1, 2],
                                default=0,
                                help="Force simplify the model(0:no simplify;1:do simplify; 2:for dynamic model)")

    convert_parser.set_defaults(func=handle_convert)

    args = parser.parse_args()

    # 执行函数功能
    try:
        args.func(args)
    except AttributeError:
        print("try use `intelliw-onnx -h`")


if __name__ == '__main__':
    main()
