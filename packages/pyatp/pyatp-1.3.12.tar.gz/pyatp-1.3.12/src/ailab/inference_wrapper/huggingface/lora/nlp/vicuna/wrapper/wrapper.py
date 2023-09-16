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
    serviceId = "chinese_llama_vicuna"
    version = "v1"
    requestCls = UserRequest()
    responseCls = UserResponse()
    model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filelogger = None

    def wrapperInit(self, config: {}) -> int:
        logger.info("Initializing ...")
        from transformers import LlamaForCausalLM, LlamaTokenizer
        from peft import PeftModel
        base_model = os.environ.get("PRETRAINED_MODEL_NAME")
        lora_weight = os.environ.get("MODEL_PATH")
        tokenizer_path = os.environ.get("TOKENIZER_PATH")
        if not base_model or not lora_weight or not tokenizer_path:
            log.error("should have environ(PRETRAINED_MODEL_NAME,MODEL_PATH(lora weight dir）,TOKENIZER_PATH)")
            return -1

        from transformers import LlamaForCausalLM,LlamaTokenizer
        from ailab.utils.streampeft import StreamPeftGenerationMixin
        tokenizer = LlamaTokenizer.from_pretrained(tokenizer_path)
        model = LlamaForCausalLM.from_pretrained(base_model, load_in_8bit=True,torch_dtype=torch.float16,device_map={"": 0},)
        model = StreamPeftGenerationMixin.from_pretrained(model, lora_weight, torch_dtype=torch.float16, device_map={"": 0})
        self.model = model
        self.tokenizer = tokenizer
        self.filelogger = getFileLogger()
        return 0

    def wrapperOnceExec(self, params: {}, reqData: DataListCls) -> Response:
        self.filelogger.info("got reqdata , %s" % reqData.list)
        tokenizer = self.tokenizer
        model = self.model

        from transformers import GenerationConfig
        def generate_prompt(instruction, input=None):
            if input:
                return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
        ### Instruction:
        {instruction}

        ### Input:
        {input}

        ### Response:"""
            else:
                return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

        ### Instruction:
        {instruction}

        ### Response:"""

        model.eval()
        model = torch.compile(model)

        def evaluate(
            input,
            temperature=0.1,
            top_p=0.75,
            top_k=40,
            num_beams=4,
            max_new_tokens=128,
            min_new_tokens=1,
            repetition_penalty=2.0,
            **kwargs,
        ):
            prompt = generate_prompt(input)
            inputs = tokenizer(prompt, return_tensors="pt")
            input_ids = inputs["input_ids"].to("cuda")
            generation_config = GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                num_beams=num_beams,
                bos_token_id=1,
                eos_token_id=2,
                pad_token_id=0,
                max_new_tokens=max_new_tokens, # max_length=max_new_tokens+input_sequence
                min_new_tokens=min_new_tokens, # min_length=min_new_tokens+input_sequence
                **kwargs,
            )
            use_typewriter = 1
            with torch.no_grad():
                for generation_output in model.stream_generate(
                    input_ids=input_ids,
                    generation_config=generation_config,
                    return_dict_in_generate=True,
                    output_scores=False,
                    repetition_penalty=float(repetition_penalty),
                ):
                    outputs = tokenizer.batch_decode(generation_output)
                response = outputs[0].split("### Response:")[1]
                return response.split("### Instruction:")[0].strip().replace('\u2047','')

        input_text = reqData.get("text").data.decode('utf-8')
        result = evaluate(input_text)
        self.filelogger.info("result , %s" % result)
        # 使用Response封装result
        res = Response()
        resd = ResponseData()
        resd.key = "result"
        resd.setDataType(DataText)
        resd.status = Once
        resd.setData(result.encode('utf-8'))
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
