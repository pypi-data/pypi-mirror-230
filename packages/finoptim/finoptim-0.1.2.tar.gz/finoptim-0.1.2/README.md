# FinOptim package 

The best python package to help you optimise your cloud spendings

### Instalation

The package is available [on PyPI](https://pypi.org/project/finoptim/), so you can install it directly with pip. 

```sh
pip install finoptim
```

It requires at least Python 3.10. The documentation is available on readthedoc at : xxxxxx (not possible with a private repo)


### Usage example


```python
import finoptim as fp
import pandas as pd


past_usage = pd.DataFrame(...) # some query of yours
prices = fp.prices.aws()
print(prices_df.iloc[:, :4].to_markdown(
    index=False,
    tablefmt='rounded_outline',
    numalign='center'))
>>>
╭────────────┬──────────────┬─────────────────┬──────────────╮
│  Arlequin  │  Moratorium  │  Anthropophage  │  Apophtegme  │
├────────────┼──────────────┼─────────────────┼──────────────┤
│   0.167    │    0.122     │     0.0056      │    0.0058    │
│   0.073    │    0.054     │     0.0025      │    0.0026    │
│ 0.0637352  │  0.0476682   │    0.0022035    │  0.00234155  │
╰────────────┴──────────────┴─────────────────┴──────────────╯
```
All the prices are per hours.

Proceeding to the optimisation is made with the `optimise` function
```
res = fp.optimise(past_usage, prices)
```
The `optimise` function can take as input lots of different predictions, and also current commitments. The optimisation is made with all the pricing models found in the `prices` object

```python
predictions = [pd.DataFrame(...), ...] # some query of yours
current_reservations = pd.DataFrame(...) # some query of yours

res = fp.optimise_past(predictions, prices, current_reservations)
```

Now the `res` object hold the best levels of commitment on the time period.

```python
guid_to_instance_name = {"K7YHHNFGTNN2DP28" : 'i3.large', 'SAHHHV5TXVX4DCTS' : 'r5.large'}
res.format(instance_type=guid_to_instance_name)
print(res)
>>>
╭─────────────────┬──────────────────────────┬───────────────╮
│ instance_type   │  three_year_commitments  │ price_per_day │
├─────────────────┼──────────────────────────┼───────────────┤
│ i3.large        │           1338           │     2,886     │
│ r5.large        │           1570           │     2,564     │
│ savings plans   │           1937           │     1,937     │
╰─────────────────┴──────────────────────────┴───────────────╯
```


### TODO

#### lib convenience

- possibility to precise the period of the data in case it is not inferred correctly
- coverage must follow the same inputs as cost
- allow for long DataFrame as input
- the cost function should return a gradient when evaluated (save some compute)
- need to listen to keyboard interupt from Rust (harder than expected with multi threading)


#### actual problems

- add in documentation that for now optimisation only works if you have RI < SP < OD
- compute the better step size to avoid waiting too long (more or less done, but not even necessary with the inertial optimiser)
- find a real stop condition for the inertial optimiser
- can we guess the "eigenvectors" of the problem ? if we have estimations, we can set great parameters for the inertial optimiser
    - problem is highly non linear and this will require more thinking


if the problem is  $f(w) = \frac{1}{2} w^T A w \:-\: b^T w$ then the optimal parameters for the inertial optimiser are :

$$ \alpha = \left(\frac{2}{\sqrt{\lambda_1} + \sqrt{\lambda_n}} \right) ^2 $$

$$ \beta = \left( \frac{\sqrt{\lambda_n} - \sqrt{\lambda_1}}{\sqrt{\lambda_1} + \sqrt{\lambda_n}} \right) ^2 $$

with $\lambda_1$ and $\lambda_n$ respectively the smallest and largest eigenvalues of $A$

lets admit constant usage for all the instances. Then $f(w) = $

### Project size

`wc -l src/finoptim/*.py rust/src/*.rs src/finoptim/prices/*.py tests/*.py`

is around 3k lines of code