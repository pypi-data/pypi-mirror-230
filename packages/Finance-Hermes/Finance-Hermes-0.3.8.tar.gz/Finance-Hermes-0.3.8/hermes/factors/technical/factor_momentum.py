# -*- encoding:utf-8 -*-
import copy
from hermes.factors.base import FactorBase, LongCallMixin, ShortMixin
from hermes.factors.technical.core.momentum import *


class FactorMomentum(FactorBase, LongCallMixin, ShortMixin):

    def __init__(self, **kwargs):
        __str__ = 'momentum'
        self.category = 'momentum'

    def _init_self(self, **kwargs):
        pass

    def ANNEALN(self,
                data,
                length=None,
                offset=None,
                dependencies=['high', 'low'],
                **kwargs):
        length = int(length) if length and length > 0 else 14
        result = annealn(copy.deepcopy(data['high']),
                         copy.deepcopy(data['low']),
                         copy.deepcopy(data['close']),
                         length=length,
                         offset=offset,
                         **kwargs)
        return self._format(result, f"Annealn_{length}")

    def AO(self,
           data,
           fast=None,
           slow=None,
           offset=None,
           dependencies=['high', 'low'],
           **kwargs):
        fast = int(fast) if fast and fast > 0 else 5
        slow = int(slow) if slow and slow > 0 else 34
        result = ao(copy.deepcopy(data['high']),
                    copy.deepcopy(data['low']),
                    fast=fast,
                    slow=slow,
                    offset=offset,
                    **kwargs)
        return self._format(result, f"AO_{fast}_{slow}")

    def APO(self,
            data,
            fast=None,
            slow=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        fast = int(fast) if fast and fast > 0 else 12
        slow = int(slow) if slow and slow > 0 else 26

        result = apo(copy.deepcopy(data['close']),
                     fast=fast,
                     slow=slow,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"APO_{fast}_{slow}")

    def BIAS(self,
             data,
             length=None,
             offset=None,
             dependencies=['close'],
             **kwargs):
        length = int(length) if length and length > 0 else 26
        result = bias(copy.deepcopy(data['close']),
                      length=length,
                      offset=offset,
                      **kwargs)
        return self._format(result, f"BIAS_{length}")

    def BOP(self,
            data,
            scalar=None,
            offset=None,
            dependencies=['open', 'high', 'low', 'close'],
            **kwargs):
        result = bop(copy.deepcopy(data['open']),
                     copy.deepcopy(data['high']),
                     copy.deepcopy(data['low']),
                     copy.deepcopy(data['close']),
                     scalar=scalar,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"BOP")

    def BRAR(self,
             data,
             length=None,
             scalar=None,
             drift=None,
             offset=None,
             dependencies=['open', 'high', 'low', 'close'],
             **kwargs):
        length = int(length) if length and length > 0 else 26
        ar, br = brar(copy.deepcopy(data['open']),
                      copy.deepcopy(data['high']),
                      copy.deepcopy(data['low']),
                      copy.deepcopy(data['close']),
                      length=length,
                      scalar=scalar,
                      drift=drift,
                      offset=offset,
                      **kwargs)
        ar = self._format(ar, f"BRARar_{length}")
        br = self._format(br, f"BRARbr_{length}")
        return ar, br

    def CHKBAR(self,
               data,
               length=None,
               offset=None,
               dependencies=['high', 'close'],
               **kwargs):
        length = int(length) if length and length > 0 else 5
        result = chkbar(copy.deepcopy(data['close']),
                        copy.deepcopy(data['high']),
                        length=length,
                        offset=offset,
                        **kwargs)
        return self._format(result, f"CHKBAR_{length}")

    def CLKBAR(self,
               data,
               length=None,
               offset=None,
               dependencies=['low', 'close'],
               **kwargs):
        length = int(length) if length and length > 0 else 5
        result = clkbar(copy.deepcopy(data['close']),
                        copy.deepcopy(data['low']),
                        length=length,
                        offset=offset,
                        **kwargs)
        return self._format(result, f"CLKBAR_{length}")

    def CCI(self,
            data,
            length=None,
            c=None,
            offset=None,
            dependencies=['high', 'low', 'close'],
            **kwargs):
        length = int(length) if length and length > 0 else 14
        c = float(c) if c and c > 0 else 0.015
        result = cci(copy.deepcopy(data['high']),
                     copy.deepcopy(data['low']),
                     copy.deepcopy(data['close']),
                     length=length,
                     c=c,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"CCI_{length}_{int(c)}")

    def CG(self,
           data,
           length=None,
           offset=None,
           dependencies=['close'],
           **kwargs):
        length = int(length) if length and length > 0 else 10
        result = cg(copy.deepcopy(data['close']),
                    length=length,
                    offset=offset,
                    **kwargs)
        return self._format(result, f"CG_{length}")

    def CMO(self,
            data,
            length=None,
            scalar=None,
            drift=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 14
        result = cmo(copy.deepcopy(data['close']),
                     length=length,
                     scalar=scalar,
                     drift=drift,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"CMO_{length}")

    def COPPOCK(self,
                data,
                length=None,
                fast=None,
                slow=None,
                offset=None,
                dependencies=['close'],
                **kwargs):
        length = int(length) if length and length > 0 else 10
        fast = int(fast) if fast and fast > 0 else 11
        slow = int(slow) if slow and slow > 0 else 14
        result = coppock(copy.deepcopy(data['close']),
                         length=length,
                         fast=fast,
                         slow=slow,
                         offset=offset,
                         **kwargs)
        return self._format(result, f"COPC_{fast}_{slow}_{length}")

    def DNCHVOLATILITY(self,
                       data,
                       length=None,
                       offset=None,
                       dependencies=['close', 'low'],
                       **kwargs):
        length = int(length) if length and length > 0 else 5
        result = dnclvolatility(copy.deepcopy(data['close']),
                                copy.deepcopy(data['low']),
                                length=length,
                                offset=offset,
                                **kwargs)
        return self._format(result, f"DNCLVolatility_{length}")

    def DNLLVOLATILITY(self,
                       data,
                       length=None,
                       offset=None,
                       dependencies=['low'],
                       **kwargs):
        length = int(length) if length and length > 0 else 5
        result = dnllvolatility(copy.deepcopy(data['low']),
                                length=length,
                                offset=offset,
                                **kwargs)
        return self._format(result, f"DNLLVolatility_{length}")

    def DM(self,
           data,
           length=None,
           drift=None,
           offset=None,
           dependencies=['high', 'low'],
           **kwargs):
        length = int(length) if length and length > 0 else 14
        pos, neg = dm(copy.deepcopy(data['high']),
                      copy.deepcopy(data['low']),
                      length=length,
                      drift=drift,
                      offset=offset,
                      **kwargs)
        pos = self._format(pos, f"DMpos_{length}")
        neg = self._format(neg, f"DMneg_{length}")
        return pos, neg

    def ER(self,
           data,
           length=None,
           drift=None,
           offset=None,
           dependencies=['close'],
           **kwargs):
        length = int(length) if length and length > 0 else 10
        result = er(copy.deepcopy(data['close']),
                    length=length,
                    drift=drift,
                    offset=offset,
                    **kwargs)
        return self._format(result, f"ER_{length}")

    def ERI(self,
            data,
            length=None,
            offset=None,
            dependencies=['high', 'low', 'close'],
            **kwargs):
        length = int(length) if length and length > 0 else 13
        bull, bear = eri(copy.deepcopy(data['high']),
                         copy.deepcopy(data['low']),
                         copy.deepcopy(data['close']),
                         length=length,
                         offset=offset,
                         **kwargs)
        bull = self._format(bull, f"ERIbull_{length}")
        bear = self._format(bear, f"ERIbear_{length}")
        return bull, bear

    def EFFRATIO(self,
                 data,
                 length=None,
                 offset=None,
                 dependencies=['close'],
                 **kwargs):
        length = int(length) if length and length > 0 else 14
        result = effratio(copy.deepcopy(data['close']),
                          length=length,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"EffRatio_{length}")

    def INTRADAY(self,
                 data,
                 length=None,
                 offset=None,
                 dependencies=['open', 'close'],
                 **kwargs):
        length = int(length) if length and length > 0 else 5
        result = intraday(copy.deepcopy(data['open']),
                          copy.deepcopy(data['close']),
                          length=length,
                          offset=offset,
                          **kwargs)
        return self._format(result, f"Intraday_{length}")

    def KDJ(self,
            data,
            length=None,
            signal=None,
            offset=None,
            dependencies=['high', 'low', 'close'],
            **kwargs):
        length = int(length) if length and length > 0 else 9
        k, d, j = kdj(copy.deepcopy(data['high']),
                      copy.deepcopy(data['low']),
                      copy.deepcopy(data['close']),
                      length=length,
                      signal=signal,
                      offset=offset,
                      **kwargs)
        k = self._format(k, f"KDJ_K_{length}")
        d = self._format(d, f"KDJ_D_{length}")
        j = self._format(j, f"KDJ_J_{length}")
        return k, d, j

    def KST(self,
            data,
            roc1=None,
            roc2=None,
            roc3=None,
            roc4=None,
            sma1=None,
            sma2=None,
            sma3=None,
            sma4=None,
            signal=None,
            drift=None,
            offset=None,
            dependencies=['close'],
            **kwargs):

        roc1 = int(roc1) if roc1 and roc1 > 0 else 10
        roc2 = int(roc2) if roc2 and roc2 > 0 else 15
        roc3 = int(roc3) if roc3 and roc3 > 0 else 20
        roc4 = int(roc4) if roc4 and roc4 > 0 else 30

        sma1 = int(sma1) if sma1 and sma1 > 0 else 10
        sma2 = int(sma2) if sma2 and sma2 > 0 else 10
        sma3 = int(sma3) if sma3 and sma3 > 0 else 10
        sma4 = int(sma4) if sma4 and sma4 > 0 else 15

        result, kst_signal = kst(copy.deepcopy(data['close']),
                                 roc1=roc1,
                                 roc2=roc2,
                                 roc3=roc3,
                                 roc4=roc4,
                                 sma1=sma1,
                                 sma2=sma2,
                                 sma3=sma3,
                                 sma4=sma4,
                                 signal=signal,
                                 drift=drift,
                                 offset=offset,
                                 **kwargs)

        result = self._format(result, f"KST_{roc1}_{roc2}_{roc3}_{roc4}")
        kst_signal = self._format(kst_signal,
                                  f"KSTs_{roc1}_{roc2}_{roc3}_{roc4}")
        return result, kst_signal

    def MACD(self,
             data,
             fast=None,
             slow=None,
             signal=None,
             offset=None,
             dependencies=['close'],
             **kwargs):
        fast = int(fast) if fast and fast > 0 else 12
        slow = int(slow) if slow and slow > 0 else 26
        signal = int(signal) if signal and signal > 0 else 9
        result, histogram, signalma = macd(copy.deepcopy(data['close']),
                                           fast=fast,
                                           slow=slow,
                                           signal=signal,
                                           offset=offset,
                                           **kwargs)
        result = self._format(result, f"MACD_{fast}_{slow}_{signal}")
        histogram = self._format(histogram, f"MACDh_{fast}_{slow}_{signal}")
        signalma = self._format(signalma, f"MACDs_{fast}_{slow}_{signal}")
        return result, histogram, signalma

    def MOM(self,
            data,
            length=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 10
        result = mom(copy.deepcopy(data['close']),
                     length=length,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"MOM_{length}")

    def OVERNIGHT(self,
                  data,
                  length=None,
                  offset=None,
                  dependencies=['open', 'close'],
                  **kwargs):
        length = int(length) if length and length > 0 else 10
        result = overnight(copy.deepcopy(data['open']),
                           copy.deepcopy(data['close']),
                           length=length,
                           offset=offset,
                           **kwargs)
        return self._format(result, f"OverNight_{length}")

    def PGO(self,
            data,
            length=None,
            offset=None,
            dependencies=['high', 'low', 'close'],
            **kwargs):
        length = int(length) if length and length > 0 else 10
        result = pgo(copy.deepcopy(data['high']),
                     copy.deepcopy(data['low']),
                     copy.deepcopy(data['close']),
                     length=length,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"PGO_{length}")

    def PPO(self,
            data,
            fast=None,
            slow=None,
            signal=None,
            scalar=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        fast = int(fast) if fast and fast > 0 else 12
        slow = int(slow) if slow and slow > 0 else 26
        signal = int(signal) if signal and signal > 0 else 9
        result, histogram, signalma = ppo(copy.deepcopy(data['close']),
                                          fast=fast,
                                          slow=slow,
                                          signal=signal,
                                          scalar=scalar,
                                          offset=offset,
                                          **kwargs)
        result = self._format(result, f"PPO_{fast}_{slow}_{signal}")
        histogram = self._format(histogram, f"PPOh_{fast}_{slow}_{signal}")
        signalma = self._format(signalma, f"PPOs_{fast}_{slow}_{signal}")
        return result, histogram, signalma

    def PSL(self,
            data,
            length=None,
            scalar=None,
            drift=None,
            offset=None,
            dependencies=['close', 'open'],
            **kwargs):
        length = int(length) if length and length > 0 else 12
        result = psl(copy.deepcopy(data['close']),
                     copy.deepcopy(data['open']),
                     length=length,
                     scalar=scalar,
                     drift=drift,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"PSL_{length}")

    def PVO(self,
            data,
            fast=None,
            slow=None,
            signal=None,
            scalar=None,
            offset=None,
            dependencies=['volume'],
            **kwargs):
        fast = int(fast) if fast and fast > 0 else 12
        slow = int(slow) if slow and slow > 0 else 26
        signal = int(signal) if signal and signal > 0 else 9
        result, histogram, signalma = pvo(copy.deepcopy(data['volume']),
                                          fast=fast,
                                          slow=slow,
                                          signal=signal,
                                          scalar=scalar,
                                          offset=offset,
                                          **kwargs)
        result = self._format(result, f"PVO_{fast}_{slow}_{signal}")
        histogram = self._format(histogram, f"PVOh_{fast}_{slow}_{signal}")
        signalma = self._format(signalma, f"PVOs_{fast}_{slow}_{signal}")
        return result, histogram, signalma

    def ROC(self,
            data,
            length=None,
            scalar=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 10
        result = roc(copy.deepcopy(data['close']),
                     length=length,
                     scalar=scalar,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"ROC_{length}")

    def RSI(self,
            data,
            length=None,
            scalar=None,
            drift=None,
            offset=None,
            dependencies=['close'],
            **kwargs):
        length = int(length) if length and length > 0 else 14
        result = rsi(copy.deepcopy(data['close']),
                     length=length,
                     scalar=scalar,
                     drift=drift,
                     offset=offset,
                     **kwargs)
        return self._format(result, f"RSI_{length}")

    def RVGI(self,
             data,
             length=None,
             swma_length=None,
             offset=None,
             dependencies=['open', 'high', 'low', 'close'],
             **kwargs):
        length = int(length) if length and length > 0 else 14
        swma_length = int(
            swma_length) if swma_length and swma_length > 0 else 4
        result, signal = rvgi(copy.deepcopy(data['open']),
                              copy.deepcopy(data['high']),
                              copy.deepcopy(data['low']),
                              copy.deepcopy(data['close']),
                              length=length,
                              swma_length=swma_length,
                              offset=offset,
                              **kwargs)
        result = self._format(result, f"RVGI_{length}_{swma_length}")
        signal = self._format(signal, f"RVGI_{length}_{swma_length}")
        return result, signal

    def SLOPE(self,
              data,
              length=None,
              as_angle=None,
              to_degrees=None,
              vertical=None,
              offset=None,
              dependencies=['close'],
              **kwargs):
        length = int(length) if length and length > 0 else 1
        as_angle = True if isinstance(as_angle, bool) else False
        to_degrees = True if isinstance(to_degrees, bool) else False
        result = slope(copy.deepcopy(data['close']),
                       length=length,
                       as_angle=as_angle,
                       to_degrees=to_degrees,
                       vertical=vertical,
                       offset=offset,
                       **kwargs)
        return self._format(
            result, f"SLOPE_{length}"
            if not as_angle else f"ANGLE{'d' if to_degrees else 'r'}_{length}")

    def STOCH(self,
              data,
              k=None,
              d=None,
              smooth_k=None,
              offset=None,
              dependencies=['high', 'low', 'close'],
              **kwargs):
        k = k if k and k > 0 else 14
        d = d if d and d > 0 else 3
        smooth_k = smooth_k if smooth_k and smooth_k > 0 else 3
        stoch_k, stoch_d = stoch(copy.deepcopy(data['high']),
                                 copy.deepcopy(data['low']),
                                 copy.deepcopy(data['close']),
                                 k=k,
                                 d=d,
                                 smooth_k=smooth_k,
                                 offset=offset,
                                 **kwargs)
        stoch_k = self._format(stoch_k, f"STOCHk_{k}_{d}_{smooth_k}")
        stoch_d = self._format(stoch_d, f"STOCHd_{k}_{d}_{smooth_k}")
        return stoch_k, stoch_d

    def STOCHRSI(self,
                 data,
                 length=None,
                 rsi_length=None,
                 k=None,
                 d=None,
                 offset=None,
                 dependencies=['close'],
                 **kwargs):
        length = length if length and length > 0 else 14
        rsi_length = rsi_length if rsi_length and rsi_length > 0 else 14
        k = k if k and k > 0 else 3
        d = d if d and d > 0 else 3
        stochrsi_k, stochrsi_d = stochrsi(copy.deepcopy(data['close']),
                                          length=length,
                                          rsi_length=rsi_length,
                                          k=k,
                                          d=d,
                                          offset=offset,
                                          **kwargs)
        stochrsi_k = self._format(stochrsi_k,
                                  f"STOCHRSIk_{length}_{rsi_length}_{k}")
        stochrsi_d = self._format(stochrsi_d,
                                  f"STOCHRSId_{length}_{rsi_length}_{d}")
        return stochrsi_k, stochrsi_d

    def TRIX(self,
             data,
             length=None,
             signal=None,
             scalar=None,
             drift=None,
             offset=None,
             dependencies=['close'],
             **kwargs):
        length = int(length) if length and length > 0 else 30
        signal = int(signal) if signal and signal > 0 else 9
        result, trix_signal = trix(copy.deepcopy(data['close']),
                                   length=length,
                                   signal=signal,
                                   scalar=scalar,
                                   drift=drift,
                                   offset=offset,
                                   **kwargs)
        result = self._format(result, f"TRIX_{length}_{signal}")
        trix_signal = self._format(trix_signal, f"TRIXs_{length}_{signal}")
        return result, trix_signal

    def TSI(self,
            data,
            fast=None,
            slow=None,
            signal=None,
            scalar=None,
            drift=None,
            offset=None,
            mamode=None,
            dependencies=['close'],
            **kwargs):
        fast = int(fast) if fast and fast > 0 else 13
        slow = int(slow) if slow and slow > 0 else 25
        signal = int(signal) if signal and signal > 0 else 13
        result, tri_signal = trix(copy.deepcopy(data['close']),
                                  fast=fast,
                                  slow=slow,
                                  signal=signal,
                                  scalar=scalar,
                                  drift=drift,
                                  offset=offset,
                                  **kwargs)
        result = self._format(result, f"TSI_{fast}_{slow}_{signal}")
        tri_signal = self._format(tri_signal, f"TSIs_{fast}_{slow}_{signal}")
        return result, tri_signal

    def UPINTRADAY(self,
                   data,
                   length=None,
                   offset=None,
                   dependencies=['open', 'high'],
                   **kwargs):
        length = int(length) if length and length > 0 else 5
        result = upintraday(copy.deepcopy(data['open']),
                            copy.deepcopy(data['high']),
                            length=length,
                            offset=offset,
                            **kwargs)
        return self._format(result, f"UPIntraday_{length}")

    def DNINTRADAY(self,
                   data,
                   length=None,
                   offset=None,
                   dependencies=['open', 'low'],
                   **kwargs):
        length = int(length) if length and length > 0 else 5
        result = dnintraday(copy.deepcopy(data['open']),
                            copy.deepcopy(data['low']),
                            length=length,
                            offset=offset,
                            **kwargs)
        return self._format(result, f"DNIntraday_{length}")

    def UPCHVOLATILITY(self,
                       data,
                       length=None,
                       offset=None,
                       dependencies=['close', 'high'],
                       **kwargs):
        length = int(length) if length and length > 0 else 5
        result = upchvolatility(copy.deepcopy(data['close']),
                                copy.deepcopy(data['high']),
                                length=length,
                                offset=offset,
                                **kwargs)
        return self._format(result, f"UPCHVolatility_{length}")

    def UPHHVOLATILITY(self,
                       data,
                       length=None,
                       offset=None,
                       dependencies=['high'],
                       **kwargs):
        length = int(length) if length and length > 0 else 5
        result = uphhvolatility(copy.deepcopy(data['high']),
                                length=length,
                                offset=offset,
                                **kwargs)
        return self._format(result, f"UPHHVolatility_{length}")

    def WILLR(self,
              data,
              length=None,
              offset=None,
              dependencies=['close', 'low', 'high'],
              **kwargs):
        length = int(length) if length and length > 0 else 14
        result = willr(copy.deepcopy(data['high']),
                       copy.deepcopy(data['low']),
                       copy.deepcopy(data['close']),
                       length=length,
                       offset=offset,
                       **kwargs)
        return self._format(result, f"WILLR_{length}")
