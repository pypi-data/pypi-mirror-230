#!/usr/bin/env python
# coding:utf-8
"""
@license: Apache License2
@file: wrapper.py
@time: 2022-08-19 02:05:07.467170
@project: mnist
@project: ./
"""
import json
import torch
import os.path
from aiges.core.types import *
try:
    from aiges_embed import ResponseData, Response, DataListNode, DataListCls  # c++
except:
    from aiges.dto import Response, ResponseData, DataListNode, DataListCls

from aiges.sdk import WrapperBase, \
    ImageBodyField, \
    StringBodyField, StringParamField
from aiges.utils.log import log, getFileLogger
from ailab.log import logger

# 定义模型的超参数和输入参数
class UserRequest(object):
    input1 = StringBodyField(key="text", value=b"I have a problem with my iphone that needs to be resolved asap!!")


# 定义模型的输出参数
class UserResponse(object):
    accept1 = StringBodyField(key="result")


# 定义服务推理逻辑
class Wrapper(WrapperBase):
    serviceId = "chatglm_6b"
    version = "v1"
    requestCls = UserRequest()
    responseCls = UserResponse()
    model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filelogger = None

    def wrapperInit(self, config: {}) -> int:
        logger.info("Initializing ...")
        from transformers import AutoTokenizer, AutoModel
        from peft import PeftModel, LoraConfig, TaskType, get_peft_model
        base_model = os.environ.get("PRETRAINED_MODEL_NAME")
        lora_weight = os.environ.get("MODEL_PATH")
        tokenizer_path = os.environ.get("TOKENIZER_PATH")
        lora_weight_bin = os.path.join(lora_weight, "adapter_model.bin")

        if not base_model or not lora_weight or not tokenizer_path:
            log.error("should have environ(BASE_MODEL,MODEL_PATH(lora weight dir.),TOKENIZER_PATH)")
            return -1

        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True)
        model = AutoModel.from_pretrained(base_model, trust_remote_code=True, load_in_8bit=True, device_map='auto')

        peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=True,
                r=8,
                lora_alpha=32,
                lora_dropout=0.1
            )
        model = get_peft_model(model, peft_config)
        model.load_state_dict(torch.load(lora_weight_bin), strict=False)
        #model = PeftModel.from_pretrained(model, lora_weight, torch_dtype=torch.float16)
        model.eval()
        model = torch.compile(model)

        self.model = model
        self.tokenizer = tokenizer
        self.filelogger = getFileLogger()
        return 0

    def wrapperOnceExec(self, params: {}, reqData: DataListCls) -> Response:
        self.filelogger.info("got reqdata , %s" % reqData.list)
        tokenizer = self.tokenizer
        model = self.model

        def evaluate(instruction: str) -> str:
            with torch.no_grad():
                input_text = f"Instruction: {instruction}\n"
                input_text += "Answer: "
                ids = tokenizer.encode(input_text)
                input_ids = torch.LongTensor([ids])
                out = model.generate(
                    input_ids=input_ids,
                    max_length=150,
                    do_sample=False,
                    temperature=0
                )
                out_text = tokenizer.decode(out[0])
                answer = out_text.replace(input_text, "").replace("\nEND", "").strip()
                return answer

        instruction = reqData.get("text").data.decode('utf-8')
        result = evaluate(instruction)
        self.filelogger.info("got result , %s" % result)
        # 使用Response封装result
        res = Response()
        resd = ResponseData()
        resd.key = "result"
        resd.setDataType(DataText)
        resd.status = Once
        resd.setData(result.encode("utf-8"))
        res.list = [resd]
        return res

    def wrapperFini(cls) -> int:
        return 0

    def wrapperError(cls, ret: int) -> str:
        if ret == 100:
            return "user error defined here"
        return ""

    '''
        此函数保留测试用，不可删除
    '''

    def wrapperTestFunc(cls, data: [], respData: []):
        pass


if __name__ == '__main__':
    m = Wrapper()
    m.run()
