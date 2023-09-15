# django-mptt-simple-listfilters

Provides simple filters based on django-mptt's TreeRelatedFieldListFilter, e.g. ListFilterIgnoreLeafNodes and ListFilterLimitDepth.

## Install

```shell
pip install django-mptt-simple-listfilters
```

## Provide List Filters

- ListFilterIgnoreLeafNodes

    Ignore all leaf nodes.

- ListFilterLimitDepth

    Only show roots in the filter list. You can create your own filter inherit from ListFilterLimitDepth and reset the max_depth value.

- ListFilterLimitDepth2
- ListFilterLimitDepth3
- ListFilterLimitDepth4

    These are shortcuts for ListFilterLimitDepth, and reset the max_depth value to 2, 3 and 4.

## Usage

Use as TreeRelatedFieldListFilter.

## Releases

### v0.1.1

- First release.

### v0.1.2

- Doc update.
