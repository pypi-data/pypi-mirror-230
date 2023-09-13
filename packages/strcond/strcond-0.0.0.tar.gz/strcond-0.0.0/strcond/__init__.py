# 文字列条件判定ツール [strcond]

import sys
from sout import sout

# 条件の指定方法が不正な場合の例外
cond_format_exception = Exception("[strcond error] The format of the condition is invalid. Condition must be structured as a nested list that starts with a logical operator (such as 'and' or 'or').")

# 文字列が条件を満たすかどうか判定
def judge(
	target_str,	# 条件を判定する対象の文字列
	cond	# 条件
):
	# 対象文字列の型エラー
	if type(target_str) != type(""):
		raise Exception("[strcond error] The processing target (target_str) must be of string type.")
	# 再帰終了条件
	if type(cond) == type(""):
		return (cond in target_str)
	# 条件の書き方の妥当性判断
	if type(cond) != type([]): raise cond_format_exception
	if len(cond) < 1: raise cond_format_exception
	# 論理結合される対象の条件列を先に判断
	int_tf_ls = [
		int(judge(target_str, c))
		for c in cond[1:]
	]
	# 論理演算子に応じて分岐
	op = cond[0]
	if op == "and":
		return (sum(int_tf_ls) == len(int_tf_ls))
	elif op == "or":
		return (sum(int_tf_ls) > 0)
	else:
		raise cond_format_exception
