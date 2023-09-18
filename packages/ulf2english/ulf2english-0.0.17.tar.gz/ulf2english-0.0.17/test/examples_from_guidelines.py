"""Unit tests based on the ULF Annotation Guidelines"""

import pytest

from ulf2english import ulf2english

class TestCounterfactuals:
  """Examples from the section Counterfactuals & Conditionals."""

  def test_1(self):
    ulf = '(i.pro ((pres wish.v) (tht (i.pro ((cf be.v) rich.a)))))'
    str = "I wish I was rich."
    assert ulf2english.convert(ulf) == str

  def test_2(self):
    ulf = '(I.pro ((pres wish.v) (tht (I.pro ((cf believe.v) you.pro)))))'
    str = "I wish I believed you."
    assert ulf2english.convert(ulf) == str

  def test_3(self):
    ulf = '(I.pro ((pres wish.v) (tht (I.pro ((cf were.v) rich.a)))))'
    str = "I wish I were rich."
    assert ulf2english.convert(ulf) == str

  def test_4(self):
    ulf = '((if.ps (I.pro ((cf be.v) rich.a))) (I.pro ((cf will.aux-s) (own.v (a.d boat.n)))))'
    str = "If I was rich I would own a boat."
    assert ulf2english.convert(ulf) == str

  def test_5(self):
    ulf = '(((cf be-destined.aux-v) he.pro leave.v) ((the.d project.n) ((cf will.aux-s) collapse.v)))'
    str = "Were he to leave the project would collapse."
    assert ulf2english.convert(ulf) == str

  def test_6(self):
    ulf = '(((cf perf) I.pro (forsee.v this.pro)) (I.pro ((cf will.aux-s) never.adv-e (perf participate.v))))'
    str = "Had I forseen this I would never have participated."
    assert ulf2english.convert(ulf) == str

  def test_7(self):
    ulf = '((If.ps (I.pro ((cf perf) (be.v rich.a)))) (I.pro ((pres would.aux-s) (own.v (a.d boat.n)))))'
    str = "If I had been rich I would own a boat."
    assert ulf2english.convert(ulf) == str

  def test_8(self):
    ulf = '((If.ps (I.pro ((cf perf) (be.v rich.a)))) (then.adv-s (I.pro ((cf will.aux-s) (perf (own.v (a.d boat.n)))))))'
    str = "If I had been rich then I would have owned a boat."
    assert ulf2english.convert(ulf) == str


class TestYesNo:
  """Examples from the Yes-No subsection."""

  def test_1(self):
    ulf = 'yes.yn'
    str = "Yes."
    assert ulf2english.convert(ulf) == str 

  def test_2(self):
    ulf = '(Uh-huh.yn (that.pro ((pres be.v) (the.d plan.n))))'
    str = "Uh huh that is the plan."
    assert ulf2english.convert(ulf) == str 

  def test_3(self):
    ulf = '(Definitely.adv-s yes.yn)'
    str = "Definitely yes."
    assert ulf2english.convert(ulf) == str 

  def test_4(self):
    ulf = '(Yes.yn (pu definitely.adv-s))'
    str = "Yes definitely."
    assert ulf2english.convert(ulf) == str 

  def test_5(self):
    ulf = '(Surprisingly.adv-s no.yn)'
    str = "Surprisingly no."
    assert ulf2english.convert(ulf) == str 


