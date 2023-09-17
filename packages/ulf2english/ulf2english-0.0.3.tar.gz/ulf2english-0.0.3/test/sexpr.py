import sys
sys.path.append("src/")

from ulf2english import sexpr

print(sexpr.parse_s_expr('(this.pro ((pres be.v) (= (a.d |TEST.N|))))'))