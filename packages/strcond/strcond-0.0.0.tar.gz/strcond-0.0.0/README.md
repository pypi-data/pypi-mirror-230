The explanations in English, Simplified Chinese, and Spanish are provided below.
下面提供了英语、简体中文和西班牙语的说明。
Las explicaciones en inglés, chino simplificado y español se proporcionan a continuación.

# strcond: 文字列条件判定ツール (日本語版)

## 概要
`strcond`は、ある文字列（HTMLなど）がAND・OR条件が組み合わさったクエリの条件を満たすかどうかを判定するPythonライブラリです。条件はネスト（入れ子）にすることができ、動的に条件を変更する際にも非常に便利です。

## ツール特徴
- ある文字列（HTMLなど）がAND・OR条件が組み合わさったクエリの条件を満たすかどうかを判定します。
- 「ある部分文字列が含まれるか」の判定を、何重かにAND、OR条件でネストした条件を扱うことができます。
- このツールは、「ネストされた条件がJSON等で与えられ、それが固定でなく可変の場合」という少々ややこしい場面で有用です
- 「あるHTMLで書かれたWebページが所定の条件を満たすかどうかの判定」などに用いることができます。

## インストール方法
```bash
pip install strcond
```

## ソースコード例

以下は基本的な使用例です。

```python
import strcond  # 文字列条件判定ツール [strcond]

# 文字列が条件を満たすかどうか判定
flag = strcond.judge(
    target_str="これはカレーについての説明文です。",
    cond=["and", "説明文",
          ["or", "カレー", "カツ丼"]
    ]
)
print(flag)  # -> True

# 条件を満たさない例
flag = strcond.judge(
    target_str="これはナンについての説明文です。",
    cond=["and", "説明文",
          ["or", "カレー", "カツ丼"]
    ]
)
print(flag)  # -> False

# もう一つの条件を満たさない例
flag = strcond.judge(
    target_str="これはカツ丼についての感想です。",
    cond=["and", "説明文",
          ["or", "カレー", "カツ丼"]
    ]
)
print(flag)  # -> False
```

## 注意点
- `cond` 引数で与える条件はリスト形式で、`["and", ...]` や `["or", ...]` のように指定します。
- 文字列の大文字・小文字は区別されます。
- 文字列内に特殊文字やエスケープシーケンスが含まれる場合は、正確な判定ができない可能性があります。


# strcond: String Condition Evaluation Tool (English Version)

## Overview
`strcond` is a Python library designed to evaluate whether a given string (such as HTML) satisfies a query that involves a combination of AND and OR conditions. The conditions can be nested and are extremely useful for dynamically altering criteria.

## Features
- Evaluates whether a given string (e.g., HTML) meets a query composed of AND and OR conditions.
- Can handle nested conditions involving phrases like "includes a certain substring," using multiple layers of AND and OR conditions.
- Accepts nested conditions in the form of JSON or other formats, facilitating easy implementation through recursive calls.
- Useful for tasks like "determining whether a web page written in HTML meets specific conditions."

## Installation
```bash
pip install strcond
```

## Example Code

Here are some basic examples:

```python
import strcond  # String Condition Evaluation Tool

# Evaluates whether a string meets a condition
flag = strcond.judge(
    target_str="This is a description about curry.",
    cond=["and", "description",
          ["or", "curry", "pork cutlet"]
    ]
)
print(flag)  # -> True

# An example that does not meet the conditions
flag = strcond.judge(
    target_str="This is a description about naan.",
    cond=["and", "description",
          ["or", "curry", "pork cutlet"]
    ]
)
print(flag)  # -> False

# Another example that does not meet the conditions
flag = strcond.judge(
    target_str="This is an opinion about pork cutlet.",
    cond=["and", "description",
          ["or", "curry", "pork cutlet"]
    ]
)
print(flag)  # -> False
```

## Caution
- The `cond` argument takes conditions in a list format, specified as `["and", ...]` or `["or", ...]`.
- The string comparison is case-sensitive.
- Special characters and escape sequences in the string may lead to inaccurate evaluations.

