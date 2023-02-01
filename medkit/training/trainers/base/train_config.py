from dataclasses import dataclass, field
from typing import Optional, Union

from transformers.optimization import SchedulerType


@dataclass
class TrainConfig:
    output_dir: str
    learning_rate: float = field(default=5)
    num_training_epochs: int = field(default=3)
    logging_dir: Optional[str] = field(default=None)
    dataloader_num_workers: int = field(default=0)
    batch_size: int = field(default=8)
    lr_scheduler_type: Union[str, SchedulerType] = field(
        default="reduce_lr_with_metric"
    )
    gradient_accumulation_steps: int = field(default=1)
    do_metrics_in_training: bool = False
    metric_to_track_lr: str = field(default="eval_loss_epoch")
