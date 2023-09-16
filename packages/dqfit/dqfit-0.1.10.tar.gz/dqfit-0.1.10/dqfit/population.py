import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from time import time

import pandas as pd

import dqfit as dq

def process_bundle(bundle_path: str, model: str, context_key: str) -> None:
    model = dq.Index.create(model=model, context=context_key)
    fhir_resources = dq.read_bundle_resources(bundle_path)
    if len(fhir_resources) == 0:
         raise ValueError(
            f"No FHIR resources found at {bundle_path}"
        )
    model.fit(fhir_resources)
    return model.population_level


def build_patient_level_result(model: str, context_key: str, bundle_paths: list):
    """A population of 1 bundle is processed in parallel"""
    main_func = partial(process_bundle, model=model, context_key=context_key)
    with ProcessPoolExecutor(max_workers=dq.MAX_CONCURRENCY) as exec:
        futures = exec.map(main_func, bundle_paths)
    patient_level = pd.concat(list(futures))
    return patient_level


def main() -> dq.Index:
    bundle_paths = dq.get_bundle_paths(population_key=args.population_key)
    if len(bundle_paths) == 0:
        raise ValueError(
            f"No FHIR bundles found at {dq.fhir_base}/{args.population_key}"
        )

    print(f"Model: {args.model_key}")
    print(f"Context: {args.context_key}")
    print(f"n: {len(bundle_paths)}")

    model = dq.Index.create(model=args.model_key, context=args.context_key)
    model.patient_level = build_patient_level_result(
        model=args.model_key, context_key=args.context_key, bundle_paths=bundle_paths
    )
    model.population_level = model.to_population_level()
    model.population_level.insert(0, 'DataQualityIndex', model.index)
    return model


def save_model_result(model: dq.Index) -> None:
    paths = dict(
        patient_level=f"{args.output}/patient_level.parquet",
        population_level=f"{args.output}/population_level.parquet",
        result_html=f"{args.output}/result.html",
        index=f"{args.output}/index.json",
    )

    model.patient_level.to_parquet(paths["patient_level"])
    model.population_level.to_parquet(paths["population_level"])
    model.visualize().write_html(paths["result_html"])

    with open(paths["index"], "w") as f:
        json.dump(
            {
                "index": model.index,
                "population": args.population_key,
                "context": args.context_key,
                "model": args.model_key,
                "created": int(start),
            },
            f,
        )

    print("\nResults available at:")
    for k, v in paths.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    start = time()

    parser = argparse.ArgumentParser(description="Data Quality Index")
    parser.add_argument("population_key", help="Key to identify the population")
    parser.add_argument("model_key", help="Key to identify the model")
    parser.add_argument("context_key", help="Key to identify the context")
    parser.add_argument("--output", help="Directory to save model results")

    args = parser.parse_args()
    model = main()

    print(f"\nData Quality Index: {model.index}\n")
    # print(f"\nPatient Count: {model.patient_count}")
    # print(f"\Resource Count: {model.resource_count}")
    print(model.population_level)

    if args.output:
        save_model_result(model)

    print(f"\nRuntime: {int(time()-start)} seconds")
