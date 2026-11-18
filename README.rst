esgf-core-models
================

Pydantic models and exceptions for the ESGF core architecture, split out of
`esgf-core-utils <https://github.com/ESGF/esgf-core-utils>`_ so consumers can
share the data definitions without pulling in Kafka, jsonschema, shapely,
requests and the rest of that package's dependencies.

Install::

    pip install esgf-core-models

Contents
--------

* ``esgf_core_models.kafka.events``: Kafka message payload models
* ``esgf_core_models.kafka.config``: Kafka producer/consumer config models
* ``esgf_core_models.auth``: permission and authorizer models
* ``esgf_core_models.exceptions``: RFC 9457 exceptions
* ``esgf_core_models.aggregation_assets``: aggregated asset constants

Migrating from esgf-core-utils
------------------------------

Replace ``esgf_core_utils.models.<x>`` with ``esgf_core_models.<x>``.
Kafka producer/consumer classes and the validation functions remain in
``esgf-core-utils``.