class TestEmphaticWh:
  """Examples from the Exclamatory/Emphatic Wh-words section."""

  def test_1(self):
    ulf = '((sub (= (What-em.d (= (a.d (beautiful.a car.n))))) (that.pro ((pres be.v) *h))) !)'
    str = "What a beautiful car that is!"
    assert ulf2english.convert(ulf) == str

  def test_2(self):
    ulf = '(sub (= (What-em.d (beautiful.a (plur car.n)))) (these.pro ((pres be.v) *h)))'
    str = "What beautiful cars these are."
    assert ulf2english.convert(ulf) == str

  def test_3(self):
    ulf = '(sub (= (What-em.d (= (a.d (strong.a person.n))))) (he.pro ((pres be.v) *h)))'
    str = "What a strong person he is."
    assert ulf2english.convert(ulf) == str

  def test_4(self):
    ulf = '(sub (= (What-em.d (smart.a (plur kid.n)))) (you.pro ((pres be.v) *h)))'
    str = "What smart kids you are."
    assert ulf2english.convert(ulf) == str

  def test_5(self):
    ulf = '((sub (What-em.d (= (a.d mess.n))) (he.pro ((past make.v) *h))) !)'
    str = "What a mess he made!"
    assert ulf2english.convert(ulf) == str

  def test_6(self):
    ulf = '((sub (= (What-em.d (= (a.d (beautiful.a car.n))))) ({that}.pro ((pres {be}.v) *h))) !)'
    str = "What a beautiful car!"
    assert ulf2english.convert(ulf) == str

  def test_7(self):
    ulf = '((sub (= (What-em.d (= (an.d idea.n)))) ({that}.pro ((pres {be}.v) *h))) !)'
    str = "What an idea!"
    assert ulf2english.convert(ulf) == str

  def test_8(self):
    ulf = '((sub (= (What-em.d (= (a.d (charming.a actress.n))))) ({she}.pro ((pres {be}.v) *h))) !)'
    str = "What a charming actress!"
    assert ulf2english.convert(ulf) == str

  def test_9(self):
    ulf = '((sub (= (What-em.d (= (a.d (n+preds bunch.n (of.p (k (beautiful.a (plur picture.n))))))))) ({those}.pro ((pres {be}.v) *h))) !)'
    str = "What a bunch of beautiful pictures!"
    assert ulf2english.convert(ulf) == str

  def test_10(self):
    ulf = '((sub (What-em.d (= (a.d (beautiful.a car.n)))) (you.pro ((past buy.v) *h))) !)'
    str = "What a beautiful car you bought!"
    assert ulf2english.convert(ulf) == str

  def test_11(self):
    ulf = '((sub (How-em.mod-a studious.a) (he.pro ((pres be.v) *h))) !)'
    str = "How studious he is!"
    assert ulf2english.convert(ulf) == str

  def test_12(self):
    ulf = '((sub (How-em.mod-a curious.a) (they.pro ((pres be.v) *h))) !)'
    str = "How curious they are!"
    assert ulf2english.convert(ulf) == str

  def test_13(self):
    ulf = '((sub (How-em.mod-a strange.a) ({that}.pro ((pres {be}.v) *h))) !)'
    str = "How strange!"
    assert ulf2english.convert(ulf) == str

  def test_14(self):
    ulf = '((sub How-em.adv-a (I.pro (((past use.v) (to (enjoy.v this.pro))) *h))) !)'
    str = "How I used to enjoy this!"
    assert ulf2english.convert(ulf) == str

  def test_15(self):
    ulf = '(You.pro ((pres should.aux-v) (see.v (ans-to (sub (what.d (beautiful.a car.n)) (he.pro ((past buy.v) *h)))))))'
    str = "You should see what beautiful car he bought."
    assert ulf2english.convert(ulf) == str

  def test_16(self):
    ulf = '(You.pro ((pres should.aux-v) (see.v (ans-to (sub (What-em.d (= (a.d (beautiful.a car.n)))) (he.pro ((past buy.v) *h)))))))'
    str = "You should see what a beautiful car he bought."
    assert ulf2english.convert(ulf) == str

  def test_17(self):
    ulf = '(You.pro ((pres should.aux-v) (see.v (ans-to (sub (what.d (n+preds (model-of.n (k car.n)))) (he.pro ((past buy.v) *h)))))))'
    str = "You should see what model of car he bought."
    assert ulf2english.convert(ulf) == str

  def test_18(self):
    ulf = '(I.pro ((pres know.v) (ans-to (sub (in.p (sub (how.mod-a deep.a) (a.d (*h (financial.a hole.n))))) (he.pro now.adv-e ((pres be.v) *h) (adv-s (because_of.p (his.d (risky.a (plur investment.n))))))))))'
    str = "I know in how deep a financial hole he now is because of his risky investments."
    assert ulf2english.convert(ulf) == str

  def test_19(self):
    ulf = '((sub (In.p (sub (how-em.mod-a deep.a) (a.d (*h (financial.a hole.n))))) (he.pro now.adv-e ((pres be.v) *h) (adv-s (because_of.p (his.d (risky.a (plur investment.n))))))) !)'
    str = "In how deep a financial hole he now is because of his risky investments!"
    assert ulf2english.convert(ulf) == str


