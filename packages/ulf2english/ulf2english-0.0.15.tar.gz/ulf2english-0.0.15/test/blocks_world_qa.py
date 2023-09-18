"""Unit tests for ulf2english on the blocks world QA question set."""

import pytest

from ulf2english import ulf2english

def test_1():
  ulf = "(((PRES BE.V) (THE.D (| Nvidia| BLOCK.N)) (TO.P (THE.D (LEFT-OF.N (THE.D | Texaco| BLOCK.N))))) ?)"
  str = "Is the Nvidia block to the left of the Texaco block?"
  assert ulf2english.convert(ulf) == str

def test_2():
  ulf = "(((PRES BE.V) (THE.D (| McDonalds| BLOCK.N)) (ON.P ({THE}.D (TOP-OF.N (THE.D (| SRI| BLOCK.N)))))) ?)"
  str = "Is the McDonalds block on top of the SRI block?"
  assert ulf2english.convert(ulf) == str

def test_3():
  ulf = "(((PRES BE.V) (THE.D (| Starbucks| BLOCK.N)) (NEAR.P (THE.D (| Toyota| BLOCK.N)))) ?)"
  str = "Is the Starbucks block near the Toyota block?"
  assert ulf2english.convert(ulf) == str

def test_4():
  ulf = "(((PRES BE.V) (THE.D (| Toyota| BLOCK.N)) (BETWEEN.P ((THE.D (| Nvidia| BLOCK.N)) AND.CC (THE.D (| Target| BLOCK.N))))) ?)"
  str = "Is the Toyota block between the Nvidia block and the Target block?"
  assert ulf2english.convert(ulf) == str

def test_5():
  ulf = "(((PRES BE.V) (THE.D (| SRI| BLOCK.N)) (FULLY.MOD-A (ON.P ({THE}.D (TOP-OF.N (ANY.D (RED.A BLOCK.N))))))) ?)"
  str = "Is the SRI block fully on top of any red block?"
  assert ulf2english.convert(ulf) == str

def test_6():
  ulf = "(((PRES DO.AUX-S) (THE.D (| Toyota| BLOCK.N)) (FACE.V (THE.D (| Nvidia| BLOCK.N)))) ?)"
  str = "Does the Toyota block face the Nvidia block?"
  assert ulf2english.convert(ulf) == str

def test_7():
  ulf = "(((PRES DO.AUX-S) (THE.D (MOST-N TALL.A STACK.N)) (HAVE.V (A.D (RED.A BLOCK.N)) (ON.P ({THE}.D (TOP-OF.N *REF))))) ?)"
  str = "Does the tallest stack have a red block on top?"
  assert ulf2english.convert(ulf) == str

def test_8():
  ulf = "(((PRES BE.V) (THE.D (| Toyota| BLOCK.N)) (= (A.D (PART-OF.N (SOME.D STACK.N))))) ?)"
  str = "Is the Toyota block a part of some stack?"
  assert ulf2english.convert(ulf) == str

def test_9():
  ulf = "(((PRES BE.V) (THE.D (| Target| BLOCK.N)) (= (A.D (PART-OF.N (SOME.D ROW.N))))) ?)"
  str = "Is the Target block a part of some row?"
  assert ulf2english.convert(ulf) == str

def test_10():
  ulf = "(((PRES DO.AUX-S) (ANY.D ROW.N) (CONTAIN.V (A.D (RED.A BLOCK.N)))) ?)"
  str = "Does any row contain a red block?"
  assert ulf2english.convert(ulf) == str

def test_11():
  ulf = "(((PRES PROG) (ANY.D (TWO.A (GREEN.A (PLUR BLOCK.N)))) TOUCH.V) ?)"
  str = "Are any two green blocks touching?"
  assert ulf2english.convert(ulf) == str

def test_12():
  ulf = "(((PRES BE.V) (ANY.D (TWO.A (PLUR STACK.N))) (NEAR.P (EACH.D (OTHER.N {REF}.N)))) ?)"
  str = "Are any two stacks near each other?"
  assert ulf2english.convert(ulf) == str

