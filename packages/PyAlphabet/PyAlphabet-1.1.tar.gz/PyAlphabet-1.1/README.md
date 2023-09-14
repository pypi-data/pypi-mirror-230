# PyAlphabet
[![Telegram](https://img.shields.io/badge/telegram-channel-0088cc.svg)](https://t.me/ProgramsCreatorRu)

# Using

```python
from PyAlphabet.AlphabetLetters import AlphabetLetters

alphabet_letters = AlphabetLetters("a", "z")
print(alphabet_letters)
# Aa Bb Cc Dd Ee Ff Gg Hh Ii Jj Kk Ll Mm Nn Oo Pp Qq Rr Ss Tt Uu Vv Ww Xx Yy Zz
```
Outputs an alphabet with large and small letters
You can also add flags.


```python
from PyAlphabet.AlphabetLetters import AlphabetLetters

alphabet_letters = AlphabetLetters("a", "z", flag_upper=False)
print(alphabet_letters)
# a b c d e f g h i j k l m n o p q r s t u v w x y z
```
Outputs only lowercase letters
You can also disable the checkbox for lowercase letters.

Return capital letters back to `flag_upper=True`

```python
from PyAlphabet.AlphabetLetters import AlphabetLetters

alphabet_letters = AlphabetLetters("a", "z", flag_upper=True, flag_lower=False)
print(alphabet_letters)
# ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

>If you disable both `flag_upper=False` and `flag_lower=False`, the response will return `None`

Consider the `flag_reflected` flag.
By default, the flag_reflected flag is set to `False`, we will fix it to `True`:

```python
from PyAlphabet.AlphabetLetters import AlphabetLetters

alphabet_letters = AlphabetLetters("a", "z", flag_upper=True, flag_lower=True, flag_reflected=True)
print(alphabet_letters)
#  zZ yY xX wW vV uU tT sS rR qQ pP oO nN mM lL kK jJ iI hH gG fF eE dD cC bB aA
```

The last flag is flag_line
By default, the flag_reflected flag is set to `False`, we will fix it to `True`:

```python
from PyAlphabet.AlphabetLetters import AlphabetLetters

alphabet_letters = AlphabetLetters("a", "z", flag_upper=True, flag_lower=True, flag_reflected=False, flag_line=True)
print(alphabet_letters)
"""Aa 
Bb
Cc
Dd
Ee
...
Zz"""
```