from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID


class EventNamingPolicy:
    exchange_prefix = "app.scene-splitter"

    @classmethod
    def get_exchange_name(cls) -> str:
        return cls.exchange_prefix

    @classmethod
    def get_routing_key(cls, event_type: str) -> str:
        return event_type

    @classmethod
    def get_event_exchange_name(cls, event_type: str) -> str:
        return f"{cls.exchange_prefix}.{event_type}"


class BaseEvent(ABC):
    EVENT_TYPE: str = ""

    def __init__(self):
        self.timestamp = datetime.utcnow()
    
    @property
    def event_type(self) -> str:
        if not self.EVENT_TYPE:
            raise ValueError("EVENT_TYPE must be defined for event classes.")
        return self.EVENT_TYPE
    
    @property
    def exchange_name(self) -> str:
        return self.get_exchange_name()

    @property
    def routing_key(self) -> str:
        return self.get_routing_key()
    
    @abstractmethod
    def to_payload(self) -> Dict[str, Any]:
        pass

    @classmethod
    def get_exchange_name(cls) -> str:
        if not cls.EVENT_TYPE:
            raise ValueError("EVENT_TYPE must be defined for event classes.")
        return EventNamingPolicy.get_event_exchange_name(cls.EVENT_TYPE)

    @classmethod
    def get_routing_key(cls) -> str:
        if not cls.EVENT_TYPE:
            raise ValueError("EVENT_TYPE must be defined for event classes.")
        return EventNamingPolicy.get_routing_key(cls.EVENT_TYPE)

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, UUID):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'payload': {
                k: self._serialize_value(v) 
                for k, v in self.to_payload().items()
            }
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.event_type}>"


class EventRegistry:
    _events: Dict[str, type] = {}
    
    @classmethod
    def register(cls, event_class: type):
        if not issubclass(event_class, BaseEvent):
            raise TypeError(f"{event_class} must inherit from BaseEvent")

        event_type = event_class.EVENT_TYPE
        if not event_type:
            raise ValueError(f"{event_class.__name__} must define EVENT_TYPE.")

        cls._events[event_type] = event_class
        return event_class
    
    @classmethod
    def get_all_events(cls) -> Dict[str, type]:
        return cls._events.copy()
    
    @classmethod
    def get_event_class(cls, event_type: str) -> Optional[type]:
        return cls._events.get(event_type)
    
    @classmethod
    def list_event_types(cls) -> list:
        return list(cls._events.keys())


def event(cls):
    EventRegistry.register(cls)
    return cls