def test_13():
  ulf = "(((PRES DO.AUX-S) (THE.D (| SRI| BLOCK.N)) (HAVE.V ANYTHING.PRO (ON.P IT.PRO))) ?)"
  str = "Does the SRI block have anything on it?"
  assert ulf2english.convert(ulf) == str

def test_14():
  ulf = "(((PRES BE.V) (THE.D ((| Nvidia| AND.CC | SRI|) (PLUR BLOCK.N))) (IN.P (THE.D (SAME.A STACK.N)))) ?)"
  str = "Are the Nvidia and SRI blocks in the same stack?"
  assert ulf2english.convert(ulf) == str

def test_15():
  ulf = "(((PRES BE.V) (THE.D (| Toyota| BLOCK.N)) (BELOW.P (THE.D (| Texaco| BLOCK.N)))) ?)"
  str = "Is the Toyota block below the Texaco block?"
  assert ulf2english.convert(ulf) == str

def test_16():
  ulf = "(((PRES BE.V) (THE.D (| Starbucks| BLOCK.N)) (ON.P ({THE}.D (TOP-OF.N (ANY.D ROW.N))))) ?)"
  str = "Is the Starbucks block on top of any row?"
  assert ulf2english.convert(ulf) == str

def test_17():
  ulf = "(((PRES BE.V) ((THE.D (| Nvidia| (PLUR {BLOCK}.N))) AND.CC (THE.D (| McDonalds| (PLUR BLOCK.N)))) SIDE_BY_SIDE.A) ?)"
  str = "Are the Nvidia and the McDonalds blocks side by side?"
  assert ulf2english.convert(ulf) == str

def test_18():
  ulf = "(((PRES BE.V) (ALL.D ({OF}.P (THE.D (RED.A (PLUR BLOCK.N))))) (NEAR.P (THE.D (| Nvidia| BLOCK.N)))) ?)"
  str = "Are all the red blocks near the Nvidia block?"
  assert ulf2english.convert(ulf) == str

def test_19():
  ulf = "(((PRES BE.V) (EVERY.D (BLUE.A BLOCK.N)) (BEHIND.P (SOME.D (OTHER.A BLOCK.N)))) ?)"
  str = "Is every blue block behind some other block?"
  assert ulf2english.convert(ulf) == str

def test_20():
  ulf = "(((PRES BE.V) (THE.D (| Texaco| BLOCK.N)) (BETWEEN.P (ANY.D (TWO.A (PLUR BLOCK.N))))) ?)"
  str = "Is the Texaco block between any two blocks?"
  assert ulf2english.convert(ulf) == str

def test_21():
  ulf = "(((PRES BE.V) (THE.D (| Target| BLOCK.N)) (SLIGHTLY.MOD-A (TO.P (THE.D (LEFT-OF.N (SOME.D (RED.A BLOCK.N))))))) ?)"
  str = "Is the Target block slightly to the left of some red block?"
  assert ulf2english.convert(ulf) == str

def test_22():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (BETWEEN.P ((THE.D (| McDonalds| (PLUR {BLOCK}.N))) AND.CC (THE.D (| SRI| (PLUR BLOCK.N)))))))) ?)"
  str = "Is there a block between the McDonalds and the SRI blocks?"
  assert ulf2english.convert(ulf) == str

def test_23():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (NEAR.P (THE.D (| Target| BLOCK.N)))))) ?)"
  str = "Is there a block near the Target block?"
  assert ulf2english.convert(ulf) == str

def test_24():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS (RED.A BLOCK.N) (NEAR.P (A.D (BLUE.A BLOCK.N)))))) ?)"
  str = "Is there a red block near a blue block?"
  assert ulf2english.convert(ulf) == str

def test_25():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (TOUCH.V (THE.D (| Nvidia| BLOCK.N)))))) ?)"
  str = "Is there a block touching the Nvidia block?"
  assert ulf2english.convert(ulf) == str

