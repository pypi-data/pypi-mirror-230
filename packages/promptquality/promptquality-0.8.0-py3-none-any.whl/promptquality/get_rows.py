from typing import Optional

from pydantic import UUID4

from promptquality.set_config import set_config
from promptquality.types.config import Config
from promptquality.types.rows import GetRowsRequest, PromptRows


def get_rows(
    project_id: Optional[UUID4] = None,
    run_id: Optional[UUID4] = None,
    config: Optional[Config] = None,
) -> PromptRows:
    config = config or set_config()
    project_id = project_id or config.current_project_id
    if not project_id:
        raise ValueError("project_id must be provided")
    run_id = run_id or config.current_run_id
    if not run_id:
        raise ValueError("run_id must be provided")
    rows_json = config.api_client.get_rows(
        GetRowsRequest(project_id=project_id, run_id=run_id)
    )
    return PromptRows.model_validate(rows_json)
