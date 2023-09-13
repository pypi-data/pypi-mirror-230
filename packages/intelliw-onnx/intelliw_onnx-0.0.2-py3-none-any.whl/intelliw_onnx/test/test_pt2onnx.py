import torch
import onnxruntime
import numpy as np

from intelliw_onnx.convert import ONNXConvert, ConvertArgs
from intelliw_onnx.test.test_onnx_demo import MyModel

input_tmp = np.random.rand(1, 3, 10, 10).astype(np.float32)

"""
 python main.py convert --model_path ./test/model.pt --model_type pytorch --output "./test/output.onnx" --input_shape '[1,3,10,10]'  \
 --model_def_file './test/test_onnx_demo.py' \
 --model_class_name 'MyModel'  \
 --params_file ./test/params.py
"""

if __name__ == '__main__':
    # 转换
    args = ConvertArgs(model_path='./model.pt',
                       model_type='pytorch',
                       output='./test_tf_model.onnx',
                       input_shape='[1,3,10,10]',
                       model_def_file="./test_onnx_demo.py",
                       model_class_name="MyModel",
                       op_set=12,
                       params_file="./params.py")
    converter = ONNXConvert(args)
    converter.convert()

    # torch
    model = torch.load("model.pt")
    dummy_input = torch.from_numpy(input_tmp)
    dummy_output = model(dummy_input)

    # onnx
    ort_session = onnxruntime.InferenceSession("test_tf_model.onnx")
    ort_outs = ort_session.run(["output"], {"input": input_tmp})
    print("\n\nonnx output: \n", np.around(ort_outs, decimals=4), "\n\ntorch output:\n", dummy_output, flush=True)