def test_26():
  ulf = "(((PRES BE.V) THERE.PRO (ANY.D (N+PREDS THING.N (AT.P (THE.D (FRONT.A (LEFT.A (CORNER-OF.N (THE.D TABLE.N))))))))) ?)"
  str = "Is there anything at the front left corner of the table?"
  assert ulf2english.convert(ulf) == str

def test_27():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS ROW.N (CONSIST.V (OF.P-ARG (THREE.D (PLUR BLOCK.N))))))) ?)"
  str = "Is there a row consisting of three blocks?"
  assert ulf2english.convert(ulf) == str

def test_28():
  ulf = "(((WHICH.D BLOCK.N) ((PRES BE.V) (ON.P (TWO.D (OTHER.A (PLUR BLOCK.N)))))) ?)"
  str = "Which block is on two other blocks?"
  assert ulf2english.convert(ulf) == str

def test_29():
  ulf = "(((WHICH.D BLOCK.N) ((PRES BE.V) (IN.P (THE.D (CENTER-OF.N (THE.D TABLE.N)))))) ?)"
  str = "Which block is in the center of the table?"
  assert ulf2english.convert(ulf) == str

def test_30():
  ulf = "(((WHAT.D (PLUR BLOCK.N)) ((PRES BE.V) (IN.P (THE.D (MOST-N LONG.A ROW.N))))) ?)"
  str = "What blocks are in the longest row?"
  assert ulf2english.convert(ulf) == str

def test_31():
  ulf = "(((WHAT.D BLOCK.N) ((PRES BE.V) ((MOD-A HALFWAY.A) (ON.P ({THE}.D (TOP-OF.N (ANY.D (OTHER.A BLOCK.N)))))))) ?)"
  str = "What block is halfway on top of any other block?"
  assert ulf2english.convert(ulf) == str

def test_32():
  ulf = "(((WHICH.D BLOCK.N) ((PRES BE.V) (SIDE_BY_SIDE.A (WITH.P-ARG (THE.D (| Texaco| BLOCK.N)))))) ?)"
  str = "Which block is side by side with the Texaco block?"
  assert ulf2english.convert(ulf) == str

def test_33():
  ulf = "((WHAT.PRO ((PRES BE.V) (THE.D (REP ((MOST (FAR.A *P)) BLOCK.N) (MOD-A (FROM.P (THE.D (CENTER-OF.N (THE.D TABLE.N))))))))) ?)"
  str = "What is the farthest block from the center of the table?"
  assert ulf2english.convert(ulf) == str

def test_34():
  ulf = "((SUB (WHICH.D BLOCK.N) ((THE.D (| Nvidia| BLOCK.N)) ((PRES BE.V) (ON.P ({THE}.D (TOP-OF.N *H)))))) ?)"
  str = "Which block the Nvidia block is on top of?"
  assert ulf2english.convert(ulf) == str

def test_35():
  ulf = "(((WHICH.D BLOCK.N) ((PRES BE.V) ((VERY.MOD-A CLOSE.A) (MOD-A (TO.P (THE.D (FRONT.N (EDGE-OF.N (THE.D TABLE.N))))))))) ?)"
  str = "Which block is very close to the front edge of the table?"
  assert ulf2english.convert(ulf) == str

def test_36():
  ulf = "((WHAT.PRO ((PRES BE.V) (IN.P (THE.D (MIDDLE-OF.N (THE.D TABLE.N)))))) ?)"
  str = "What is in the middle of the table?"
  assert ulf2english.convert(ulf) == str

def test_37():
  ulf = "(((WHICH.D (RED.A BLOCK.N)) ((PRES BE.V) (THE.D (N+PREDS ({RED}.A {BLOCK}.N) (MOST (CLOSE.A (MOD-A (TO.P (THE.D (| Toyota| BLOCK.N)))))))))) ?)"
  str = "Which red block is the closest to the Toyota block?"
  assert ulf2english.convert(ulf) == str

