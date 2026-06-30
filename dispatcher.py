from collections.abc import Callable
from collections import deque
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Any
import threading

class Event(Enum):
    FORWARD = 1
    BACKWARD = 2
    UP = 3
    DOWN = 4
    RIGHT = 5
    LEFT = 6
    ENTER = 7
    QUIT = 8
    APP_BACK = 9
    PAGE_NEXT = 10
    PAGE_PREVIOUS = 11
    UNKNOWN = 99

@dataclass(frozen=True)
class EventHandler:
    event_type: Event
    handler: Callable[[dict[str, Any]], None]
    blocking: bool = False

class EventDispatcher(ABC):
    def __init__(self):
        self.event_handlers: dict[int, EventHandler] = {}
        self.lock = threading.Lock()
        
    def register_handler(self, event_handler: EventHandler) -> int:
        handler_id:int = hash(event_handler)

        with self.lock:
            self.event_handlers[handler_id] = event_handler
        return handler_id
    
    def register_handlers(self, event_handlers: list[EventHandler]) -> list[int]:
        handler_ids = []
        for event_handler in event_handlers:
            handler_id = self.register_handler(event_handler)
            handler_ids.append(handler_id)
        return handler_ids
    
    def unregister_handler(self, handler_id: int) -> bool:
        ret:bool = False

        with self.lock:
            if handler_id in self.event_handlers:
                self.event_handlers.pop(handler_id)
                ret = True

        return ret
            
    def unregister_handlers(self, handler_ids: list[int]) -> None:
        for handler_id in handler_ids:
            self.unregister_handler(handler_id)

    def unregister_all_handlers(self) -> None:
        with self.lock:
            self.event_handlers.clear()
    
    def _dispatch(self, event:Event, data: dict[str, Any] | None = None): 
        if data is None:
            data = {}

        with self.lock:
            current_observers = self.event_handlers.copy()
        
        for handler in reversed(list(current_observers.values())):
            if handler.event_type == event:
                handler.handler(data)
                if handler.blocking:
                    break
    
    
                
    