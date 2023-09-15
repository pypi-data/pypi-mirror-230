"""Add label YAML."""
from __future__ import annotations

from typing import Any

import flatdict
import pydantic

import gdsfactory as gf
from gdsfactory.name import clean_name
from gdsfactory.typings import LayerSpec

ignore = [
    "cross_section",
    "decorator",
    "cross_section1",
    "cross_section2",
    "contact",
    "pad",
]


@pydantic.validate_call
def add_label_yaml(
    component: gf.Component,
    position: tuple[float, float] = (0, 0),
    layer: LayerSpec = "LABEL",
    metadata_ignore: list[str] | None = ignore,
    metadata_include_parent: list[str] | None = None,
    metadata_include_child: list[str] | None = None,
    test: list[str] | None = None,
    test_settings: dict[str, Any] | None = None,
    analysis: str | None = None,
    analysis_settings: dict[str, Any] | None = None,
    doe: str | None = None,
) -> gf.Component:
    """Returns Component with measurement label.

    Args:
        component: to add labels to.
        position: label position.
        layer: text label layer.
        metadata_ignore: list of settings keys to ignore. Works with flatdict setting:subsetting.
        metadata_include_parent: parent metadata keys to include. Works with flatdict setting:subsetting.
        metadata_include_child: child metadata keys to include.
        test: test config name.
        test_settings: test settings.
        analysis: analysis name.
        analysis_settings: Extra analysis settings. Defaults to component settings.
        doe: Design of Experiment name.
    """
    from gdsfactory.pdk import get_layer

    metadata_ignore = metadata_ignore or []
    metadata_include_parent = metadata_include_parent or []
    metadata_include_child = metadata_include_child or []

    text = f"""component_name: {component.name}
doe: {doe}
test: {test}
analysis: {analysis}
wavelength: {component.metadata.get('wavelength')}
"""

    text += """analysis_settings:
"""
    info = []
    layer = get_layer(layer)

    # metadata = component.metadata_child.changed
    metadata = component.metadata_child.get("changed")
    if metadata:
        info += [
            f"  {k}: {v}"
            for k, v in metadata.items()
            if k not in metadata_ignore and isinstance(v, int | float | str)
        ]

    metadata = (
        flatdict.FlatDict(component.metadata.get("full"))
        if component.metadata.get("full")
        else {}
    )
    info += [
        f"  {clean_name(k)}: {metadata.get(k)}"
        for k in metadata_include_parent
        if metadata.get(k)
    ]

    metadata = (
        flatdict.FlatDict(component.metadata_child.get("full"))
        if component.metadata_child.get("full")
        else {}
    )
    info += [
        f"  {clean_name(k)}: {metadata.get(k)}"
        for k in metadata_include_child
        if metadata.get(k)
    ]

    info += ["ports:\n"]

    ports_info = []
    if component.ports:
        for port in component.get_ports_list():
            ports_info += []
            ports_info += [f"  {port.name}:"]
            s = f"    {port.to_yaml()}"
            s = s.split("\n")
            ports_info += ["    \n    ".join(s)]

    text += "\n".join(info)
    text += "\n".join(ports_info)

    label = gf.Label(
        text=text,
        origin=position,
        anchor="o",
        layer=layer[0],
        texttype=layer[1],
    )
    component.add(label)
    return component


if __name__ == "__main__":
    from omegaconf import OmegaConf

    c = gf.c.straight(length=11)
    c = gf.c.mmi2x2(length_mmi=2.2)
    c = gf.routing.add_fiber_array(
        c,
        get_input_labels_function=None,
        grating_coupler=gf.components.grating_coupler_te,
        decorator=add_label_yaml,
    )
    print(c.labels[0].text)
    d = OmegaConf.create(c.labels[0].text)
    c.show(show_ports=True)
