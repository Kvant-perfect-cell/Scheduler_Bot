from abc import ABC, abstractmethod

class ScheduleRepository(ABC):
    @abstractmethod
    def get_schedule(self, group, date):
        pass