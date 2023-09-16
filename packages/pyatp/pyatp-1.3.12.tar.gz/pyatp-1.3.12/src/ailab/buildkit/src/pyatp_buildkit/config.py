import logging

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(ch)

SUPPORTED_DISTRO_LIST = ["ubuntu1804"]
SUPPORTED_PYVERSION_LIST = ["3.9.13", "conda-3.7", "conda-3.8", "conda-3.9"]
SUPPORTED_GOLANG_LIST = ["1.17"]
SUPPORTED_CUDA_LIST = ["10.1", "10.2", "11.2", "11.6"]

# ECR_REPO = "public.ecr.aws/iflytek-open"
ECR_REPO = "iflyopensource"
INNER_REPO = "artifacts.iflytek.com/docker-private/atp"
TEMP_GEN_DIR = "/tmp/ailab_sdk_tmpdir"
Dockerfile = "Dockerfile"

SUPPORTED_TRAIN_TASKS = ['text_classification', 'chatglm_6b', "chinese_llama_vicuna", "chinese_llama_alpaca",
                         "standford_alpaca","llama2_7b", "chinese-alpaca-2-7b","chinese_llama_alpaca_2"]

SUPPORTED_TRAIN_TASKS_WRAPPER_MAP = {
    "text_classification": "ailab/inference_wrapper/huggingface/transformers/nlp/text_classification",
    "chatglm_6b":"ailab/inference_wrapper/huggingface/lora/nlp/chatglm",
    "chinese_llama_vicuna": "ailab/inference_wrapper/huggingface/lora/nlp/vicuna",
    "chinese_llama_alpaca": "ailab/inference_wrapper/huggingface/lora/nlp/alpaca",
    "standford_alpaca": "ailab/inference_wrapper/huggingface/lora/nlp/alpaca",
    'llama2_7b': "ailab/inference_wrapper/huggingface/lora/nlp/llama2",
    "chinese_llama_alpaca_2": "ailab/inference_wrapper/huggingface/lora/nlp/chinese_alpaca2",
}