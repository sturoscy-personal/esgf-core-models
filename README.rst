esgf-core-models
================

The shared data definitions for the ESGF core architecture, as a small
standalone package.

ESGF's core services (publishers, consumers, and the services that process
their events) pass STAC items around as Kafka messages. For those services to
interoperate, they all need to agree on what a message, a permission or an
error looks like. These Pydantic models and exceptions are that agreement.

They were originally part of
`esgf-core-utils <https://github.com/ESGF/esgf-core-utils>`_, which also
contains a Kafka producer and consumer, STAC validation and settings. Using the
models from there means installing all of those dependencies too. This package
contains only the models, so a project that has its own Kafka client, or none
at all, can still use the same definitions without the extra weight. Its
dependencies are ``pydantic``, ``stac-pydantic`` and ``stac-fastapi.extensions``.

Install
-------

Add it to a project managed by `uv <https://docs.astral.sh/uv/>`_::

    uv add esgf-core-models

Or install it into an existing virtual environment::

    uv pip install esgf-core-models

Requires Python 3.12 or newer.

Documentation
-------------

The models are documented in the ``esgf-core-utils`` API reference. Only the
modules below are in this package. The ``consumer``, ``producer``,
``message_processor``, ``validation`` and ``settings`` pages describe code that
stays in ``esgf-core-utils``.

Replace ``esgf_core_utils.models`` with ``esgf_core_models`` in the import
paths shown there.

.. list-table::
   :header-rows: 1

   * - This package
     - Reference page
   * - ``esgf_core_models.kafka.events``
     - `events <https://esgf.github.io/esgf-core-utils/autoapi/esgf_core_utils/models/kafka/events/index.html>`__
   * - ``esgf_core_models.kafka.config``
     - `config <https://esgf.github.io/esgf-core-utils/autoapi/esgf_core_utils/models/kafka/config/index.html>`__
   * - ``esgf_core_models.auth``
     - `auth <https://esgf.github.io/esgf-core-utils/autoapi/esgf_core_utils/models/auth/index.html>`__
   * - ``esgf_core_models.exceptions``
     - `exceptions <https://esgf.github.io/esgf-core-utils/autoapi/esgf_core_utils/models/exceptions/index.html>`__
   * - ``esgf_core_models.aggregation_assets``
     - `aggregation_assets <https://esgf.github.io/esgf-core-utils/autoapi/esgf_core_utils/models/aggregation_assets/index.html>`__

Examples
--------

Parse a Kafka event. ``KafkaEvent`` picks the payload type from ``method``
(``POST``, ``PUT`` or ``PATCH``)::

    from esgf_core_models.kafka.events import KafkaEvent, PatchPayload

    event = KafkaEvent.model_validate_json(message_value)

    if isinstance(event.data.payload, PatchPayload):
        print(event.data.payload.item_id, event.data.payload.patch)

Build Kafka client settings. Fields accept either the Python name or the
Kafka property name::

    from esgf_core_models.kafka.config import KafkaConsumerConfig

    config = KafkaConsumerConfig(
        **{
            "bootstrap.servers": "kafka.example.org:9093",
            "sasl.username": "user",
            "sasl.password": "secret",
            "group.id": "my-consumer",
        }
    )
    # Pass the Kafka property names to confluent-kafka (or your own client):
    client_config = config.model_dump(by_alias=True, exclude_none=True)

Check that a publisher may act on a project and its asset hosts. Entitlement
strings are matched against your own regular expression, which must define
the named groups ``type`` (``project`` or ``node``), ``id`` and ``role``::

    from esgf_core_models.auth import Authorizer
    from esgf_core_models.exceptions import AuthorizationException
    from esgf_core_models.kafka.events import RequesterData

    authorizer = Authorizer(
        requester_data=RequesterData(client_id="c", iss="https://idp", sub="u"),
        regex=r"^(?P<type>project|node):(?P<id>[^:]+):(?P<role>[A-Z]+)$",
    )
    authorizer.add(["project:CMIP6:CREATE", "node:data.example.org:CREATE"])

    try:
        authorizer.authorize(
            collection_id="CMIP6",
            item=item,  # an stac_pydantic Item
            role="CREATE",
            request_id="req-1",
            event_id="evt-1",
        )
    except AuthorizationException as exc:
        print(exc.rfc945response())  # RFC 9457 problem details

Return RFC 9457 problem details from any of the exceptions::

    from esgf_core_models.exceptions import ItemDoesNotExistException

    exc = ItemDoesNotExistException("CMIP6", "some-item-id", instance="req-1:evt-1")
    exc.rfc945response()
