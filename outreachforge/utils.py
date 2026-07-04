import time
from langchain_groq import ChatGroq
from .config import settings
from .errors import ExternalAPIError
from .logger import log
from .resilience import retry, CircuitBreaker, ResilientProxy

_llm_circuit = CircuitBreaker(max_failures=3, reset_timeout=120)


from .tracing import get_tracer


def _create_llm() -> ChatGroq:
    tracer = get_tracer("outreachforge.utils")
    with tracer.start_as_current_span("llm.create"):
        try:
            llm = ChatGroq(api_key=settings.groq_api_key, model="mixtral-8x7b-32768")
            log("llm_initialized")
            return llm
        except Exception as exc:
            raise ExternalAPIError(f"LLM initialization failed: {exc}") from exc


@retry(max_attempts=3, base_delay=1.0, backoff_factor=2.0)
def get_llm():
    tracer = get_tracer("outreachforge.utils")
    with tracer.start_as_current_span("llm.get"):
        llm = _llm_circuit.call(_create_llm)
        return ResilientProxy(llm, _llm_circuit)
