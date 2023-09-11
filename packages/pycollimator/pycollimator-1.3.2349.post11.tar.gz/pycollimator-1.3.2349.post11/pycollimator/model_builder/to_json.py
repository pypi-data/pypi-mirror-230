#!/usr/bin/env python3

from collections import defaultdict
import uuid
import numpy as np


def _np_tojson(v: np.ndarray):
    return "np." + repr(v)


def _autolayout(model, ids_to_uiprops):
    uiprops = ids_to_uiprops or {}

    h_spacing = 100
    v_spacing = 100

    def _process_node(node, x, y):
        if node.id not in uiprops:
            uiprops[node.id] = {
                "x": x,
                "y": y,
                "show_port_name_labels": node.typename == "core.ReferenceSubmodel",
            }

        # layout all incoming nodes
        n_input = len(node.input_names)
        start_y = y - (n_input - 1) * v_spacing / 2
        for i in range(n_input):
            inport = node.input_port(i)

            if inport not in model.links:
                continue

            in_node = model.links[inport].dst.node
            if in_node.id in uiprops:
                continue
            uiprops[in_node.id] = {
                "x": x - h_spacing,
                "y": start_y + i * v_spacing,
            }

    x, y = 0, 0
    for node in model.nodes.values():
        if node.id in uiprops:
            continue
        _process_node(node, x, y)
        x += 100

    for link in model.links.values():
        if link.id not in uiprops:
            uiprops[link.id] = {
                "link_type": {"connection_method": "direct_to_block"},
                "segments": [],
            }

    return uiprops


def _handle_reference_submodel_node(submodel_reference_uuid, node, node_json):
    """Additional handling for ReferenceSubmodel nodes"""
    node_json["submodel_reference_uuid"] = submodel_reference_uuid
    node_json["parameters"].update({k: {"order": i, "value": v} for i, (k, v) in enumerate(node.params.items())})


def _render_diagram(model, ids_to_uuids, uiprops):
    uiprops = _autolayout(model, uiprops)

    nodes = []
    for node in model.nodes.values():
        nodes.append(_render_node(node, ids_to_uuids[node.id], uiprops[node.id]))
        if node.typename == "core.ReferenceSubmodel":
            _handle_reference_submodel_node(ids_to_uuids[model.submodels[node].id], node, nodes[-1])

    return {
        "nodes": nodes,
        "links": [_render_link(lk, ids_to_uuids, uiprops[lk.id]) for lk in model.links.values()],
        "annotations": [],
    }


def _render_model(model, reference_submodels, groups, ids_to_uuids, uiprops=None, is_submodel=False):
    if is_submodel:
        groups = {"diagrams": {}, "references": {}}

    for node, group in model.groups.items():
        group_json = _render_model(
            group,
            reference_submodels,
            groups,
            ids_to_uuids,
            uiprops=uiprops,
            is_submodel=False,
        )
        groups["diagrams"][ids_to_uuids[group.id]] = group_json["diagram"]
        groups["references"][ids_to_uuids[node.id]] = {"diagram_uuid": ids_to_uuids[group.id]}

    parameters = None
    if is_submodel:
        parameters = [
            {
                "name": k,
                "default_value": v.default_value,
                "description": v.description,
                "uuid": ids_to_uuids[v.id],
                "uiprops": uiprops.get(v.id, {}),
            }
            for k, v in model.parameters.items()
        ]
    else:
        parameters = {k: {"value": v.value} for k, v in model.parameters.items()}

    reference_submodels.update(
        {
            ids_to_uuids[submodel.id]: _render_model(
                submodel,
                reference_submodels,
                groups,
                ids_to_uuids,
                uiprops=uiprops,
                is_submodel=True,
            )
            for submodel in model.submodels.values()
        }
    )

    return {
        "name": model.name,
        "uuid": ids_to_uuids[model.id],
        "diagram": _render_diagram(model, ids_to_uuids, uiprops),
        "submodels": groups if is_submodel else None,
        "parameters": parameters,
        "configuration": model.configuration or {} if not is_submodel else None,
    }


def render_model(model, ids_to_uuids=None, uiprops=None, is_submodel=False):
    _ids_to_uuids = defaultdict(lambda: str(uuid.uuid4()))

    if ids_to_uuids is not None:
        for k, v in ids_to_uuids.items():
            _ids_to_uuids[k] = v

    reference_submodels = {}
    groups = {"diagrams": {}, "references": {}}
    model_dict = _render_model(
        model,
        reference_submodels,
        groups,
        ids_to_uuids=_ids_to_uuids,
        uiprops=uiprops,
        is_submodel=is_submodel,
    )
    model_dict["reference_submodels"] = reference_submodels
    model_dict["submodels"] = groups
    return model_dict


def _render_node(node, uuid, uiprops):
    parameters = {}
    for k, v in node.params.items():
        if k not in node.schema.parameter_definitions and not node.schema._get("base", "extra_parameters"):
            continue
        if k not in node.schema.parameter_definitions:
            raise ValueError(f"Parameter {k} not found in schema for node {node.name}")
        if node.schema.parameter_definitions[k].get("data_type", "any") == "string":
            parameters[k] = {"value": str(v), "is_string": True}
        elif isinstance(v, np.ndarray):
            value = _np_tojson(v)
            parameters[k] = {"value": value}
        else:
            parameters[k] = {"value": str(v)}

    # Note: we don't include the ports kind, it's not useful
    return {
        "name": node.name,
        "uuid": uuid,
        "type": node.typename,
        "inputs": [{"name": name} for name in node.input_names],
        "outputs": [{"name": name} for name in node.output_names],
        "parameters": parameters,
        "time_mode": node.time_mode,
        "uiprops": uiprops,
    }


def _render_link(link, ids_to_uuids, uiprops):
    src, dst = link.src, link.dst
    return {
        "uuid": ids_to_uuids[link.id],
        # "name": f"{src.node.name}.{src.name} -> {dst.node.name}.{dst.name}",
        "src": {
            "node": ids_to_uuids[src.node.id],
            "port": src.index,
            # "node_name": src.node.name,
            # "port_name": src.name,
        },
        "dst": {
            "node": ids_to_uuids[dst.node.id],
            "port": dst.index,
            # "node_name": dst.node.name,
            # "port_name": dst.name,
        },
        "uiprops": uiprops,
    }
