from typing import Optional

import typer

from predibase.cli_commands.utils import get_client

app = typer.Typer(no_args_is_help=True)


@app.command(help="Fine-tune a Large Language Model (LLM)")
def llm(
    base_model_name: str = typer.Option(
        None,
        "--base-model",
        "-b",
        prompt="Name of the base model to fine-tune",
        prompt_required=True,
        help="Name of the base model to fine-tune",
    ),
    repo_name: Optional[str] = typer.Option(
        None,
        "--repo-name",
        "-r",
        prompt="Name of the repo in which to save the new model",
        prompt_required=True,
        help="Name of the repo in which to save the new model",
    ),
    template: str = typer.Option(
        None,
        "--template",
        prompt="Template input",
        prompt_required=True,
        help="Prompt template input text",
    ),
    target: str = typer.Option(
        None,
        "--target",
        prompt="Fine-tuning target column",
        prompt_required=True,
        help="Fine-tuning target column",
    ),
    dataset_name: Optional[str] = typer.Option(
        None,
        "--dataset",
        "-d",
        prompt="Dataset to fine-tune on",
        prompt_required=True,
        help="Dataset to fine-tune on",
    ),
    wait: Optional[bool] = typer.Option(
        None,
        "--wait",
        prompt="Whether to wait until training finishes",
        prompt_required=False,
        help="If set, the deploy command will not return until the training process finishes",
    ),
):
    client = get_client()
    job = client.LLM(base_model_name).finetune(
        template=template,
        target=target,
        dataset=dataset_name,
        repo=repo_name,
    )
    if wait:
        job.get()


if __name__ == "__main__":
    app()
