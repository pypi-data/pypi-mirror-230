# Hueprint

## Summary

Hueprint is a simple package that allows the usage of colour and text effects in Python console applications.

## Data Types

The package introduces two simple enums: `EColour` and `EEffect`.

## Functions

- `cprint`: allows using `EColour` and `EEffect` for easy text style customization.
- `sprint`: "success" style; green, no effect.
- `eprint`: "error" style; red, no effect.
- `wprint`: "warning" style; yellow, no effect.
- `nprint`: "notification" style; blue, no effect.
- `iprint`: a wrapper to the `pprint` function (from the `pprint` package).

## Example

`cprint` is the only function that differs from `print` in terms of number or arguments required, so this example will focus on that:

```python
    from hueprint import cprint
    from hueprint.types import EColour, EEffect

    text = "Hello, World!"
    colour = EColour.CYAN
    effect = EEffect.ITALIC

    cprint(text, colour, effect)  # This will print the specified text in cyan and italic.
```