def test_38():
  ulf = "(((WHICH.D (RED.A (PLUR BLOCK.N))) ((PRES BE.V) DIRECTLY.ADV-A (ON.P (THE.D TABLE.N)))) ?)"
  str = "Which red blocks are directly on the table?"
  assert ulf2english.convert(ulf) == str

def test_39():
  ulf = "((SUB (WHICH.D (BLUE.A BLOCK.N)) ((THE.D (| Nvidia| BLOCK.N)) ((PRES BE.V) NOT (NEAR.A (MOD-A (TO.P *H)))))) ?)"
  str = "Which blue block the Nvidia block is not near to?"
  assert ulf2english.convert(ulf) == str

def test_40():
  ulf = "((SUB WHERE.A ((PRES BE.V) (THE.D (| Toyota| BLOCK.N)) *H)) ?)"
  str = "Where is the Toyota block?"
  assert ulf2english.convert(ulf) == str

def test_41():
  ulf = "((SUB WHERE.A ((PRES BE.V) (SOME.D (BLUE.A BLOCK.N)) *H)) ?)"
  str = "Where is some blue block?"
  assert ulf2english.convert(ulf) == str

def test_42():
  ulf = "((SUB WHERE.A ((PRES BE.V) (THE.D (MOST-N LEFT.A (RED.A BLOCK.N))) *H)) ?)"
  str = "Where is the leftmost red block?"
  assert ulf2english.convert(ulf) == str

def test_43():
  ulf = "((SUB WHERE.A ((PRES BE.V) (ANY.D (CLEAR.A BLOCK.N)) *H)) ?)"
  str = "Where is any clear block?"
  assert ulf2english.convert(ulf) == str

def test_44():
  ulf = "((SUB WHERE.A ((PRES BE.V) (THE.D (MOST-N SHORT.A STACK.N)) *H)) ?)"
  str = "Where is the shortest stack?"
  assert ulf2english.convert(ulf) == str

def test_45():
  ulf = "((SUB WHERE.A ((PRES BE.V) (THE.D (MOST-N HIGH.A BLOCK.N)) *H)) ?)"
  str = "Where is the highest block?"
  assert ulf2english.convert(ulf) == str

def test_46():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (FACE.V (THE.D (FRONT.A (RIGHT.A (CORNER-OF.N (THE.D TABLE.N))))))))) ?)"
  str = "Is there a block facing the front right corner of the table?"
  assert ulf2english.convert(ulf) == str

def test_47():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (FACE.V (THE.D (FRONT.A (EDGE-OF.N (THE.D TABLE.N)))))))) ?)"
  str = "Is there a block facing the front edge of the table?"
  assert ulf2english.convert(ulf) == str

def test_48():
  ulf = "(((PRES BE.V) THERE.PRO (TWO.D (N+PREDS (PLUR BLOCK.N) (FACE.V (EACH.D (OTHER.N {REF}.N)))))) ?)"
  str = "Are there two blocks facing each other?"
  assert ulf2english.convert(ulf) == str

def test_49():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (IN.P (THE.D (MIDDLE-OF.N (THE.D TABLE.N))))))) ?)"
  str = "Is there a block in the middle of the table?"
  assert ulf2english.convert(ulf) == str

def test_50():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS STACK.N (NEAR.P (THE.D (CENTER-OF.N (THE.D TABLE.N))))))) ?)"
  str = "Is there a stack near the center of the table?"
  assert ulf2english.convert(ulf) == str

def test_51():
  ulf = "(((PRES BE.V) THERE.PRO (TWO.D (N+PREDS (PLUR STACK.N) (THAT.REL ((PRES BE.V) SIDE_BY_SIDE.A))))) ?)"
  str = "Are there two stacks that are side by side?"
  assert ulf2english.convert(ulf) == str

def test_52():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS (MOST-N SHORT.A STACK.N) (ON.P (THE.D TABLE.N))))) ?)"
  str = "Is there a shortest stack on the table?"
  assert ulf2english.convert(ulf) == str

