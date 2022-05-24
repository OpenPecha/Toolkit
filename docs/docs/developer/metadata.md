# Pecha Metadata

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
