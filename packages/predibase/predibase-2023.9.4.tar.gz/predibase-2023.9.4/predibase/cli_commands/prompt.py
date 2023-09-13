from typing import Optional

import typer
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from predibase.cli_commands.utils import df_to_table, get_client, get_console
from predibase.resource.llm.response import GeneratedResponse

app = typer.Typer(no_args_is_help=True)


@app.command(help="Query a Large Language Model (LLM)")
def llm(
    template: str = typer.Option(
        None,
        "--template",
        "-t",
        prompt="Template input",
        prompt_required=True,
        help="Prompt template input text",
    ),
    deployment_name: str = typer.Option(
        None,
        "--deployment-name",
        "-m",
        prompt="Deployment to prompt",
        prompt_required=True,
        help="The name of the deployment to prompt",
    ),
    index_name: Optional[str] = typer.Option(
        None,
        "--index-name",
        "-i",
        prompt_required=False,
        help="Optional dataset to index",
    ),
    dataset_name: Optional[str] = typer.Option(
        None,
        "--dataset-name",
        "-d",
        prompt_required=False,
        help="Optional dataset for batch inference",
    ),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", prompt_required=False, help="Optional results limit"),
):
    client = get_client()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Querying LLM...", total=None)
        responses = client.LLM(f"pb://deployments/{deployment_name}").prompt(
            template,
            # return_df=True,
        )
        df = GeneratedResponse.to_pandas(responses)

    table = Table(show_header=True, header_style="bold magenta")

    # Modify the table instance to have the data from the DataFrame
    table = df_to_table(df, table)

    # Update the style of the table
    table.row_styles = ["none", "dim"]
    table.box = box.SIMPLE_HEAD

    get_console().print(table)


if __name__ == "__main__":
    app()