def test_53():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (ON.P (THE.D (LEFT.A (SIDE-OF.N (THE.D TABLE.N)))))))) ?)"
  str = "Is there a block on the left side of the table?"
  assert ulf2english.convert(ulf) == str

def test_54():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (ON.P (THE.D (LEFT.A (SIDE-OF.N (THE.D TABLE.N)))))))) ?)"
  str = "Is there a block on the left side of the table?"
  assert ulf2english.convert(ulf) == str

def test_55():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (THAT.REL ((PRES BE.V) (SIDE_BY_SIDE.A (WITH.P-ARG (THE.D (| Nvidia| BLOCK.N))))))))) ?)"
  str = "Is there a block that is side by side with the Nvidia block?"
  assert ulf2english.convert(ulf) == str

def test_56():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (THAT.REL ((PRES BE.V) (SIDE_BY_SIDE.A (WITH.P-ARG (ANY.D (RED.A BLOCK.N))))))))) ?)"
  str = "Is there a block that is side by side with any red block?"
  assert ulf2english.convert(ulf) == str

def test_57():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (THAT.REL ((PRES BE.V) (BELOW.P (TWO.D (BLUE.A (PLUR BLOCK.N))))))))) ?)"
  str = "Is there a block that is below two blue blocks?"
  assert ulf2english.convert(ulf) == str

def test_58():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (ON.P ({THE}.D (TOP-OF.N (ANY.D STACK.N))))))) ?)"
  str = "Is there a block on top of any stack?"
  assert ulf2english.convert(ulf) == str

def test_59():
  ulf = "(((PRES BE.V) THERE.PRO (TWO.D (N+PREDS (PLUR BLOCK.N) (THAT.REL ((PRES BE.V) NOT.ADV-S (NEAR.P (EACH.D (OTHER.N {REF}.N)))))))) ?)"
  str = "Are there two blocks that are not near each other?"
  assert ulf2english.convert(ulf) == str

def test_60():
  ulf = "(((PRES BE.V) THERE.PRO (A.D (N+PREDS BLOCK.N (CLOSE.A (TO.P-ARG (ANY.D STACK.N)))))) ?)"
  str = "Is there a block close to any stack?"
  assert ulf2english.convert(ulf) == str

def test_61():
  ulf = "(SUB (WHAT.MOD-N COLOR.N) (((PRES BE.V) (THE.D (N+PREDS BLOCK.N (TO.P (THE.D (LEFT-OF.N (THE.D (| Nvidia| BLOCK.N))))))) *H) ?))"
  str = "What color is the block to the left of the Nvidia block?"
  assert ulf2english.convert(ulf) == str

def test_62():
  ulf = "(SUB (WHAT.MOD-N COLOR.N) (((PRES BE.V) (THE.D (N+PREDS BLOCK.N (THAT.REL ((PRES BE.V) (NEAR.P (THE.D (MOST-N LEFT.A (RED.A BLOCK.N)))))))) *H) ?))"
  str = "What color is the block that is near the leftmost red block?"
  assert ulf2english.convert(ulf) == str

def test_63():
  ulf = "(SUB (WHAT.MOD-N COLOR.N) (((PRES BE.V) (THE.D (N+PREDS (PLUR BLOCK.N) (NEAR.A (TO.P-ARG (THE.D (| Toyota| BLOCK.N)))))) *H) ?))"
  str = "What color are the blocks near to the Toyota block?"
  assert ulf2english.convert(ulf) == str

def test_64():
  ulf = "(SUB (WHAT.MOD-N COLOR.N) (((PRES BE.V) (THE.D (N+PREDS BLOCK.N (CLOSE.A (TO.P-ARG (THE.D (FRONT.A (EDGE-OF.N (THE.D TABLE.N)))))))) *H) ?))"
  str = "What color is the block close to the front edge of the table?"
  assert ulf2english.convert(ulf) == str

