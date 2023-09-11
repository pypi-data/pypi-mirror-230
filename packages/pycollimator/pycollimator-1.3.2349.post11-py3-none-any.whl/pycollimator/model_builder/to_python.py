from .core import ReferenceSubmodel, Group, Submodel


def _normalize_name(name):
    return name.strip().replace(" ", "_").replace("-", "_")


def to_python_str(
    model_builder,
    builder_name: str = None,
    output_submodels: bool = True,
    output_groups: bool = True,
    omit_model_builder: bool = False,
):
    lines, submodels_func_def = _to_python_str(
        model_builder,
        builder_name=builder_name,
        output_submodels=output_submodels,
        output_groups=output_groups,
        omit_model_builder=omit_model_builder,
    )

    create_submodels = [
        f"{submodel_name}_builder = make_{_normalize_name(submodel_name)}_builder()"
        for submodel_name, _ in submodels_func_def.items()
    ]

    if output_submodels:
        submodels_func_def = [
            line for lines in submodels_func_def.values() for line in lines
        ]
        lines = submodels_func_def + create_submodels + lines

    return "\n".join(lines)


def _create_node(model_builder, node, builder_name, lines, omit_model_builder):
    node_params = [f'id="{node.id}"']
    for pname, pvalue in node.params.items():
        if type(pvalue) is str:
            value = pvalue.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
            node_params.append(f'{pname}="{value}"')
        else:
            node_params.append(f"{pname}={pvalue}")
    func_params = [f'name="{node.name}"']

    if not model_builder.has_link(node) and not omit_model_builder:
        func_params = [f"model_builder={builder_name}"] + func_params

    params = func_params + node_params

    if node.has_dynamic_input_ports:
        inames = [f'"{iname}"' for iname in node.input_names]
        inames = ", ".join(inames)
        if len(inames) > 0:
            params.append(f"input_names=({inames},)")
        else:
            params.append("input_names=()")
    if node.has_dynamic_output_ports:
        onames = [f'"{oname}"' for oname in node.output_names]
        onames = ", ".join(onames)
        if len(onames) > 0:
            params.append(f"output_names=({onames},)")
        else:
            params.append("output_names=()")

    if (
        node.schema._get("modes", "time") != node.time_mode
        and node.time_mode is not None
    ):
        params.append(f'time_mode="{node.time_mode}"')

    params_str = ", ".join(params)

    add_group = "add_group"
    add_reference_submodel = "add_reference_submodel"
    if not omit_model_builder:
        add_group = f"{builder_name}.{add_group}"
        add_reference_submodel = f"{builder_name}.{add_reference_submodel}"

    if type(node) is ReferenceSubmodel:
        submodel_name = model_builder.submodels[node].name
        lines.append(
            f'{node.name} = {add_reference_submodel}("{node.name}", {submodel_name}_builder)'
        )
    elif type(node) is Group or type(node) is Submodel:
        lines.append(f'{node.name} = {add_group}("{node.name}", {node.name}_builder)')
    else:
        lines.append(f"{node.name} = core.{node.__class__.__name__}({params_str})")

    if not model_builder.has_link(node) and omit_model_builder:
        lines.append(f"add_block({node.name})")


def _to_python_str(
    model_builder,
    model_name=None,
    builder_name=None,
    output_submodels: bool = True,
    output_groups: bool = True,
    omit_model_builder: bool = False,
):
    lines = []
    submodels_func_def = {}

    if model_name is None:
        model_name = _normalize_name(model_builder.name)

    if builder_name is None:
        # Append _builder to avoid name conflict with node name
        builder_name = f"{_normalize_name(model_name)}_builder"

    add_parameter = "add_parameter"
    add_link = "add_link"
    if not omit_model_builder:
        add_parameter = f"{builder_name}.{add_parameter}"
        add_link = f"{builder_name}.{add_link}"

    if not omit_model_builder:
        lines.append(
            f'{builder_name} = ModelBuilder("{model_builder.name}", id="{model_builder.id}")'
        )

    # Parameters
    for k, v in model_builder.parameters.items():
        if v.default_value is not None:
            lines.append(
                f'{add_parameter}("{k}", "{v.value}", '
                f'default_value="{v.default_value}", description="{v.description}")'
            )
        else:
            lines.append(f'{add_parameter}("{k}", "{v.value}")')

    lines.append("")

    # Groups
    groups = set()
    if output_groups:
        for node, group in model_builder.groups.items():
            lines.append(f"def make_{_normalize_name(node.name)}_builder():")
            group_code, other_submodels = _to_python_str(group, model_name=node.name)
            submodels_func_def.update(other_submodels)
            group_code += [f"return {node.name}_builder", ""]
            lines.extend(["    " + line for line in group_code])
            groups.add(node.id)
            lines.append(
                f"{node.name}_builder = make_{_normalize_name(node.name)}_builder()"
            )

    # Submodels
    if output_submodels:
        for node, submodel in model_builder.submodels.items():
            submodel_code, other_submodels = _to_python_str(
                submodel, model_name=submodel.name
            )
            submodel_code = "\n".join("    " + line for line in submodel_code)
            submodel_name = _normalize_name(submodel.name)
            submodel_def_str = [
                f"def make_{_normalize_name(submodel_name)}_builder():",
                submodel_code,
                f"    return {submodel_name}_builder",
                "",
            ]

            submodels_func_def.update(other_submodels)
            submodels_func_def[submodel.name] = submodel_def_str

    # Create nodes
    for node in model_builder.nodes.values():
        _create_node(model_builder, node, builder_name, lines, omit_model_builder)

    lines.append("")

    # Connect nodes
    for link in model_builder.links.values():
        src = f"{link.src.node.name}.{link.src.name}"
        dst = f"{link.dst.node.name}.{link.dst.name}"
        lines.append(f'{add_link}({src}, {dst}, id="{link.id}")')

    return lines, submodels_func_def
