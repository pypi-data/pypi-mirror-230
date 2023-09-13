![Tests](https://github.com/strangeworks/strangeworks-optimization/actions/workflows/cron_test.yml/badge.svg)

# strangeworks-optimization

[Docs](https://docs.strangeworks.com/apps/optimization)


## Usage

```python
# model has been created and is one of the StrangeworksModelTypes
model = ...
solver = "my_provider.my_solver"
optimizer = StrangeworksOptimizer(model, solver)
optimizer.run()
print(optimizer.status())
print(optimizer.results())
```