def test_65():
  ulf = "(SUB (WHAT.MOD-N COLOR.N) (((PRES BE.V) (THE.D (N+PREDS (PLUR BLOCK.N) (NEAR.P (ANY.D (EDGE-OF.N (THE.D TABLE.N)))))) *H) ?))"
  str = "What color are the blocks near any edge of the table?"
  assert ulf2english.convert(ulf) == str

def test_66():
  ulf = "((WHAT.PRO ((PRES BE.V) (= (THE.D (HEIGHT-OF.N (THE.D (MOST-N LEFT.A STACK.N))))))) ?)"
  str = "What is the height of the leftmost stack?"
  assert ulf2english.convert(ulf) == str

def test_67():
  ulf = "((WHAT.PRO ((PRES BE.V) (= (THE.D (LENGTH-OF.N (THE.D (MOST-N LONG.A ROW.N))))))) ?)"
  str = "What is the length of the longest row?"
  assert ulf2english.convert(ulf) == str

def test_68():
  ulf = "((SUB (WHAT.D DIRECTION.N) ((PRES PROG) (THE.D (| Toyota| BLOCK.N)) (FACE.V *H))) ?)"
  str = "What direction is the Toyota block facing?"
  assert ulf2english.convert(ulf) == str

def test_69():
  ulf = "(SUB (WHAT.MOD-N COLOR.N) (((PRES BE.V) (THE.D (N+PREDS (MIDDLE.A BLOCK.N) (IN.P (THE.D (MOST-N LONG.A ROW.N))))) *H) ?))"
  str = "What color is the middle block in the longest row?"
  assert ulf2english.convert(ulf) == str

def test_70():
  ulf = "(SUB (WHAT.MOD-N (PLUR COLOR.N)) (((PRES BE.V) (THE.D (N+PREDS (PLUR BLOCK.N) (THAT.REL ((PRES BE.V) (UNDER.P (SOME.D (BLUE.N BLOCK.N))))))) *H) ?))"
  str = "What colors are the blocks that are under some blue block?"
  assert ulf2english.convert(ulf) == str

def test_71():
  ulf = "(SUB (WHAT.MOD-N COLOR.N) (((PRES BE.V) (THE.D (N+PREDS (MOST-N LOW.A BLOCK.N) (OF.P (THE.D (MOST-N SHORT.A STACK.N))))) *H) ?))"
  str = "What color is the lowest block of the shortest stack?"
  assert ulf2english.convert(ulf) == str

def test_72():
  ulf = "(SUB (WHAT.MOD-N COLOR.N) (((PRES BE.V) (THE.D (N+PREDS (LAST.A BLOCK.N) (IN.P (THE.D (MOST-N LEFT.A ROW.N))))) *H) ?))"
  str = "What color is the last block in the leftmost row?"
  assert ulf2english.convert(ulf) == str

def test_73():
  ulf = "(((K ((HOW.MOD-A MANY.A) (PLUR BLOCK.N))) ((PRES PROG) (FACE.V (ANY.D (N+PREDS CORNER.N (OF.P (THE.D TABLE.N))))))) ?)"
  str = "How many blocks are facing any corner of the table?"
  assert ulf2english.convert(ulf) == str

def test_74():
  ulf = "(((K ((HOW.MOD-A MANY.A) (PLUR STACK.N))) ((PRES BE.V) (ON.P (THE.D TABLE.N)))) ?)"
  str = "How many stacks are on the table?"
  assert ulf2english.convert(ulf) == str

def test_75():
  ulf = "(((K ((HOW.MOD-A MANY.A) (PLUR ROW.N))) ((PRES BE.V) (ON.P (THE.D TABLE.N)))) ?)"
  str = "How many rows are on the table?"
  assert ulf2english.convert(ulf) == str

def test_76():
  ulf = "(((K ((HOW.MOD-A MANY.A) (PLUR BLOCK.N))) ((PRES BE.V) (ON.P (THE.D (N+PREDS (LEFT.A SIDE.N) (OF.P (THE.D TABLE.N))))))) ?)"
  str = "How many blocks are on the left side of the table?"
  assert ulf2english.convert(ulf) == str