---

# strcond: 字符串条件评估工具 (简体中文版本)

## 概述
`strcond`是一个Python库，用于评估给定的字符串（如HTML）是否满足涉及AND和OR条件组合的查询。条件可以嵌套，并且在动态改变条件时非常有用。

## 功能
- 评估给定的字符串（例如，HTML）是否满足由AND和OR条件组成的查询。
- 可以处理涉及“包括某个子字符串”的嵌套条件，使用多层AND和OR条件。
- 以JSON或其他格式接受嵌套条件，方便通过递归调用进行实现。
- 适用于“确定用HTML编写的网页是否满足特定条件”等任务。

## 安装
```bash
pip install strcond
```

## 示例代码

以下是一些基础示例：

```python
import strcond  # 字符串条件评估工具

# 评估字符串是否满足条件
flag = strcond.judge(
    target_str="这是关于咖喱的描述。",
    cond=["and", "描述",
          ["or", "咖喱", "猪排"]
    ]
)
print(flag)  # -> True

# 不满足条件的示例
flag = strcond.judge(
    target_str="这是关于馕的描述。",
    cond=["and", "描述",
          ["or", "咖喱", "猪排"]
    ]
)
print(flag)  # -> False

# 另一个不满足条件的示例
flag = strcond.judge(
    target_str="这是关于猪排的感想。",
    cond=["and", "描述",
          ["or", "咖喱", "猪排"]
    ]
)
print(flag)  # -> False
```

## 注意事项
- `cond`参数以列表格式接受条件，指定为 `["and", ...]` 或 `["or", ...]`。
- 字符串比较区分大小写。
- 字符串中的特殊字符和转义序列可能导致评估不准确。

---

# strcond: Herramienta de evaluación de condiciones de cadenas (Versión en español)

## Resumen
`strcond` es una biblioteca de Python diseñada para evaluar si una cadena dada (como HTML) cumple con una consulta que involucra una combinación de condiciones AND y OR. Las condiciones pueden ser anidadas y son extremadamente útiles para alterar dinámicamente los criterios.

## Características
- Evalúa si una cadena dada (por ejemplo, HTML) cumple con una consulta compuesta de condiciones AND y OR.
- Puede manejar condiciones anidadas que involucran frases como "incluye una cierta subcadena", utilizando múltiples capas de condiciones AND y OR.
- Acepta condiciones anidadas en forma de JSON u otros formatos, facilitando la implementación fácil a través de llamadas recursivas.
- Útil para tareas como "determinar si una página web escrita en HTML cumple con condiciones específicas".

## Instalación
```bash
pip install strcond
```

## Ejemplo de código

Aquí hay algunos ejemplos básicos:

```python
import strcond  # Herramienta de evaluación de condiciones de cadenas

# Evalúa si una cadena cumple con una condición
flag = strcond.judge(
    target_str="Esta es una descripción sobre curry.",
    cond=["and", "descripción",
          ["or", "curry", "milanesa de cerdo"]
    ]
)
print(flag)  # -> True

# Un ejemplo que no cumple con las condiciones
flag = strcond.judge(
    target_str="Esta es una descripción sobre naan.",
    cond=["and", "descripción",
          ["or", "curry", "milanesa de cerdo"]
    ]
)
print(flag)  # -> False

# Otro ejemplo que no cumple con las condiciones
flag = strcond.judge(
    target_str="Esta es una opinión sobre milanesa de cerdo.",
    cond=["and", "descripción",
          ["or", "curry", "milanesa de cerdo"]
    ]
)
print(flag)  # -> False
```

## Precauciones
- El argumento `

cond` toma condiciones en un formato de lista, especificado como `["and", ...]` o `["or", ...]`.
- La comparación de cadenas distingue entre mayúsculas y minúsculas.
- Los caracteres especiales y las secuencias de escape en la cadena pueden llevar a evaluaciones inexactas.
