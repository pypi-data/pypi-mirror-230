# Agently 2.0

## QUICK START

```python
import Agently
worker = Agently.create_worker()
worker.set_llm_name("GPT").set_llm_auth("GPT", "Your-API-Key")
result = worker\
    .input("Give me 5 words and 1 sentence.")\
    .output({
        "words": ("Array",),
        "sentence": ("String",),
    })\
    .start()
print(result)
print(result["words"][2])
```

## Recently Update

support new models:

- XunFei Spark
- Baidu WenXin Workshop

## MORE INFORMATION

Python`v2.0.3`: [Chinese](https://github.com/Maplemx/Agently/blob/main/README.md)

NodeJS`v1.1.3`: [English](https://github.com/Maplemx/Agently/blob/main/README_node_v1_EN.md) | [Chinese](https://github.com/Maplemx/Agently/blob/main/README_node_v1_CN.md)