def test_77():
  ulf = "(((K ((HOW.MOD-A MANY.A) (PLUR BLOCK.N))) ((PRES BE.V) (IN.P (THE.D (MOST-N TALL.A STACK.N))))) ?)"
  str = "How many blocks are in the tallest stack?"
  assert ulf2english.convert(ulf) == str

def test_78():
  ulf = "(((K ((HOW.MOD-A MANY.A) (PLUR BLOCK.N))) ((PRES BE.V) (IN.P (THE.D (MOST-N LONG.A ROW.N))))) ?)"
  str = "How many blocks are in the longest row?"
  assert ulf2english.convert(ulf) == str

def test_79():
  ulf = "(((K ((HOW.MOD-A MANY.A) (PLUR BLOCK.N))) ((PRES BE.V) (BETWEEN.P (ANY.D (TWO.A (PLUR STACK.N)))))) ?)"
  str = "How many blocks are between any two stacks?"
  assert ulf2english.convert(ulf) == str

def test_80():
  ulf = "(((K ((HOW.MOD-A MANY.A) (PLUR BLOCK.N))) ((PRES BE.V) CLEAR.A)) ?)"
  str = "How many blocks are clear?"
  assert ulf2english.convert(ulf) == str

def test_81():
  ulf = "(((K ((HOW.MOD-A MANY.A) (PLUR BLOCK.N))) ((PRES BE.V) (IN.P (SOME.D (ROW.N OR.CC STACK.N))))) ?)"
  str = "How many blocks are in some row or stack?"
  assert ulf2english.convert(ulf) == str

def test_82():
  ulf = "(((K ((HOW.MOD-A MANY.A) (PLUR BLOCK.N))) ((PRES PROG) NOT.ADV-S (TOUCH.V (THE.D TABLE.N)))) ?)"
  str = "How many blocks are not touching the table?"
  assert ulf2english.convert(ulf) == str

def test_83():
  ulf = "((WHAT.PRO ((PRES BE.V) (= (THE.D (N+PREDS (PLUR BLOCK.N) (ON.P (K (N+PREDS TOP.N (OF.P (THE.D (| Toyota.N| BLOCK.N))))))))))) ?)"
  str = "What are the blocks on top of the Toyota block?"
  assert ulf2english.convert(ulf) == str

def test_84():
  ulf = "((WHAT.PRO ((PRES BE.V) (= (THE.D (N+PREDS (PLUR BLOCK.N) (THAT.REL ((PRES BE.V) NOT.ADV-S (ON.P (K (N+PREDS TOP.N (OF.P (ANY.D (OTHER.A BLOCK.N))))))))))))) ?)"
  str = "What are the blocks that are not on top of any other block?"
  assert ulf2english.convert(ulf) == str

def test_85():
  ulf = "((WHAT.PRO ((PRES BE.V) (= (THE.D (N+PREDS BLOCK.N (BETWEEN.P ((THE.D (| Toyota.N| {BLOCK}.N)) AND.CC (THE.D (| SRI.N| BLOCK.N))))))))) ?)"
  str = "What is the block between the Toyota and the SRI block?"
  assert ulf2english.convert(ulf) == str

def test_86():
  ulf = "((WHAT.PRO ((PRES BE.V) (= (THE.D (PLUR (N+PREDS BLOCK.N (NEAR.P (THE.D (PLUR (N+PREDS CORNER.N (OF.P (THE.D TABLE.N)))))))))))) ?)"
  str = "What are the blocks near the corners of the table?"
  assert ulf2english.convert(ulf) == str

def test_87():
  ulf = "((WHAT.PRO ((PRES BE.V) (= (THE.D (N+PREDS BLOCK.N (ON.P (K (N+PREDS TOP.N (OF.P (THE.D (MOST-N TALL.A STACK.N))))))))))) ?)"
  str = "What is the block on top of the tallest stack?"
  assert ulf2english.convert(ulf) == str

