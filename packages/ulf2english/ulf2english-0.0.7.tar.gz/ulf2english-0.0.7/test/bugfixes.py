import sys
sys.path.append("src/")

import pytest

from ulf2english import ulf2english

ulf = '((SUB HOW.PQ ((PRES DO.AUX-S) YOU.PRO ((SAY.V (" 2 ")) (ADV-A (IN.P | Latin|)) *H)) ?)'
# ulf = '2'
print(ulf2english.convert(ulf, verbose=True))

class TestNoTypeErrorOnNumber:
  """Ensure that there isn't a type error on numbers in ULFs."""

  def test_1(self):
    ulf = '((SUB HOW.PQ ((PRES DO.AUX-S) YOU.PRO ((SAY.V (" 2 ")) (ADV-A (IN.P | Latin|)) *H)) ?)'
    str = 'How do you say 2 in Latin?'
    assert ulf2english.convert(ulf) == str