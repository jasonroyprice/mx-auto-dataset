import logbook

class Base(object):
    def __init__(self):
        self.logger = logbook.Logger(self.__class__.__name__)

    def _setup_vars(self, kwargs):
        self.__dict__.update(kwargs)

    def process(self, **kwargs):
        pass

    def __repr__(self, ):
        return '%s()' % (self.__class__.__name__, )

    def __getattr__(self, attr):
        try:
            return getattr(self.input, attr)
        except AttributeError:
            return getattr(self.output, attr)

#define a class for when we expect process to return an updated list of options
class ReturnOptions(Base):
    pass