def test_88():
  ulf = "((WHAT.PRO ((PRES BE.V) (= (THE.D (N+PREDS (PLUR BLOCK.N) (BEHIND.P (THE.D (| Nvidia.N| BLOCK.N)))))))) ?)"
  str = "What are the blocks behind the Nvidia block?"
  assert ulf2english.convert(ulf) == str

def test_89():
  ulf = "((WHAT.PRO ((PRES BE.V) (= (THE.D (N+PREDS BLOCK.N (THAT.REL ((PRES BE.V) (AT.P (THE.D (MOST-N RIGHT.A (RED.A BLOCK.N))))))))))) ?)"
  str = "What is the block that is at the rightmost red block?"
  assert ulf2english.convert(ulf) == str

def test_90():
  ulf = "(((WHICH.D BLOCK.N) ((PRES BE.V) (= (THE.D (MOST-N HIGH.A {BLOCK}.N))))) ?)"
  str = "Which block is the highest?"
  assert ulf2english.convert(ulf) == str

def test_91():
  ulf = "(((WHICH.D BLOCK.N) ((PRES BE.V) (ON.P (TWO.D (OTHER.A (PLUR BLOCK.N)))))) ?)"
  str = "Which block is on two other blocks?"
  assert ulf2english.convert(ulf) == str

def test_92():
  ulf = "(((WHICH.D BLOCK.N) ((PRES BE.V) (IN.P (THE.D (N+PREDS CENTER.N (OF.P (THE.D TABLE.N))))))) ?)"
  str = "Which block is in the center of the table?"
  assert ulf2english.convert(ulf) == str

def test_93():
  ulf = "(((WHAT.D (PLUR BLOCK.N)) ((PRES BE.V) (IN.P (THE.D (MOST-N LONG.A ROW.N))))) ?)"
  str = "What blocks are in the longest row?"
  assert ulf2english.convert(ulf) == str

def test_94():
  ulf = "(((WHAT.D BLOCK.N) ((PRES BE.V) (HALFWAY.MOD-A (ON.P (K (N+PREDS TOP.N (OF.P (ANY.D (OTHER.A BLOCK.N))))))))) ?)"
  str = "What block is halfway on top of any other block?"
  assert ulf2english.convert(ulf) == str

def test_95():
  ulf = "(((WHICH.D BLOCK.N) ((PRES BE.V) (SIDE_BY_SIDE.A (WITH.P-ARG (THE.D (| Texaco.N| BLOCK.N)))))) ?)"
  str = "Which block is side by side with the Texaco block?"
  assert ulf2english.convert(ulf) == str

def test_96():
  ulf = "((SUB (WHICH.D BLOCK.N) ((THE.D (| Nvidia.N| BLOCK.N)) ((PRES BE.V) (ON.P (K (N+PREDS TOP.N (OF.P *H))))))) ?)"
  str = "Which block the Nvidia block is on top of?"
  assert ulf2english.convert(ulf) == str

def test_97():
  ulf = "(((WHICH.D BLOCK.N) ((PRES BE.V) ((MOD-A (VERY.MOD-A CLOSE.A)) (TO.P (THE.D (FRONT.A (N+PREDS EDGE.N (OF.P (THE.D TABLE.N))))))))) ?)"
  str = "Which block is very close to the front edge of the table?"
  assert ulf2english.convert(ulf) == str

def test_98():
  ulf = "((WHAT.PRO ((PRES BE.V) (IN.P (THE.D (N+PREDS MIDDLE.N (OF.P (THE.D TABLE.N))))))) ?)"
  str = "What is in the middle of the table?"
  assert ulf2english.convert(ulf) == str

def test_99():
  ulf = "(((WHICH.D (RED.A (PLUR BLOCK.N))) ((PRES BE.V) (DIRECTLY.MOD-A (ON.P (THE.D TABLE.N))))) ?)"
  str = "Which red blocks are directly on the table?"
  assert ulf2english.convert(ulf) == str