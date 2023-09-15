from tritonclient.utils import *
import tritonclient.grpc as grpcclient
import tritonclient.http as httpclient
import numpy as np
import os

def stream_chat(
                message='你好',
                history=[],
                model_name='chatglm2-6b',
                sequence_id=10087
                ):
    # %pip install tritonclient[all]
    """

    :param model_name: str 'chatglm2-6b','llama2-7b','yulan_13b','baichuan-13b'
    :param message: str '你好'
    :param history: [] or [['你好', '我是朱皮特'], ['你好', '我是皮特严格'], ['你好', '我是皮特严格'], ['你好', '我是皮特严格']]
    :param sequence_id: int 10087
    :return:
    """
    ip = os.environ.get('Triton_HTTP_IP',None)
    if ip is None:
        raise ValueError("Triton_HTTP_IP is not set")

    with httpclient.InferenceServerClient(ip) as client:
        idx = 0
        history = history if history != [] else [[]]
        input0_data = np.array([[message]], dtype=np.dtype(object))
        input1_data = np.array([history], dtype=np.dtype(object))
        inputs = [httpclient.InferInput("INPUT0", input0_data.shape, np_to_triton_dtype(input0_data.dtype)),
                  httpclient.InferInput("INPUT1", input1_data.shape, np_to_triton_dtype(input1_data.dtype))
                  ]

        inputs[0].set_data_from_numpy(input0_data)
        inputs[1].set_data_from_numpy(input1_data)

        outputs = [
            httpclient.InferRequestedOutput('OUTPUT0')
        ]
        history += [[[], []]]
        while True:
            response = client.infer(model_name,
                                    inputs,
                                    outputs=outputs,
                                    request_id=str(idx),
                                    sequence_id=sequence_id,
                                    sequence_start=(idx == 0),
                                    sequence_end=False)

            result = response.get_response()
            if result['outputs'][0]['shape'] == [1, 1, 2]:
                if model_name in ['chatglm2-6b','yulan-13b']:
                    response = response.as_numpy("OUTPUT0")[0][0][0].decode('utf-8')
                elif model_name in ['llama2-7b','baichuan-13b']:
                    response = response.as_numpy("OUTPUT0")[0][0].decode('utf-8')
            else:
                break
            history[-1][0] = message
            history[-1][1] = response
            yield response, history

def chat(message='你好',history=[],**kwargs):
     return [i for i in stream_chat(message=message,history=history,**kwargs)][-1]
