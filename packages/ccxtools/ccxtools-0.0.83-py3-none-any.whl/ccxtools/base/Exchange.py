from abc import ABCMeta, abstractmethod


class Exchange(metaclass=ABCMeta):

    @abstractmethod
    def get_balance(self, ticker):
        raise NotImplementedError
