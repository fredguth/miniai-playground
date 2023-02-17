# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/store.ipynb.

# %% ../nbs/store.ipynb 2
from __future__ import annotations
from typing import List, Callable, TypeVar,  Generic, Sequence, Union, Optional, Any, Set

# %% auto 0
__all__ = ['T', 'TSubscriber', 'TUnsubscriber', 'TUpdater', 'TStartStop', 'Readable', 'Writable', 'Subscriber']

# %% ../nbs/store.ipynb 4
T = TypeVar("T")

TSubscriber = Callable[[T], None]
TUnsubscriber = Callable[[], None]
TUpdater = Callable[[T], T]
TStartStop = Callable[[TSubscriber], Union[TUnsubscriber, None]]

    
class Readable(Generic[T]):
    def __init__(self, value: T, start: Optional[TStartStop]=None) -> None:
        self.value: T = value
        self.start: Optional[TStartStop] = start
        self.subscribers: set[TSubscriber] = set() # callback list

    def __getattr__(self, name):
        return getattr(self.value, name)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    def __str__(self) -> str: return str(self.value)

    def get(self) -> T: return self.value

    def _set(self, new_value: T) -> None:
        if new_value != self.value: self.value = new_value
        for subscriber in self.subscribers: subscriber(self.value)

    def subscribe(self, subscriber: TSubscriber) -> TUnsubscriber:
        self.subscribers.add(subscriber)
        subscriber(self.value)
        if (len(self.subscribers) == 1):
             if self.start is not None: 
                self.stop: Union[TUnsubscriber, None] =  self.start(self._set) 
        def unsubscribe()-> None:
            self.subscribers.remove(subscriber)
        if isinstance(subscriber, Subscriber): subscriber.add_subscription(unsubscribe)
        return unsubscribe

class Writable(Readable[T]):

    def set(self, new_value: T) -> None:
        self._set(new_value)
    
    def update(self, fn: TUpdater) -> None: self.set(fn(self.value))


class Subscriber(Generic[T]):
    """ Represents a subscriber (a callback) to a store (an observable)."""
    def __init__(self, fn: Callable[[T], None], observable: Optional[Union[Readable[T], Writable[T]]]) -> None:
        self.fn = fn
        self.subscriptions: Set[Callable[[], None]] = set()

    def __call__(self, value: T) -> None:
        self.fn(value)

    def __eq__(self, other: Callable[[T], None]) -> bool:
        return self.fn == other.fn

    def __hash__(self) -> int:
        return hash(self.fn)
    
    def __del__(self)-> None:
        for unsubscribe in self.subscriptions: unsubscribe()
        
    def add_subscription(self, unsubscribe: Callable[[], None])-> None:
        self.subscriptions.add(unsubscribe)
    
