import sys
sys.path.append("src/")

from ulflib import ulflib

# print(ulflib.apply_substitution_macros(['sub', ['the.d', 'dog.n'], ['|John|', [['past', 'pet.v'], '*h']]]))
# print(ulflib.apply_substitution_macros(['|Mary|', [['past', 'go.v'], ['to.p', ['the.d', 'store.n']]]]))

print(ulflib.noun_p(['n+preds', 'dog.n', ['above.p', 'it.pro']]))
print(ulflib.adj_p(['very.mod-a', 'red.a']))
print(ulflib.vp_head_p(['past', 'test.v']))