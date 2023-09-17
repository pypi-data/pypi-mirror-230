import sys
sys.path.append("src/")

import pytest

from ulf2english import ulf2english

ulf = "(({YOU}.PRO ((PRES NAME.V) ((|Li'l Abner| 'S) (FAVORITE.A (|Indian.A| DRINK.N))))) !)"
print(ulf2english.convert(ulf, verbose=True))

class TestNoTypeErrorOnNumber:
  """Ensure that there isn't a type error on numbers in ULFs."""

  def test_1(self):
    ulf = '((SUB HOW.PQ ((PRES DO.AUX-S) YOU.PRO ((SAY.V (" 2 ")) (ADV-A (IN.P | Latin|)) *H))) ?)'
    str = 'How do you say "2" in Latin?'
    assert ulf2english.convert(ulf) == str


class TestParticiplesFromDoc:
  """Proper handling of participles (examples from documentation on predicate modification)."""

  def test_1(self):
    ulf = '(i.pro ((past greet.v) (the.d ((mod-n (frequently.adv-f return.v)) (member-of.n *ref)))))'
    str = 'i greeted the frequently returning member .'
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_2(self):
    ulf = '(we.pro ((pres (pasv require.v)) (to (submit.v (a.d ((mod-n (carefully.adv-a (pasv write.v))) notice.n))))))'
    str = "we are required to submit a carefully written notice ."
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_3(self):
    ulf = '(|Kenneth| (nervously.adv-a ((past watch.v) (the.d woman.n) (adv-a ((pasv alarm.v) (by.p-arg (her.d gun.n)))))))'
    str = "kenneth nervously watched the woman alarmed by her gun ."
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_4(self):
    ulf = '(i.pro ((past go.v) back.adv-a (to.p-arg (k sleep.n)) (adv-a (perf (hear.v this.pro before.adv-e)))))'
    str = "i went back to sleep having heard this before ."
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_5(self):
    ulf = '(sub (adv-a (lift.v (k (plur weight.n)) (adv-e (for.p (two.d (plur hour.n)))))) (|Ron| ((past develop.v) (k (sore.a (plur muscle.n))) *h)))'
    str = "lifting weights for two hours ron developed sore muscles ."
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_6(self):
    ulf = '((any.d (n+preds student.n (score.v (a.d (good.a grade.n)) (on.p-arg (the.d exam.n))))) ((pres will.aux-s) (receive.v (an.d award.n))))'
    str = "any student scoring a good grade on the exam will receive an award ."
    assert ulf2english.convert(ulf, standardize=True) == str


class TestVocativesFromDoc:
  """Find issues with vocatives (examples from documentation on vocatives)."""

  def test_1(self):
    ulf = '((voc |Mary|) (I.pro ((pres see.v) you.pro)))'
    str = "mary i see you ."
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_2(self):
    ulf = '((I.pro ((pres do.aux-s) not.adv-s (think.v (tht (I.pro ((pres understand.v) {ref}.pro)))))) (voc |Susan|))'
    str = "i do not think i understand susan ."
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_3(self):
    ulf = '((My.d (n+preds (ill.a (plur feeling.n)) (towards.p-arg you.pro))) (voc |Lex|) ((pres be.v) endless.a))'
    str = "my ill feelings towards you lex are endless ."
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_4(self):
    ulf = '(((voc (np+preds you.pro (in.p (the.d (yellow.a shirt.n))))) ({you}.pro ((pres call.v) |911|))) !)'
    str = "you in the yellow shirt call 911 !"
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_5(self):
    ulf = '(((voc |John|) (voc (np+preds you.pro rascal.n)) (sub (at.p (what.d place.n)) ((pres perf) you.pro (be.v *h)))) ?)'
    str = "john you rascal where have you been ?"
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_6(self):
    ulf = '(((voc (np+preds you.pro rascal.n)) (sub (at.p (what.d place.n)) ((pres perf) you.pro (be.v *h))) (voc |John|)) ?)'
    str = "you rascal where have you been john ?"
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_7(self):
    ulf = '(((Why.adv-s ((pres be.v) ye.pro fearful.a)) (voc-O (np+preds ye.pro (of.p (little.a faith.n))))) ?)'
    str = "why are ye fearful o ye of little faith ?"
    assert ulf2english.convert(ulf, standardize=True) == str


class TestNamedPredicates:
  """Named predicate error detected during ulf inference experiments."""

  def test_1(self):
    ulf = "(({YOU}.PRO ((PRES NAME.V) ((|Li'l Abner| 'S) (FAVORITE.A (|Indian.A| DRINK.N))))) !)"
    str = "name li'l abner 's favorite indian drink !"
    assert ulf2english.convert(ulf, standardize=True) == str

  def test_2(self):
    ulf = '({THE}.D (N+PREDS POLLSTER.N (= |Robert M. Teeter|)))'
    str = "pollster robert m . teeter ."
    assert ulf2english.convert(ulf, standardize=True) == str