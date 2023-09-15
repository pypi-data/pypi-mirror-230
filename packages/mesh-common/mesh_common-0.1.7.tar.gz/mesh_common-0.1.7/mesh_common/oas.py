from typing import Any, Callable, Optional, cast


def transform_oas_spec(
    openapi_schema: dict[str, Any],
    method_transformer: Optional[Callable[[dict[str, Any]], None]] = None,
    parameter_transformer: Optional[Callable[[dict[str, Any]], None]] = None,
) -> dict:
    """
        transform the openapi schema for compatibility with APIM rendering
    Args:
        openapi_schema: the starting schema from fastapi get_openapi
        method_transformer: function to further transform methods
        parameter_transformer: function to further transform parameters
    Returns:
        dict: transformed schema
    """

    schema_components = openapi_schema.get("components", {}).get("schemas", {})

    # apim schema rendering doesn't support referenced schemas,  so resolve to inline properties
    def _resolve_refs(item: dict, definitions: dict):
        if not item:
            return

        keys = list(item.keys())
        if keys == ["$ref"]:
            ref = item.pop("$ref")
            definition = definitions[ref.split("/")[-1]]
            item.update(definition)
            return

        for value in item.values():
            if not isinstance(value, dict):
                continue
            _resolve_refs(value, definitions)

    _resolve_refs(schema_components, schema_components)

    def _definitions_inline(schema: dict):
        components = {}
        components.update(schema_components)
        definitions = schema.pop("definitions", None)
        if definitions:
            components.update(definitions)

        _resolve_refs(schema, components)

    def _transform_method(method: dict[str, Any]) -> dict[str, Any]:

        parameters: list[dict] = method.get("parameters", [])

        if parameter_transformer:
            for parameter in parameters:
                parameter_transformer(parameter)

        if method_transformer:
            method_transformer(method)

        responses = method.get("responses", {})
        # reverse sort media types to get most recent first
        for response in responses.values():
            content = response.get("content", {})
            if not content:
                continue
            response["content"] = {key: response["content"][key] for key in reversed(sorted(content.keys()))}

            for media_type in response["content"].values():
                if not media_type.get("schema"):
                    continue

                _definitions_inline(media_type["schema"])

        return method

    def _transform_methods(oas_methods: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        route_methods = [
            (spec.pop("spec_order", 999), route_method, _transform_method(spec))
            for route_method, spec in oas_methods.items()
        ]
        route_methods.sort(key=lambda x: (x[0], x[1]))
        lowest_key = route_methods[0][0]
        return lowest_key, {route_method: spec for _, route_method, spec in route_methods}

    def _transform_routes(oas_paths: dict[str, dict[str, Any]]) -> dict[str, Any]:
        sortable_routes = [
            (ix, path_methods[0], _transform_methods(cast(dict[str, Any], path_methods[1])))
            for ix, path_methods in enumerate(oas_paths.items())
        ]
        sortable_routes.sort(key=lambda x: (x[2][0], x[0]))
        return {route: sorted_routes[1] for _, route, sorted_routes in sortable_routes}

    openapi_schema["paths"] = _transform_routes(openapi_schema["paths"])

    openapi_schema.pop("components", None)

    return openapi_schema
