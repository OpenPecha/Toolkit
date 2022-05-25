# Pecha Metadata

# Create Metadata for a Pecha

Since, OpenPecha as has three types of pecha, we have metadata classes to create metadata for each type of pecha. Here is the list of pecha types with it's associated metadata class.

Pecha Type | ID format | Metadata Class
---|---|---
Initial Pecha | I######## | `openpecha.core.metadata.InitialPechaMetadata`
Diplomatic Pecha | D######## | `openpecha.core.metadata.DiplomaticPechaMetadata`
Open Pecha | O######## | `openpecha.core.metadata.OpenPechaMetadata`

here is an example to create metadata for *Initial Pecha* type

```python
{!../../docs_src/developer/metadata/create_metadata_tutorial001.py!}
```

!!! attention

    Only the `initial_creation_type` attribute is required, rest of the attributes are optional.

!!! attention

    No need to assign pecha id when creating metadata, the metadata class will automatically create id with correct id prefix for a particular pecha type.

## Adding Copyright and License

here is an example to add copyright and license in pecha's metadata

```python
{!../../docs_src/developer/metadata/add_copyright_and_license.py!}
```

### Copyright Status

OpenPecha provides three Copyright Status:

- `CopyrightStatus.UNKNOWN`, use if the Copyright of the pecha is unknown.
- `CopyrightStatus.COPYRIGHTED`, use if the pecha source is Copyright restricted.
- `CopyRightStatus.PUBLIC_DOMAIN`, use if the pecha source is in [Public Domain](https://wiki.creativecommons.org/wiki/Public_domain).


### Licenses

OpenPecha relies on [Creative Common Licenses](https://creativecommons.org/licenses/) for licensing any pecha on OpenPecha Repository,

We can access Creative Common Licenses through `LicenseType` enum.
