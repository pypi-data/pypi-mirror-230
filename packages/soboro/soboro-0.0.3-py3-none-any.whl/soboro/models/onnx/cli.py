from ...cli import cli as base_cli

__all__ = ["cli"]

cli = base_cli.sub_cli("onnx")
