# 文字列条件判定ツール [strcond]
# 【動作確認 / 使用例】

import sys
from sout import sout
from ezpip import load_develop
# 文字列条件判定ツール [strcond]
strcond = load_develop("strcond", "../", develop_flag = True)

# 文字列が条件を満たすかどうか判定
flag = strcond.judge(
	target_str = "これはカレーについての説明文です。",
	cond = ["and", "説明文",
		["or", "カレー", "カツ丼"]
	]
)
# 結果確認
print(flag)	# -> True

# 文字列が条件を満たすかどうか判定
flag = strcond.judge(
	target_str = "これはナンについての説明文です。",
	cond = ["and", "説明文",
		["or", "カレー", "カツ丼"]
	]
)
# 結果確認
print(flag)	# -> False

# 文字列が条件を満たすかどうか判定
flag = strcond.judge(
	target_str = "これはカツ丼についての感想です。",
	cond = ["and", "説明文",
		["or", "カレー", "カツ丼"]
	]
)
# 結果確認
print(flag)	# -> False