class TestImperatives:
  """Imperative examples from the guidelines."""

  def test_1(self):
    ulf = '(({you}.pro ((pres go.v) (k home.n))) !)'
    str = "Go home!"
    assert ulf2english.convert(ulf) == str

  def test_2(self):
    ulf = '(((voc |John|) ({you}.pro ((pres go.v) (k home.n)))) !)'
    str = "John go home!"
    assert ulf2english.convert(ulf) == str


class TestDomainSpecific:
  """Examples from the domain specific section in the ULF guidelines."""

  def test_1(self):
    str, ulf = ("555 555-5555", '(ds phone-number "555 555-5555")')
    assert ulf2english.convert(ulf) == str

  def test_2(self):
    str, ulf = ("(555)555-5555", '(ds phone-number "(555)555-5555")')
    assert ulf2english.convert(ulf) == str

  def test_3(self):
    str, ulf = ("5555555", '(ds phone-number "5555555")')
    assert ulf2english.convert(ulf) == str

  def test_4(self):
    str, ulf = ("5:30pm", '(ds date-time "5:30pm")')
    assert ulf2english.convert(ulf) == str

  def test_5(self):
    str, ulf = ("June 18th 2017", '(ds date-time "June 18th 2017")')
    assert ulf2english.convert(ulf) == str

  def test_6(self):
    str, ulf = ("quarter after 3", '(ds date-time "quarter after 3")')
    assert ulf2english.convert(ulf) == str

  def test_7(self):
    str, ulf = ("$50.12", '(ds currency "$50.12")')
    assert ulf2english.convert(ulf) == str

  def test_8(self):
    str, ulf = ("Fifty dollars and 12 cents", '(ds currency "Fifty dollars and 12 cents")')
    assert ulf2english.convert(ulf) == str

  def test_9(self):
    str, ulf = ("e30", '(ds currency "e30")')
    assert ulf2english.convert(ulf) == str

  def test_10(self):
    str, ulf = ("880 Linden Ave", '(ds address "880 Linden Ave")')
    assert ulf2english.convert(ulf) == str

  def test_11(self):
    str, ulf = ("Rochester NY 14620", '(ds address "Rochester NY 14620")')
    assert ulf2english.convert(ulf) == str

  def test_12(self):
    str, ulf = ("bonjour monsieur", '(ds fws "bonjour monsieur")')
    assert ulf2english.convert(ulf) == str

  def test_13(self):
    str, ulf = ("君の名は", '(ds fws "君の名は")')
    assert ulf2english.convert(ulf) == str

  def test_14(self):
    str, ulf = ("dm-drogerie markt", '(ds fws "dm-drogerie markt")')
    assert ulf2english.convert(ulf) == str

  def test_15(self):
    str, ulf = ("5 degrees Celsius", '(ds temp "5 degrees Celsius")')
    assert ulf2english.convert(ulf) == str

  def test_16(self):
    str, ulf = ("5'11¨", '(ds length "5\'11¨")')
    assert ulf2english.convert(ulf) == str

  def test_17(self):
    str, ulf = ("seven meters", '(ds length "seven meters")')
    assert ulf2english.convert(ulf) == str

  def test_18(self):
    str, ulf = ("80km", '(ds length "80km")')
    assert ulf2english.convert(ulf) == str

  def test_19(self):
    str, ulf = ("17kph", '(ds speed "17kph")')
    assert ulf2english.convert(ulf) == str

  def test_20(self):
    str, ulf = ("50mile per hour", '(ds speed "50mile per hour")')
    assert ulf2english.convert(ulf) == str

  def test_21(self):
    str, ulf = ("8.2 m/s", '(ds speed "8.2 m/s")')
    assert ulf2english.convert(ulf) == str

  def test_22(self):
    str, ulf = ("whhhatre yooooouuuuse doeeeein", '(ds unk "whhhatre yooooouuuuse doeeeein")')
    assert ulf2english.convert(ulf) == str
