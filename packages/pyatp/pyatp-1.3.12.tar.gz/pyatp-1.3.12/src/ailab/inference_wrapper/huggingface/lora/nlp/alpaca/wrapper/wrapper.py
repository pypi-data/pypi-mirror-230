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
    serviceId = "standford_alpaca"
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
            log.error("should have environ(BASE_MODEL,LORA_WEIGHT,TOKENIZER_PATH)")
            return -1

        tokenizer = LlamaTokenizer.from_pretrained(tokenizer_path)
        model = LlamaForCausalLM.from_pretrained(base_model,load_in_8bit=True,torch_dtype=torch.float16,device_map="auto",)
        model = PeftModel.from_pretrained(model,lora_weight,torch_dtype=torch.float16,)
        model.config.pad_token_id = tokenizer.pad_token_id = 0  # unk
        model.config.bos_token_id = 1
        model.config.eos_token_id = 2
        model.eval()
        model = torch.compile(model)
        self.model = model
        self.tokenizer = tokenizer
        self.filelogger = getFileLogger()
        self.filelogger.info("wrapperInit end")
        return 0

    def wrapperOnceExec(self, params: {}, reqData: DataListCls) -> Response:
        self.filelogger.info("got reqdata , %s" % reqData.list)
        tokenizer = self.tokenizer
        model = self.model

        import transformers
        from transformers import GenerationConfig
        from ailab.utils.callbacks import Iteratorize, Stream

        prompt_template: str = ""  # The prompt template to use, will default to alpaca.
        from ailab.utils.prompter import Prompter
        prompter = Prompter(prompt_template)

        def evaluate(
            instruction,
            input=None,
            temperature=0.1,
            top_p=0.75,
            top_k=40,
            num_beams=4,
            max_new_tokens=128,
            stream_output=False,
            **kwargs,
        ):
            prompt = prompter.generate_prompt(instruction, input)
            inputs = tokenizer(prompt, return_tensors="pt")
            input_ids = inputs["input_ids"].to('cuda')
            generation_config = GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                num_beams=num_beams,
                **kwargs,
            )

            # Without streaming
            with torch.no_grad():
                generation_output = model.generate(
                    input_ids=input_ids,
                    generation_config=generation_config,
                    return_dict_in_generate=True,
                    output_scores=True,
                    max_new_tokens=max_new_tokens,
                )
            s = generation_output.sequences[0]
            output = tokenizer.decode(s)
            response =  prompter.get_response(output)
            return response.split("### Instruction:")[0].strip()

        input_text = reqData.get("text").data.decode('utf-8')
        self.filelogger.info("got input_text , %s" % input_text)
        result = evaluate(input_text)
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
