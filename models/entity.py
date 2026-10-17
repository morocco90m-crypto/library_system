from abc import ABC, abstractmethod


class Entity(ABC):
    def __init__(self, entity_id):
        self.__id = entity_id      # private, can't be changed from outside

    @property
    def id(self):                  # read only, no setter
        return self.__id

    @abstractmethod
    def to_dict(self):             # every child class must write this
        pass