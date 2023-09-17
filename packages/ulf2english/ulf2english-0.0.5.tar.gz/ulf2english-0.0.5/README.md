# Python ULF-to-English

Maps Unscoped Logical Form (ULF) formulas to English sentences. A Python port of the original [Common Lisp ulf2english implementation](https://github.com/genelkim/ulf2english) by Gene Kim.

## Dependencies

* [pattern](https://github.com/clips/pattern); If using Python 3, install with `pip install pattern`.
* [ulflib](https://pypi.org/project/ulflib/)
* [transduction](https://pypi.org/project/transduction/)
* [memoization](https://pypi.org/project/memoization/)

## Summary

Install the package using `pip install ulf2english`.

The following example shows how to convert ULF to English using the package:

```python
from ulf2english import ulf2english

ulf = ['this.pro', [['pres', 'be.v'], ['=', ['a.d', ['test.n', 'ulf.n']]]]]
ulf2english.convert(ulf)
# -> "This is a test ulf."
```

The following optional parameters can be given to the convert function:

* `add_punct = False` : omit any final punctuation in the generated sentence.
* `capitalize_front = False` : do not capitalize the first word in the generated sentence.
* `add_commas = True` : add commas to the generated sentence in particular sub-expressions.
* `standardize = True` : standardize the generated sentence by converting to all-lowercase and adding space around all punctuation.
* `verbose = True` : print the intermediate staged output after each processing stage.

