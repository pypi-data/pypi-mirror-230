import sys
sys.path.append("src/")

from ulf2english import ulf2english

# ulf = ['John', [['pres', 'perf'], 'go.v', 'there.pro']]
# ulf = ['John', [['pres', 'prog'], 'go.v', ['to.p', ['the.d', 'store.n']]]]
# ulf = ['John', [['prog', 'go.v'], 'there.pro']]
# ulf = [['set-of', 'Testone.name', 'Testtwo.name', 'Testthree.name'], [['pres', 'be.v'], ['=', ['a.d', ['test.a', 'ulf.n']]]]]
# ulf = ['John', ['pres', ['pasv', 'confuse.v']]]
ulf = ['this.pro', [['pres', 'be.v'], ['=', ['a.d', ['test.n', 'ulf.n']]]]]
# ulf = [['what.pro', [['pres', 'be.v'], ['=', ['that.d', 'thing.n']]]], '?']

print(ulf2english.convert(ulf, verbose=True))

# print(ulf2english.convert(ulf))
# print(ulf2english.convert(ulf, add_punct=False))
# print(ulf2english.convert(ulf, capitalize_front=False))
# print(ulf2english.convert(ulf, add_commas=True))
# print(ulf2english.convert(ulf, standardize=True))