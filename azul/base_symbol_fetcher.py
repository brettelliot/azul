import logbook

log = logbook.Logger('BaseSymbolFetcher')


class BaseSymbolFetcher(object):

    def __init__(self):
        pass

    def symbols(self):
        """
        Returns the list of symbols that were fetched.

        Returns:
            symbols (list): list of symbols that were fetched.

        """
        raise NotImplementedError
