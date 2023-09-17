import sys
sys.path.append("src/")

import pytest

from ulflib import ulflib

class TestTT_P_ARG_MOD:
  def test_1(self):
    ulf = ['right.mod-a', ['before.ps', ['i.pro', [['past', 'move.v'], 'it.pro']]]]
    assert ['sent-mod'] == ulflib.phrasal_ulf_type(ulf)

  def test_2(self):
    ulf = ['right.mod-n', ['before.ps', ['i.pro', [['past', 'move.v'], 'it.pro']]]]
    assert ['unknown'] == ulflib.phrasal_ulf_type(ulf)