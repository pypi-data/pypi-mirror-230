#!env python3

import collections

from . import core
from .model import ModelBuilder


def _parse_parameters(parameters, model_builder):
    if type(parameters) is list:
        for param in parameters:
            model_builder.add_parameter(param["name"], param["value"])
    elif type(parameters) is dict:
        for key, val in parameters.items():
            model_builder.add_parameter(key, val["value"])


def _parse_parameter_definitions(parameters, model_builder, uuids_to_ids, ids_to_uiprops):
    if type(parameters) is list:
        for param in parameters:
            p = model_builder.add_parameter(
                param["name"],
                param["default_value"],
                default_value=param["default_value"],
                description=param.get("description", ""),
            )
            uuids_to_ids[param["uuid"]] = p.id
            ids_to_uiprops[p.id] = param["uiprops"]
    elif type(parameters) is dict:
        for key, val in parameters.items():
            p = model_builder.add_parameter(
                key,
                val["name"],
                val["default_value"],
                default_value=val["default_value"],
                description=val.get("description", ""),
            )
            uuids_to_ids[val["uuid"]] = p.id
            ids_to_uiprops[p.id] = val["uiprops"]


def parse_json(data):
    model_data = "model" in data and data["model"] or data

    uuids = {}
    uiprops = {}
    root_model_builder = ModelBuilder(model_data["name"])

    # pylint: disable=no-member
    uuids[root_model_builder.id] = model_data["uuid"]
    is_submodel = "kind" in model_data and model_data["kind"] == "Submodel"

    # TODO: add description of parameters too
    if is_submodel:
        _parse_parameter_definitions(model_data["parameter_definitions"], root_model_builder, uuids, uiprops)
    else:
        _parse_parameters(model_data["parameters"], root_model_builder)

    core_vars = vars(core)
    nodes = {}
    submodels = {}

    def _handle_group(model_builder, node, groups):
        diagram_uuid = groups["references"][node["uuid"]]["diagram_uuid"]
        group_builder = ModelBuilder(node["name"])
        parse_diagram(group_builder, groups["diagrams"][diagram_uuid], groups)
        return model_builder.add_group(node["name"], group_builder)

    def _handle_submodel(model_builder, node):
        submodel_uuid = node["submodel_reference_uuid"]

        if submodel_uuid not in submodels:
            if "reference_submodels" not in data:
                print("Reference submodels not found in the file, skipping...")
                return
            else:
                submodel_json = data["reference_submodels"][submodel_uuid]
                submodels[submodel_uuid] = ModelBuilder(submodel_json["name"])
                uuids[submodels[submodel_uuid].id] = submodel_json["uuid"]
                _parse_parameter_definitions(
                    submodel_json["parameters"],
                    submodels[submodel_uuid],
                    uuids,
                    uiprops,
                )
                parse_diagram(
                    submodels[submodel_uuid],
                    submodel_json["diagram"],
                    submodel_json["submodels"],
                )
        submodel = submodels[submodel_uuid]
        return model_builder.add_reference_submodel(node["name"], submodel)

    def parse_diagram(model_builder, diagram, groups):
        for node in diagram["nodes"]:
            params = {param_name: param_data["value"] for param_name, param_data in node["parameters"].items()}
            node_type = "".join(node["type"].split(".")[1:])

            params["input_names"] = tuple(i["name"] for i in node["inputs"])
            params["output_names"] = tuple(i["name"] for i in node["outputs"])
            params["time_mode"] = node.get("time_mode")

            if node_type not in core_vars:
                raise ValueError(f"Unknown node type: {node_type}")

            if node_type in ("Submodel", "Group"):
                node_obj = _handle_group(model_builder, node, groups)
            elif node_type == "ReferenceSubmodel":
                node_obj = _handle_submodel(model_builder, node)
            else:
                node_obj = core_vars[node_type](model_builder=model_builder, name=node["name"], **params)

            nodes[node["uuid"]] = node_obj
            uuids[node_obj.id] = node["uuid"]
            uiprops[node_obj.id] = node["uiprops"]

        node_inputs = collections.defaultdict(list)
        for link in diagram["links"]:
            if "src" not in link or "dst" not in link:
                continue
            src_node = nodes[link["src"]["node"]]
            src_port_id = link["src"]["port"]
            dst_node = nodes[link["dst"]["node"]]
            dst_port_id = link["dst"]["port"]
            node_inputs[dst_node].append((src_node, src_port_id))
            out_port = src_node.output_port(src_port_id)
            in_port = dst_node.input_port(dst_port_id)
            lk = model_builder.add_link(out_port, in_port)
            uuids[lk.id] = link["uuid"]
            uiprops[lk.id] = link["uiprops"]

    root_diagram = model_data["diagram"] if "diagram" in model_data else model_data["rootModel"]
    parse_diagram(root_model_builder, root_diagram, model_data["submodels"])
    return root_model_builder, uuids, uiprops
