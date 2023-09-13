# pyright: reportShadowedImports=false
from pathlib import Path
from typing import *

import onnx
from onnxsim import simplify
from typer import Argument

from .cli import cli

__all__ = ["clean"]


@cli.command()
def clean(
    source: Path = Argument(..., help="Source onnx"),
    target: Path = Argument(..., help="Target onnx"),
):
    assert (
        source.exists() and source.is_file() and source.suffix.lower() == ".onnx"
    ), f"{source} is invalid"
    model = onnx.load(source.as_posix())
    model_simp, check = simplify(model)

    if check:
        model = model_simp

    if model.ir_version < 4:
        print(
            "Model with ir_version below 4 requires to include initilizer in graph input"
        )
        return

    inputs = model.graph.input
    name_to_input = {}
    for input in inputs:
        name_to_input[input.name] = input

    for initializer in model.graph.initializer:
        if initializer.name in name_to_input:
            inputs.remove(name_to_input[initializer.name])

    target.parent.mkdir(exist_ok=True, parents=True)
    onnx.save(model, target.as_posix())
