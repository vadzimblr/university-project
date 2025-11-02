from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID


class BaseEvent(ABC):
    def __init__(self):
        self.timestamp = datetime.utcnow()
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        pass
    
    @property
    @abstractmethod
    def exchange_name(self) -> str:
        pass

    @property
    @abstractmethod
    def routing_key(self) -> str:
        pass
    
    @abstractmethod
    def to_payload(self) -> Dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def get_exchange_name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_routing_key(cls) -> str:
        pass

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
        
        temp_instance = event_class.__new__(event_class)
        event_type = event_class.event_type.fget(temp_instance)
        
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
