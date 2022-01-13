# Pecha

## Adding Base and Layer

Refer [layer](layer.md) docs to how to create layer.

```python
{!../../docs_src/developer/pecha/add_base_and_layer.py!}
```

After successfully parsing the input, you should be able to get base text and layers.

Then create an `OpenPecha` instance (for eg, `pecha`), which is act like a storage for storing base and layers.

Since, layers are based on the base text, first you need to set base to `pecha` with `pecha.set_base('base content`) which will return `base_name`, which is identifier for base and it's associated layers. Then you use `base_name` to set layer to `pecha`.

After adding all the bases and layer, call `pecha.save()` to save bases and layers.
