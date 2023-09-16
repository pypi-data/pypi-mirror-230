#!/usr/bin/env python
# coding:utf-8

import os
import torch
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
device = torch.device(0)

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
    serviceId = "chinese_llama_alpaca_2"
    version = "v1"
    requestCls = UserRequest()
    responseCls = UserResponse()
    model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filelogger = None

    def wrapperInit(self, config: {}) -> int:
        logger.info("Initializing ...")
        from ailab.utils.attn_and_long_ctx_patches import apply_attention_patch, apply_ntk_scaling_patch
        apply_attention_patch(use_memory_efficient_attention=True)
        apply_ntk_scaling_patch(1.0)

        from transformers import LlamaTokenizer, LlamaForCausalLM
        from peft import PeftModel
        base_model_path = os.environ.get("PRETRAINED_MODEL_NAME")
        lora_weight = os.environ.get("MODEL_PATH")
        tokenizer_path = os.environ.get("TOKENIZER_PATH")
        if not base_model_path or not lora_weight or not tokenizer_path:
            log.error("should have environ(PRETRAINED_MODEL_NAME,MODEL_PATH(lora weight dir）,TOKENIZER_PATH)")
            return -1

        load_type = torch.float16
        tokenizer = LlamaTokenizer.from_pretrained(tokenizer_path)
        base_model = LlamaForCausalLM.from_pretrained(
            base_model_path,
            load_in_8bit=True,
            torch_dtype=load_type,
            low_cpu_mem_usage=True,
            device_map='auto',
            )

        model_vocab_size = base_model.get_input_embeddings().weight.size(0)
        tokenzier_vocab_size = len(tokenizer)
        logger.info(f"Vocab of the base model: {model_vocab_size}")
        logger.info(f"Vocab of the tokenizer: {tokenzier_vocab_size}")
        if model_vocab_size!=tokenzier_vocab_size:
            assert tokenzier_vocab_size > model_vocab_size
            logger.info("Resize model embeddings to fit tokenizer")
            base_model.resize_token_embeddings(tokenzier_vocab_size)
        model = PeftModel.from_pretrained(base_model, lora_weight,torch_dtype=load_type,device_map='auto',)
        model.eval()

        self.model = model
        self.tokenizer = tokenizer
        self.filelogger = getFileLogger()
        return 0

    def wrapperOnceExec(self, params: {}, reqData: DataListCls, resId:int =0 ) -> Response:
        self.filelogger.info("got reqdata , %s" % reqData.list)
        tokenizer = self.tokenizer
        model = self.model

        def evaluate(instruction: str) -> str:
            generation_config = dict(
                temperature=0.2,
                top_k=40,
                top_p=0.9,
                do_sample=True,
                num_beams=1,
                repetition_penalty=1.3,
                max_new_tokens=400
                )

            # The prompt template below is taken from llama.cpp
            # and is slightly different from the one used in training.
            # But we find it gives better results
            prompt_input = (
                "[INST] <<SYS>>\n"
                "{system_prompt}\n"
                "<</SYS>>\n\n"
                "{instruction} [/INST]"
            )
            DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant. 你是一个乐于助人的助手。"""
            def generate_prompt(instruction, system_prompt=DEFAULT_SYSTEM_PROMPT):
                return prompt_input.format_map({'instruction': instruction,'system_prompt': system_prompt})

            with torch.no_grad():
                input_text = generate_prompt(instruction=instruction)
                inputs = tokenizer(input_text,return_tensors="pt")  #add_special_tokens=False ?
                input_ids = inputs["input_ids"].to(device)
                attention_mask = inputs['attention_mask'].to(device)
                generation_output = model.generate(
                    input_ids = input_ids, 
                    attention_mask = attention_mask,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.pad_token_id,
                    **generation_config
                )
                s = generation_output[0]
                output = tokenizer.decode(s,skip_special_tokens=True)
                response = output.split("[/INST]")[-1].strip()
                return response

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
