"""
Simple user mapping service for Behflow.
Maps external user identifiers (strings) to persistent UUIDs.
This is an in-memory placeholder for a real user registry or DB table.
"""
from uuid import UUID, uuid4
from typing import Dict
from shared.logger import get_logger

logger = get_logger(__name__)

_USER_MAP: Dict[str, UUID] = {}


def get_or_create_user_uuid(external_id: str) -> UUID:
    """Return the UUID for an external user identifier, creating one if missing.

    Args:
        external_id: External user id (e.g., an auth subject or username)

    Returns:
        UUID assigned to that external id
    """
    if external_id in _USER_MAP:
        logger.debug("Found existing UUID for external_id=%s", external_id)
        return _USER_MAP[external_id]
    uid = uuid4()
    _USER_MAP[external_id] = uid
    logger.info("Created new UUID %s for external_id=%s", uid, external_id)
    return uid


def get_user_uuid(external_id: str) -> UUID | None:
    return _USER_MAP.get(external_id)
