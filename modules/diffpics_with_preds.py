import os
from .base import Base
import logging


class DiffPicsWithPreds(Base):

    def __init__(self, run_name, *args, **kwargs):
        super(DiffPicsWithPreds, self).__init__()
        self.run_name = run_name
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return 'DiffPicsWithPreds(%s)' % self.run_name

    def process(self, **kwargs):
        # find a way to figure out whether this is a retriggering
        if os.path.exists("%s/XDS_ASCII.HKL_hsymm" % self.dataset.process_dir):
            from jobs import diffpics_with_preds
            job = diffpics_with_preds.delay(self.dataset.process_dir)
            logging.info('Queued diffpics with preds calculation with id: %s' % job)
