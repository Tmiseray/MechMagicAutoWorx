from pathlib import Path
import yaml
from collections import OrderedDict

class OrderedDumper(yaml.SafeDumper):
    pass

def dict_representer(dumper, data):
    return dumper.represent_dict(data.items())

OrderedDumper.add_representer(OrderedDict, dict_representer)

def combine_openapi_docs():
    base_dir = Path(__file__).resolve().parent.parent / "static"
    combined = OrderedDict()

    # Load main openapi.yaml
    with open(base_dir / "openapi.yaml", "r", encoding="utf-8") as f:
        combined = yaml.safe_load(f)
        combined = OrderedDict(combined)

    # Prepare OpenAPI 3.0 structure
    combined.setdefault("components", OrderedDict())
    for section in ["schemas", "requestBodies", "responses", "examples", "securitySchemes"]:
        combined["components"].setdefault(section, OrderedDict())

    # Load and merge all index.yaml files from components/*
    components_dir = base_dir / "components"
    for section in combined["components"]:
        section_path = components_dir / section / "index.yaml"
        if section_path.exists():
            with open(section_path, "r", encoding="utf-8") as f:
                index_data = yaml.safe_load(f)
                if index_data and "components" in index_data and section in index_data["components"]:
                    combined["components"][section].update(index_data["components"][section])

    # SKIP outdated Swagger 2.0 paths
    combined["paths"] = OrderedDict()

    # Write combined OpenAPI 3.0 doc
    output_path = base_dir / "combined_docs.yaml"
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(combined, f, Dumper=OrderedDumper, sort_keys=False, allow_unicode=True)

    print(f"✅ OpenAPI 3.0 docs saved to: {output_path}")

if __name__ == "__main__":
    combine_openapi_docs()
