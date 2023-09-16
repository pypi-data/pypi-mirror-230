import os, argparse
import torch
from ailab.atp_dataset.dataset import AILabDataset
from ailab.atp_dataset.constant import Sources
from ailab.atp_finetuner.constant import Task, Framework
from ailab.atp_finetuner.finetuner import AILabFinetuner
from ailab.atp_finetuner.constant import Model


def train_progress(percent: float):
    pass


def model_test(args):
    # todo     # fixed pretrained in train_deprecatied.py
    pretrained_model_name = args.PRETRAINED_MODEL_NAME

    dataset_path = args.DATASET_PATH
    output_dir = args.OUTPUT_DIR
    pretrained_model_path = args.PRETRAINED_MODEL_PATH
    tokenizer_path = args.TOKENIZER_PATH
    finetune_type = args.FINETUNE_TYPE
    epoch = int(args.NUM_TRAIN_EPOCHS)
    learning_rate = float(args.LEARNING_RATE)
    max_source_length = int(args.MAX_SOURCE_LENGTH)
    batch_size = int(args.PER_DEVICE_TRAIN_BATCH_SIZE)
    end_to_zip = True if args.END_TO_ZIP.lower() == 'true' else False

    args = {
        "model_args": {
            "quantization_bit": None,  # LoRA
            "max_source_length": max_source_length,
        },
        "train_args": {
            "output_dir": output_dir,
            "evaluation_strategy": "epoch",
            "per_device_eval_batch_size": batch_size,
            "eval_steps": 250,
            "resume_from_checkpoint": False,
            "num_train_epochs": epoch,
            "per_device_train_batch_size": batch_size,
            "gradient_accumulation_steps": 4,
            "learning_rate": learning_rate,
            "logging_steps": 10,
            "save_steps": 500,
            "bf16": False,
            "save_strategy": "steps",
            "weight_decay": 0,
            "end_to_zip":end_to_zip
        },
    }

    # 根据不同的模型，个性化处理
    dataset = AILabDataset.load_dataset(dataset_path, src=Sources.huggingface)

    if pretrained_model_name in [
        Model.chinese_alpaca,
        Model.chinese_alpaca_2,
        Model.vicuna,
        Model.open_llama,
        Model.alpaca,
        Model.ziya_llama_13b,
        Model.bencao_llama,
    ]:
        dataset.train_test_split(test_size=0.2)

    if pretrained_model_name == Model.chinese_alpaca_2:
        finetune_type == "lora"

    if pretrained_model_name == Model.xverse_13b or pretrained_model_name == Model.code_geex_2:
        args["train_args"]["bf16"] = True

    # 针对 微调方式的处理
    if finetune_type == "qlora":
        args["model_args"]["quantization_bit"] = 4
        args["model_args"]["quantization_type"] = "nf4"
        args["model_args"]["double_quantization"] = True
        args["model_args"]["compute_dtype"] = torch.float16

    finetuner = AILabFinetuner(
        Task.question_answering,
        Framework.Pytorch,
        dataset,
        pretrained_model_name,
        train_progress,
        pretrained_model_path,
        tokenizer_path,
        **args
    )
    finetuner.finetuner()


if __name__ == "__main__":
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="Example script with arguments")

    # 添加参数
    parser.add_argument("--PRETRAINED_MODEL_NAME", type=str, help="Pretrained model name")
    parser.add_argument("--DATASET_PATH", type=str, help="Dataset path")
    parser.add_argument("--PRETRAINED_MODEL_PATH", type=str, help="Pretrained model path")
    parser.add_argument("--TOKENIZER_PATH", type=str, help="Tokenizer path")
    parser.add_argument("--OUTPUT_DIR", type=str, help="Output directory")
    parser.add_argument("--FINETUNE_TYPE", type=str, help="Finetune type")
    parser.add_argument("--NUM_TRAIN_EPOCHS", type=str, help="epochs")
    parser.add_argument("--LEARNING_RATE", type=str, help="learning_rate")
    parser.add_argument("--MAX_SOURCE_LENGTH", type=str, help="max source token length")
    parser.add_argument("--END_TO_ZIP", type=str, help="after train to pack zip")
    parser.add_argument("--PER_DEVICE_TRAIN_BATCH_SIZE", type=str, help="batch size")

    # 解析命令行参数
    args = parser.parse_args()

    model_test(args)
