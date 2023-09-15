# wordpredict

This is a library that predicts words for ambiguous input.

## Installation

```bash
pip install wordpredict
```

## How to use

### code

```python
import pandas as pd
from wordpredict import WordPredict


corpus = pd.read_csv(
    "./unigram_freq.csv",
    header=0,
    keep_default_na=False,
).values
wp = WordPredict(corpus[:, 0], corpus[:, 1])

print("start user input")

input = ["e", "f", "g", "h"]
print(wp.update(input))
input = ["e", "f", "g", "h"]
print(wp.update(input))
input = ["i", "j", "k", "l"]
print(wp.update(input))

print("reset user input")
wp.reset()

input = ["e", "f", "g", "h"]
print(wp.update(input))
input = ["m", "n", "o", "p"]
print(wp.update(input))
```

### output

```
start user input
['for', 'e', 'from', 'he', 'has', 'have']
['he', 'get', 'here', 'her', 'help', 'few']
['help', 'held', 'felt', 'hell', 'hello', 'helps']
reset user input
['for', 'e', 'from', 'he', 'has', 'have']
['for', 'home', 'go', 'how', 'good', 'end']
```

### corpus

e.g., https://www.kaggle.com/datasets/rtatman/english-word-frequency

## execution time

```python
%%timeit

import pandas as pd
from wordpredict import WordPredict


corpus = pd.read_csv(
    "./unigram_freq.csv",
    header=0,
    keep_default_na=False,
).values
wp = WordPredict(corpus[:, 0], corpus[:, 1])
```

1.42 s ± 83.7 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

```python
%%timeit

input = ["e", "f", "g", "h"]
wp.update(input)
input = ["e", "f", "g", "h"]
wp.update(input)
input = ["i", "j", "k", "l"]
wp.update(input)
```

8.34 ms ± 315 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

## note

autocomple was implemented with reference to https://doi.org/10.1145/3173574.3173755
