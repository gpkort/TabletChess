from collections.abc import Callable
from abc import ABC
from enum import Enum
from dataclasses import dataclass
from typing import Any
import threading

class Event(Enum):
    NEW_GAME = 1
    QUIT_CURRENT = 2
    QUIT = 3
    NEW_PUZZLE = 4
    SQUARE_CLICK = 5
    PUZZLE_SELECT = 6
    LOAD_GAME = 7
    LOAD_PUZZLE = 8
    UNKNOWN = 99

@dataclass(frozen=True)
class EventHandler:
    event_type: Event
    handler: Callable[[Event, dict[str, Any]], None]
    blocking: bool = False

class EventDispatcher(ABC):
    def __init__(self):
        self._event_handlers: dict[int, EventHandler] = {}
        self._lock = threading.Lock()
        self._all_listeners:dict[int, list[int]] = {}
        
    def register_handler(self, event_handler: EventHandler) -> int:
        handler_id:int = hash(event_handler)

        with self._lock:
            self._event_handlers[handler_id] = event_handler
        return handler_id

    def register_all_events(self, listener:object, callback: Callable[[Event, dict[str, Any]], None]):
        self.unregister_all_events(listener)

        for event in Event:
            self._all_listeners[id(listener)] = self.register_handler(EventHandler(event, callback))  #type: ignore

    def unregister_all_events(self, listener:object):
            for hid in self._all_listeners.get(id(listener), []):
                self.unregister_handler(hid)  
    
    def register_handlers(self, event_handlers: list[EventHandler]) -> list[int]:
        handler_ids = []
        for event_handler in event_handlers:
            handler_id = self.register_handler(event_handler)
            handler_ids.append(handler_id)
        return handler_ids
    
    def unregister_handler(self, handler_id: int) -> bool:
        ret:bool = False

        with self._lock:
            if  self._event_handlers.get(handler_id) is not None:
                self._event_handlers.pop(handler_id)
                ret = True

        return ret
            
    def unregister_handlers(self, handler_ids: list[int]) -> None:
        for handler_id in handler_ids:
            self.unregister_handler(handler_id)

    def unregister_all_handlers(self) -> None:
        with self._lock:
            self._event_handlers.clear()
    
    def _dispatch(self, event:Event, data: dict[str, Any] | None = None): 
        if data is None:
            data = {}

        with self._lock:
            current_observers = self._event_handlers.copy()
        
        for handler in reversed(list(current_observers.values())):
            if handler.event_type == event:
                handler.handler(event, data)
                if handler.blocking:
                    break
