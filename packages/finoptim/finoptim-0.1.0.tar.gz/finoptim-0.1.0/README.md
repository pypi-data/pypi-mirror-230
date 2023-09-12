# FinOps package 

The best python package to help you optimise your cloud spendings



### Usage example


```python
import finoptim as fp
import pandas as pd


past_usage = pd.DataFrame(...)
guid_to_price = fp.cloud.load_aws_prices(as_dict=True)
prices = np.array(past_usqge.index.map(guid_to_price))

usage = fp.normalize(past_usage)

res = fp.optimise_past(usage, prices)
```


```python
predictions = pd.DataFrame(...) # some SQL query
current_reservations = pd.DataFrame(...) # some SQL query

normalize_reservations = fp.normalize(current_reservations)

res = fp.optimise_past(predictions, prices)
```

Now the res object hold the best levels of commitment on the time period.

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


if the problem is  $f(w) = \frac{1}{2} w^T A w \:-\: b^T w$ then the optimal parameters for the inertial optimiser are :

$$ \alpha = \left(\frac{2}{\sqrt{\lambda_1} + \sqrt{\lambda_n}} \right) ^2 $$

$$ \beta = \left( \frac{\sqrt{\lambda_n} - \sqrt{\lambda_1}}{\sqrt{\lambda_1} + \sqrt{\lambda_n}} \right) ^2 $$

with $\lambda_1$ and $\lambda_n$ respectively the smallest and largest eigenvalues of $A$

lets admit constant usage for all the instances. Then $f(w) = $