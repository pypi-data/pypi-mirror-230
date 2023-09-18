"""Tests for comma insertions."""

import pytest

from ulf2english import ulf2english

class TestSentCoord:
  """Comma insertions for sentential coordinators"""

  def test_1(self):
    ulf = '((i.pro (past leave.v)) and.cc ((the.d tower.n) (past fall.v))))'
    str = "I left, and the tower fell."
    assert ulf2english.convert(ulf, add_commas=True) == str

  def test_2(self):
    ulf = '((i.pro (past leave.v)) (he.pro ((past turn.v) around.adv-a)) and.cc ((the.d tower.n) (past fall.v))))'
    str = "I left, he turned around, and the tower fell."
    assert ulf2english.convert(ulf, add_commas=True) == str


class TestNounCoord:
  """Comma insertions for nominal coordinators"""

  def test_1(self):
    ulf = '(i.pro ((past buy.v) ((the.d (plur book.n)) (k (plur apple.n)) and.cc (some.d sugar.n)))))'
    str = "I bought the books, apples, and some sugar."
    assert ulf2english.convert(ulf, add_commas=True) == str

  def test_2(self):
    ulf = '(they.pro ((pres prog) (look.v (for.p-arg (you.pro and.cc me.pro))))))'
    str = "They are looking for you and me."
    assert ulf2english.convert(ulf, add_commas=True) == str


class TestVerbCoord:
  """Comma insertions for verbal coordinators"""

  def test_1(self):
    ulf = '(i.pro (((past turn.v) around.adv-a) and.cc (past leave.v))))'
    str = "I turned around and left."
    assert ulf2english.convert(ulf, add_commas=True) == str

  def test_2(self):
    ulf = '(i.pro ((past wave.v) ((past turn.v) around.adv-a) and.cc (past leave.v))))'
    str = "I waved, turned around, and left."
    assert ulf2english.convert(ulf, add_commas=True) == str


class TestScopedPs:
  """Comma insertions for *.ps where arguments are individually scoped"""

  def test_1(self):
    ulf = '((k (plur mango.n)) ((pres be.v) delicious.a (when.ps (they.pro ((pres be.v) ripe.a))))'
    str = "Mangoes are delicious, when they are ripe."
    assert ulf2english.convert(ulf, add_commas=True) == str

  def test_2(self):
    ulf = '((when.ps (they.pro ((pres be.v) ripe.a))) ((k (plur mango.n)) ((pres be.v) delicious.a)))'
    str = "When they are ripe, mangoes are delicious."
    assert ulf2english.convert(ulf, add_commas=True) == str

  def test_3(self):
    ulf = '(((k (plur Leg.n)) (pres ache.v)) (when.ps (they.pro (pres (pasv strain.v))))))'
    str = "Legs ache, when they are strained."
    assert ulf2english.convert(ulf, add_commas=True) == str


class TestFlatPs:
  """Comma insertions for *.ps where arguments are flatly scoped"""

  def test_1(self):
    ulf = '(when.ps (they.pro ((pres be.v) ripe.a)) ((k (plur mango.n)) ((pres be.v) delicious.a)))'
    str = "When they are ripe, mangoes are delicious."
    assert ulf2english.convert(ulf, add_commas=True) == str

  def test_2(self):
    ulf = '(when.ps (they.pro (pres (pasv strain.v))) ((k (plur leg.n)) (pres ache.v)))'
    str = "When they are strained, legs ache."
    assert ulf2english.convert(ulf, add_commas=True) == str