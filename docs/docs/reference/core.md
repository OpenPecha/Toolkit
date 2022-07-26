# Core

## OpenPecha

::: openpecha.core.pecha.OpenPecha
    options:
        members:
            - pecha_id
            - meta
            - components
            - get_base
            - set_base
            - get_layers
            - get_layer
            - set_layer
            - update_metadata
            - get_span_info

## OpenPechaFS

::: openpecha.core.pecha.OpenPechaFS
    options:
        members:
            - opf_path
            - pecha_path
            - base_path
            - layers_path
            - meta_fn
            - index_fn
            - read_base_fil
            - read_layers_file
            - read_meta_file
            - save_meta
            - save_single_base
            - save_base
            - save_layer
            - save_index
            - save
            - update_base
            - reset_layer
            - reset_layers
            - publish
            - remove
