from typing import List, Optional, Union

from promptquality.constants.scorers import Scorers
from promptquality.get_metrics import get_metrics
from promptquality.helpers import (
    create_job,
    create_project,
    create_run,
    create_template,
    upload_custom_metrics,
    upload_dataset,
)
from promptquality.job_progress import job_progress
from promptquality.set_config import set_config
from promptquality.types.config import Config
from promptquality.types.custom_scorer import CustomScorer
from promptquality.types.run import PromptMetrics
from promptquality.types.settings import Settings
from promptquality.utils.dataset import DatasetType
from promptquality.utils.name import ts_run_name
from promptquality.utils.scorer import bifurcate_scorers


def run(
    template: str,
    dataset: DatasetType,
    project_name: Optional[str] = None,
    run_name: Optional[str] = None,
    template_name: Optional[str] = None,
    scorers: Optional[List[Union[Scorers, CustomScorer]]] = None,
    settings: Optional[Settings] = None,
    wait: bool = True,
    silent: bool = False,
    config: Optional[Config] = None,
) -> Optional[PromptMetrics]:
    config = config or set_config()
    # Create project.
    project = create_project(project_name, config)
    # Create template.
    template_response = create_template(
        template,
        project.id,
        # Use project name as template name if not provided.
        template_name=template_name or project.name,
        config=config,
    )
    # Upload dataset.
    dataset_id = upload_dataset(
        dataset,
        project.id,
        template_response.selected_version_id,
        config,
    )
    # Run prompt.
    run_id = create_run(
        project.id,
        run_name=run_name
        or ts_run_name(
            template_response.name, template_response.selected_version.version
        ),
        config=config,
    )
    galileo_scorers, custom_scorers = bifurcate_scorers(scorers)
    job_id = create_job(
        project.id,
        run_id,
        dataset_id,
        template_response.selected_version_id,
        settings,
        galileo_scorers,
        config,
    )
    if wait:
        job_progress(job_id, config)
    if not silent:
        print(f"🔭 View your prompt run on the Galileo console at: {config.run_url}")
    if custom_scorers:
        for scorer in custom_scorers:
            upload_custom_metrics(
                scorer, project_id=project.id, run_id=run_id, config=config
            )
    return get_metrics(
        project_id=project.id, run_id=run_id, job_id=job_id, config=config
    )
