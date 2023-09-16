from typing import Callable, Optional
from ailab.atp_dataset.dataset import AILabDataset
from ailab.atp_finetuner.constant import Framework, Task, Model
from ailab.atp_finetuner.preprossor import AILabPreprocessor
from ailab.atp_finetuner.model import AILabModel
from ailab.atp_finetuner.datacollator import AILabDataCollator
from ailab.atp_finetuner.metric import AILabMetric
from ailab.atp_finetuner.trainer import AILabTrainer
from ailab.atp_finetuner.accelerator import AILabAccelerator

class AILabFinetuner:
    def __init__(self, task: Task, framework: Framework.Pytorch, 
                dataset: AILabDataset, model_name: Model, 
                train_progress:Callable, 
                model_dir: Optional[str] = None,
                pc_dir: Optional[str] = None, 
                **args):
        accelerator = AILabAccelerator.from_project_config(**args)
        preprocessor = AILabPreprocessor.from_pretrained(task, model_name, dataset, pc_dir, **args)
        preprocessor.accelerator = accelerator
        tokenized_dataset = preprocessor.process_data()

        model = AILabModel.from_pretrained('cuda', task, model_name, model_dir, **args)
        model.accelerator = accelerator
        model.forward()

        data_collator = AILabDataCollator.from_task_model(task, model_name, framework, preprocessor, model)
        metrics = AILabMetric.from_task_model(task, model_name)
        trainer = AILabTrainer.from_task_model(task, model_name, tokenized_dataset, model, preprocessor, data_collator,
                                               metrics, train_progress, **args)
        trainer.accelerator = accelerator

        self._trainer = trainer

    def finetuner(self):
        self._trainer.train()
