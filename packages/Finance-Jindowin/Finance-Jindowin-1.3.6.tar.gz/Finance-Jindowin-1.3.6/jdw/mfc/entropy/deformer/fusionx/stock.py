from jdw.mfc.entropy.deformer.fusionx.base import Base


class Stock(Base):

    def __init__(self,
                 batch,
                 freq,
                 horizon,
                 offset,
                 id=None,
                 directory=None,
                 is_full=False):
        super(Stock, self).__init__(batch=batch,
                                    freq=freq,
                                    horizon=horizon,
                                    offset=offset,
                                    id=id,
                                    directory=directory,
                                    is_full=is_full)
