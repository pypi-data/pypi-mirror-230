"""Falcon SSMs."""


from openssm.core.ssm.base_ssm import BaseSSM
from openssm.core.adapter.abstract_adapter import AbstractAdapter
from openssm.core.backend.abstract_backend import AbstractBackend
from openssm.integrations.huggingface.slm import Falcon7bSLM


class Falcon7bSSM(BaseSSM):
    """Falcon 7-billion-parameter SSM."""

    def __init__(self,
                 adapter: AbstractAdapter = None,
                 backends: list[AbstractBackend] = None):
        """Initialize Falcon 7-billion-parameter SSM."""
        super().__init__(Falcon7bSLM(), adapter, backends)
