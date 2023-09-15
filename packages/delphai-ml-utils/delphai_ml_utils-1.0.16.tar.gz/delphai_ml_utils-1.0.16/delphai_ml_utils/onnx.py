# Following https://huggingface.co/docs/transformers/serialization

import os
from transformers import AutoTokenizer


def make_onnx(
    path_to_model: str,
    pretrained_model_name: str,
    feature: str = "sequence-classification",
    atol: float = 0,
) -> None:
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=pretrained_model_name
    )
    tokenizer.save_pretrained(path_to_model)
    command = f"python -m transformers.onnx --model={path_to_model} {path_to_model}"
    if feature:
        command += f" --feature {feature}"
    if atol:
        command += f" --atol {atol}"
    os.system(command)
