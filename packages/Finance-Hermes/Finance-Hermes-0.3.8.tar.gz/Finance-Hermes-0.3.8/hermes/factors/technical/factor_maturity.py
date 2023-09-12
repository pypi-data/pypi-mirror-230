# -*- encoding:utf-8 -*-
from hermes.factors.base import FactorBase, LongCallMixin, ShortMixin
from hermes.factors.technical.core.maturity import *


class FactorMaturity(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'maturity'
        self.category = 'maturity'

    def _init_self(self, **kwargs):
        pass

    def MARSTS(self,
               data,
               drift=None,
               offset=None,
               dependencies=['recent', 'far', 'rinterval', 'finterval'],
               **kwargs):
        result = marsts(data['recent'],
                        data['far'],
                        data['rinterval'],
                        data['finterval'],
                        drift=drift,
                        offset=offset,
                        **kwargs)
        return self._format(result, f"MARSTS")

    def PLUTOTS(self,
                data,
                drift=None,
                offset=None,
                dependencies=['main', 'second', 'minterval', 'sinterval'],
                **kwargs):
        result = plutots(data['main'],
                         data['second'],
                         data['minterval'],
                         data['sinterval'],
                         drift=drift,
                         offset=offset,
                         **kwargs)
        return self._format(result, f"PLUTOTS")

    def COMENTTS(self,
                 data,
                 drift=None,
                 offset=None,
                 dependencies=['main', 'far', 'minterval', 'finterval'],
                 **kwargs):
        result = comentts(data['main'],
                          data['far'],
                          data['minterval'],
                          data['finterval'],
                          drift=drift,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"COMENTTS")

    def ARIESTS(self,
                data,
                drift=None,
                offset=None,
                dependencies=['recent', 'second', 'rinterval', 'sinterval'],
                **kwargs):
        result = ariests(data['recent'],
                         data['second'],
                         data['rinterval'],
                         data['sinterval'],
                         drift=drift,
                         offset=offset,
                         **kwargs)
        return self._format(result, f"ARIESTS")

    def MARSTSMOM(self,
                  data,
                  length=None,
                  offset=None,
                  dependencies=['recent', 'far'],
                  **kwargs):
        length = int(length) if isinstance(length, int) else 20
        result = marstsmom(data['recent'],
                           data['far'],
                           length=length,
                           offset=offset,
                           **kwargs)
        return self._format(result, f"MARSTSMOM_{length}")

    def PLUTOTSMOM(self,
                   data,
                   length=None,
                   offset=None,
                   dependencies=['main', 'second'],
                   **kwargs):
        length = int(length) if isinstance(length, int) else 20
        result = plutotsmom(data['main'],
                            data['second'],
                            length=length,
                            offset=offset,
                            **kwargs)
        return self._format(result, f"PLUTOTSMOM_{length}")

    def COMENTTSMOM(self,
                    data,
                    length=None,
                    offset=None,
                    dependencies=['main', 'far'],
                    **kwargs):
        length = int(length) if isinstance(length, int) else 20
        result = comenttsmom(data['main'],
                             data['far'],
                             length=length,
                             offset=offset,
                             **kwargs)
        return self._format(result, f"COMENTTSMOM_{length}")

    def ARIESTSMOM(self,
                   data,
                   length=None,
                   offset=None,
                   dependencies=['recent', 'second'],
                   **kwargs):
        length = int(length) if isinstance(length, int) else 20
        result = ariestsmom(data['recent'],
                            data['second'],
                            length=length,
                            offset=offset,
                            **kwargs)
        return self._format(result, f"ARIESTSMOM_{length}")
