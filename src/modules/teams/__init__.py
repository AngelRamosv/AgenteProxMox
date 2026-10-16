"""
Módulo de Integración con Microsoft Teams.
"""
from src.modules.teams.reader import (
    read_latest_message_from_group,
    read_last_message_text_plus_image_ocr,
    teams_find_chat_item,
    is_chat_unread,
)
from src.modules.teams.sender import send_teams_message

__all__ = [
    "read_latest_message_from_group",
    "read_last_message_text_plus_image_ocr",
    "teams_find_chat_item",
    "is_chat_unread",
    "send_teams_message",
]
