
from typing import Dict, Optional,Callable
import os,torch,sys,json
from transformers.modeling_utils import unwrap_model
from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer
from peft.utils.other import WEIGHTS_NAME
from ailab.utils.other import get_state_dict,load_trainable_params,load_valuehead_params,plot_loss,VALUE_HEAD_FILE_NAME
from ailab.atp_dataset.dataset import AILabDataset
from ailab.atp_finetuner.trainer import AILabTrainer 
from ailab.atp_finetuner.model import AILabModel
from ailab.atp_finetuner.datacollator import AILabDataCollator
from ailab.atp_finetuner.metric import AILabMetric
from ailab.atp_finetuner.preprossor import AILabPreprocessor
from ailab.atp_finetuner.build import TrainerRg
from ailab.atp_finetuner.constant import Task, Model
from ailab.utils.callbacks import TrainProgress
from ailab.log import logger

class PeftTrainer(Seq2SeqTrainer):
    r"""
    Inherits Seq2SeqTrainer to support parameter-efficient checkpoints.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _save(self, output_dir: Optional[str] = None, state_dict: Optional[Dict[str, torch.Tensor]] = None) -> None:
        r"""
        Saves trainable parameters as model checkpoint.

        This function will only be executed at the process zero.

        Subclass and override to inject custom behavior. It should not be directly used by external scripts.
        """

        output_dir = output_dir if output_dir is not None else self.args.output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Saving model checkpoint to {output_dir}")
        model = unwrap_model(self.model)

        if hasattr(model, "pretrained_model"): # for models with valuehead
            logger.info(f'model hasattr pretrained_model')
            backbone_model = getattr(model, "pretrained_model")
        else:
            logger.info(f'model not hasattr pretrained_model')
            backbone_model = model
        from peft.utils.other import WEIGHTS_NAME
        if hasattr(backbone_model, "peft_config"): # peft methods
            logger.info(f'model hasattr peft_config')
            backbone_model.save_pretrained(output_dir, state_dict=get_state_dict(backbone_model)) # save lora weights
        else:
            logger.info(f'model not hasattr peft_config')
            torch.save(get_state_dict(backbone_model), os.path.join(output_dir, WEIGHTS_NAME)) # save trainable weights

        if hasattr(model, "v_head"): # save valuehead weights
            torch.save(get_state_dict(getattr(model, "v_head")), os.path.join(output_dir, VALUE_HEAD_FILE_NAME))

    def _load_best_model(self):
        r"""
        Loads trainable parameters from model checkpoint.

        Subclass and override to inject custom behavior. It should not be directly used by external scripts.
        """
        logger.info(f"Loading best model from {self.state.best_model_checkpoint} (score: {self.state.best_metric}).")
        model = unwrap_model(self.model)
        if hasattr(model, "peft_config"): # peft methods
            model.load_adapter(self.state.best_model_checkpoint, getattr(model, "active_adapter"))
        else:
            load_trainable_params(model, self.state.best_model_checkpoint)

        if hasattr(model, "v_head"):
            load_valuehead_params(model, self.state.best_model_checkpoint)

@TrainerRg.register((Task.question_answering, Model.baichuan_7b))
@TrainerRg.register((Task.question_answering, Model.baichuan_13b))
@TrainerRg.register((Task.question_answering, Model.bloomz_7b1_mt))
@TrainerRg.register((Task.question_answering, Model.falcon_7b))
@TrainerRg.register((Task.question_answering, Model.moss_moon_003_base))
@TrainerRg.register((Task.question_answering, Model.llama2_7b))
@TrainerRg.register((Task.question_answering, Model.internlm_7b))
@TrainerRg.register((Task.question_answering, Model.belle_7b_2m))
@TrainerRg.register((Task.question_answering, Model.xverse_13b))
@TrainerRg.register((Task.question_answering, Model.lawgpt_llama))
class BaichuanTrainer(AILabTrainer):
    def __init__(self):
        super().__init__()

    def preprocess(self, dataset:AILabDataset, model:AILabModel, preprocessor: AILabPreprocessor, \
                      data_collator:AILabDataCollator, metric:AILabMetric, train_progress:Callable, **kwargs):
        train_args = kwargs['train_args']
        output_dir = train_args.get('output_dir', 'my_model')
        learning_rate = train_args.get('learning_rate', 1e-5)
        num_train_epochs = train_args.get('num_train_epochs', 2)
        save_strategy = train_args.get('save_strategy', "steps")
        per_device_train_batch_size = train_args.get('per_device_train_batch_size', 4)
        gradient_accumulation_steps = train_args.get('gradient_accumulation_steps', 1)
        logging_steps = train_args.get('logging_steps', 10)
        fp16 = True 
        bf16 = train_args.get('bf16',False)
        if bf16 == True:
            fp16 = False
        save_steps = train_args.get('save_steps', 500)

        deepspeed_dir = os.path.dirname(os.path.abspath(__file__))
        deepspeed_dir = os.path.join(deepspeed_dir,"ds_zero2_no_offload.json")
        training_args=Seq2SeqTrainingArguments(
                generation_max_length = 512,
                generation_num_beams = None,
                per_device_train_batch_size=per_device_train_batch_size,
                gradient_accumulation_steps=gradient_accumulation_steps,
                lr_scheduler_type="cosine",
                num_train_epochs=num_train_epochs,
                learning_rate=learning_rate,
                fp16=fp16,
                bf16=bf16,
                logging_steps=logging_steps,
                optim="adamw_torch",
                save_strategy=save_strategy,
                save_steps=save_steps,
                output_dir=output_dir,
                save_total_limit=3,
                report_to= None,
                push_to_hub=False,
                ddp_find_unused_parameters=False,
                ddp_timeout=30000,
                deepspeed=deepspeed_dir,
            )

        logger.info(f'training_args {training_args}')
        
        trainer = PeftTrainer(
            model=model.model_ins,
            train_dataset=dataset.to_hf_dataset(),
            args=training_args,
            tokenizer=preprocessor.preprocessor_ins,
            data_collator=data_collator.datacollator_ins,
            callbacks=[TrainProgress(train_progress)],
        )

        self.trainer = trainer
        self.train_args = train_args
    
    def train(self):
        trainer = self.trainer
        output_dir = self.train_args.get('output_dir', 'my_model')
        resume_from_checkpoint = self.train_args.get('resume_from_checkpoint', False)
        end_to_zip = self.train_args.get('end_to_zip', False)

        train_result = trainer.train()
        trainer.log_metrics("train", train_result.metrics)
        trainer.save_metrics("train", train_result.metrics)
        trainer.save_state()
        trainer.save_model()

        if trainer.is_world_process_zero():
            plot_loss(output_dir, keys=["loss", "eval_loss"])
            if end_to_zip:
                from ailab.utils.other import create_zip_and_delete_folder
                zip_file_path = output_dir+"/adapter.zip"
                create_zip_and_delete_folder(output_dir,zip_file_path)

    def postprocess(self):
        self.trainer.evaluate()



