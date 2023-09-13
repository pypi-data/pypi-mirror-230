import torch
import onnx
import onnxruntime
import numpy as np

input_tmp = np.random.rand(1, 3, 10, 10).astype(np.float32)


class MyModel(torch.nn.Module):
    def __init__(self, n):
        super().__init__()
        self.n = n
        self.conv = torch.nn.Conv2d(3, 3, 3)

    def forward(self, x):
        for i in range(self.n):
            x = self.conv(x)
        return x


def create_model():
    model = MyModel(3)
    dummy_input = torch.from_numpy(input_tmp)
    dummy_output = model(dummy_input)
    print("torch output: ", dummy_output)
    torch.save(model, 'model.pt')
    torch.onnx.export(model, dummy_input, 'model.onnx', input_names=["input_0"], output_names=["output_0"])


def run_pt():
    model = torch.load("model.pt")
    dummy_input = torch.from_numpy(input_tmp)
    dummy_output = model(dummy_input)
    print("torch output: ", dummy_output)


def run_onnx():
    model = onnx.load("test_tf_model.onnx")  # 加载onnx
    onnx.checker.check_model(model)  # 检查生成模型是否错误
    print(onnx.helper.printable_graph(model.graph))

    ort_session = onnxruntime.InferenceSession("test_tf_model.onnx")
    ort_outs = ort_session.run(["output_0"], {"input_0": input_tmp})
    print("onnx output: ", ort_outs)


if __name__ == '__main__':
    # create_model()
    # run_pt()
    run_onnx()
