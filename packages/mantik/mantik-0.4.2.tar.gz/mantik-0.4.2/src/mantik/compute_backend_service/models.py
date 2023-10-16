"""Request models."""
import pydantic


class SubmitRunResponse(pydantic.BaseModel):
    """
    Model for submitted run response.

    Attributes
    ----------
    experiment_id: Experiment id.
    run_id: Run id.
    unicore_job_id: Unicore Job id.
    """

    experiment_id: int
    run_id: str
    unicore_job_id: str
