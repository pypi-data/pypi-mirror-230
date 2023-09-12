"""OpenSSM Contrib."""


from collections.abc import Sequence

from .streamlit_chatssm import ChatSSMComponent as ChatSSMStreamlitComponent


__all__: Sequence[str] = (
    'ChatSSMStreamlitComponent',
)
