from pathlib import Path
import yaml
from collections import OrderedDict

class OrderedDumper(yaml.SafeDumper):
    pass

def dict_representer(dumper, data):
    return dumper.represent_dict(data.items())

OrderedDumper.add_representer(OrderedDict, dict_representer)

def combine_swagger_docs():
    base_dir = Path(__file__).resolve().parent.parent / "static"
    combined = OrderedDict()

    # Load main swagger.yaml
    with open(base_dir / "swagger.yaml", "r", encoding="utf-8") as f:
        combined = yaml.safe_load(f)
        combined = OrderedDict(combined)

    # Load schemas2.yaml
    with open(base_dir / "schemas.yaml", "r", encoding="utf-8") as f:
        schemas = yaml.safe_load(f)
        if "definitions" in schemas:
            combined.setdefault("definitions", OrderedDict()).update(schemas["definitions"])

    # Load update_schemas.yaml
    update_schema_path = base_dir / "update_schemas.yaml"
    if update_schema_path.exists():
        with open(update_schema_path, "r", encoding="utf-8") as f:
            update_schemas = yaml.safe_load(f)
            if "definitions" in update_schemas:
                combined.setdefault("definitions", OrderedDict()).update(update_schemas["definitions"])

    # Load all paths from paths directory
    paths_dir = base_dir / "paths"
    combined.setdefault("paths", OrderedDict())
    for path_file in sorted(paths_dir.glob("*.yaml")):
        with open(path_file, "r", encoding="utf-8") as f:
            path_content = yaml.safe_load(f)
            combined["paths"].update(path_content)

    # Load and inject examples
    examples_dir = base_dir / "examples"
    for example_file in sorted(examples_dir.glob("*.yaml")):
        with open(example_file, "r", encoding="utf-8") as f:
            example_data = yaml.safe_load(f)
            for path_key, methods in example_data.items():
                for method_key, method_content in methods.items():
                    if path_key in combined["paths"] and method_key in combined["paths"][path_key]:
                        if "value" in method_content:
                            example_body = method_content["value"]
                            combined["paths"][path_key][method_key].setdefault("examples", {}).update({
                                "application/json": example_body.get("request", {})
                            })

    # Write combined Swagger YAML with ordered keys
    output_path = base_dir / "combined_swagger.yaml"
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(combined, f, Dumper=OrderedDumper, sort_keys=False, allow_unicode=True)

    print(f"Combined Swagger file saved to: {output_path}")

if __name__ == "__main__":
    combine_swagger_docs()
