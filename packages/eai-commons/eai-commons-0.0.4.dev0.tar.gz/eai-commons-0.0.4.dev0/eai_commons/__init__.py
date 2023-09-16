from typing import Optional
from contextvars import ContextVar

trace_id_context: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
