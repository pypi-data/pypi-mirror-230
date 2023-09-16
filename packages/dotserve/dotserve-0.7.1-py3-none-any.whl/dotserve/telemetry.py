from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opentelemetry.sdk.resources import Attributes, Resource
    from opentelemetry.trace import Tracer

import hashlib
import logging
from functools import wraps
from socket import gethostname

import uptrace
from dotserve.config import config
from dotserve.version import __version__


class DotserveTelemetry:
    def __init__(self):
        self._tracer = None

    # Patch uptrace.py to hash the hostname to avoid leaking it.
    @staticmethod
    def _build_resource(
        resource: "Resource",
        resource_attributes: "Attributes",
        service_name: str,
        service_version: str,
        deployment_environment: str,
    ) -> "Resource":
        from opentelemetry.sdk.resources import Resource

        if resource:
            return resource

        # If we are in production, use the URL as hostname
        if config.dotserve_prod_url:
            host_name = config.dotserve_prod_url
        # Hash the local hostname to avoid leaking it.
        else:
            host_name = gethostname()
            host_name = hashlib.sha256(host_name.encode("UTF-8")).hexdigest()

        attrs = {"host.name": host_name}

        if resource_attributes:
            attrs.update(resource_attributes)
        if service_name:
            attrs["service.name"] = service_name
        if service_version:
            attrs["service.version"] = service_version
        if deployment_environment:
            attrs["deployment.environment"] = deployment_environment

        return Resource.create(attrs)

    def configure_tracer(self):
        from opentelemetry.exporter.otlp.proto.grpc.exporter import (
            logger as exporter_logger,
        )
        from opentelemetry.trace import get_tracer

        if self._tracer:
            return self._tracer

        uptrace.uptrace._build_resource = self._build_resource

        uptrace.configure_opentelemetry(
            dsn="https://YPa4AbDF853uCW6UWN2oYg@api.uptrace.dev/1778",
            service_name="dotserve",
            service_version="1.1.0",
            deployment_environment="production",
            logging_level=logging.CRITICAL,
        )

        exporter_logger.setLevel(logging.CRITICAL)

        tracer = get_tracer("dotserve", __version__)
        return tracer

    @property
    def tracer(self) -> "Tracer":
        if self._tracer is None:
            self._tracer = self.configure_tracer()

        return self._tracer


dotserve_telemetry = DotserveTelemetry()


def trace_event(event_name):
    if config.project.enable_telemetry:
        with dotserve_telemetry.tracer.start_as_current_span(
            event_name, record_exception=False, set_status_on_exception=False
        ):
            return


def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if config.project.enable_telemetry:
            event_name = func.__name__
            with dotserve_telemetry.tracer.start_as_current_span(
                event_name, record_exception=False, set_status_on_exception=False
            ):
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    return wrapper
