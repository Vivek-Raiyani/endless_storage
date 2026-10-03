"""
Service-layer exceptions
========================
Services raise these instead of HTTPException so they stay framework-agnostic.
Routes translate them to HTTP status codes via `to_http()`.
"""
from fastapi import HTTPException


class ServiceError(Exception):
    status_code = 400


class NotFoundError(ServiceError):
    status_code = 404


class ForbiddenError(ServiceError):
    status_code = 403


class ConflictError(ServiceError):
    status_code = 409


def to_http(e: Exception) -> HTTPException:
    """Map a service exception (or legacy ValueError) to an HTTPException."""
    if isinstance(e, ServiceError):
        return HTTPException(status_code=e.status_code, detail=str(e))
    return HTTPException(status_code=400, detail=str(e))
