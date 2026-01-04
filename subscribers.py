"""
Subscriber management for weather alerts.
Handles adding/removing subscribers and retrieving the list.
"""

import json
import os
from typing import List, Set
from pathlib import Path


SUBSCRIBERS_FILE = "subscribers.json"


def _load_subscribers() -> Set[str]:
    """Load subscribers from file."""
    if not os.path.exists(SUBSCRIBERS_FILE):
        return set()
    
    try:
        with open(SUBSCRIBERS_FILE, 'r') as f:
            data = json.load(f)
            return set(str(s) for s in data.get('subscribers', []))
    except Exception:
        return set()


def _save_subscribers(subscribers: Set[str]):
    """Save subscribers to file."""
    with open(SUBSCRIBERS_FILE, 'w') as f:
        json.dump({'subscribers': sorted(list(subscribers))}, f, indent=2)


def add_subscriber(chat_id: str) -> bool:
    """
    Add a subscriber.
    
    Args:
        chat_id: Telegram chat ID
        
    Returns:
        True if added, False if already subscribed
    """
    subscribers = _load_subscribers()
    
    if chat_id in subscribers:
        return False
    
    subscribers.add(chat_id)
    _save_subscribers(subscribers)
    return True


def remove_subscriber(chat_id: str) -> bool:
    """
    Remove a subscriber.
    
    Args:
        chat_id: Telegram chat ID
        
    Returns:
        True if removed, False if not subscribed
    """
    subscribers = _load_subscribers()
    
    if chat_id not in subscribers:
        return False
    
    subscribers.remove(chat_id)
    _save_subscribers(subscribers)
    return True


def get_subscribers() -> List[str]:
    """Get list of all subscribers."""
    return list(_load_subscribers())


def is_subscribed(chat_id: str) -> bool:
    """Check if a chat ID is subscribed."""
    return chat_id in _load_subscribers()


def get_all_chat_ids(config_chat_ids: List[str] = None) -> List[str]:
    """
    Get all chat IDs (config + subscribers).
    
    Args:
        config_chat_ids: Chat IDs from config file
        
    Returns:
        Combined list of unique chat IDs
    """
    all_ids = set(get_subscribers())
    
    if config_chat_ids:
        all_ids.update(str(id) for id in config_chat_ids)
    
    return list(all_ids)

