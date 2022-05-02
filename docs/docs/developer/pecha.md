# Pecha

## Create new pecha
```python
{!../../docs_src/developer/pecha/create_new_pecha.py!}
```

When we are creating a brand new pecha, first we must create an instance of `PechaMetaData`, which will automatically issue a unique id for the pecha and allow us to specify other metadata about the pecha.

Then, we will use this metadata object to create pecha container, instance of `OpenPechaFS`.

After adding *base* and *layer(s)* we need to call `pecha.save()` to save pecha to file system in [OpenPecha Format](../opf-format.md).


## Adding Base and Layer

Refer [layer](layer.md) docs to how to create layer.

```python
{!../../docs_src/developer/pecha/add_base_and_layer.py!}
```

After successfully parsing the input, you should be able to get base text and layers.

Since, layers are based on the base text, first you need to set base to `pecha` with `pecha.set_base('base content`) which will return `base_name`, which is identifier for base and it's associated layers. Then you use `base_name` to set layer to `pecha`.

After adding all the bases and layer, call `pecha.save()` to save bases and layers.

## Update Base layer
In order to update a base, we need to know the `base_name` of base that we want to update.

```python
{!../../docs_src/developer/pecha/update_base_layer.py!}
```
