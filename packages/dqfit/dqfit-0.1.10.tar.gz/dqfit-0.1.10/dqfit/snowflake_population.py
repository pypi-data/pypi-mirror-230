import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from time import time

import pandas as pd

import dqfit as dq

FHIR_BASE = "/Users/ah24562/data/snowflake"
RESULT_BASE = "/Users/ah24562/data/result"


def unpack_fhir_resource(row) -> list:
    resource_types = [
            "CLAIM",
            "COVERAGE",
            "CONDITION",
            "OBSERVATION",
            "PROCEDURE",
            "ENCOUNTER",
        ]

    fhir_resources = [eval(row['PATIENT'])]
    for resource_type in resource_types:
        if isinstance(row.get(resource_type), str):
            fhir_resources.extend(json.loads(row[resource_type]))
    return fhir_resources

def process_member(row: dict, model: str, context_key: str) -> None:
    model = dq.Index.create(model=model, context=context_key)
    fhir_resources = unpack_fhir_resource(row)
    if len(fhir_resources) == 0:
        raise ValueError(f"No FHIR resources found")
    model.fit(fhir_resources)
    return model.patient_level


def build_patient_level_result(model: str, context_key: str, member_fhir: pd.DataFrame):
    """A population of 1 bundle is processed in parallel"""
    main_func = partial(process_member, model=model, context_key=context_key)
    with ProcessPoolExecutor(max_workers=dq.MAX_CONCURRENCY) as exec:
        futures = exec.map(main_func, member_fhir.to_dict(orient="records")[0:5])
    patient_level = pd.concat(list(futures))
    return patient_level



def main() -> dq.Index:
    

    member_fhir = pd.read_csv(f"{FHIR_BASE}/{args.population_key}.csv.zip").dropna(how="all", axis=1)
    
    if len(member_fhir) == 0:
        raise ValueError(
            f"No FHIR bundles found at {dq.fhir_base}/{args.population_key}"
        )

    print(f"population: {args.population_key}")
    print(f"model: {args.model_key}")
    print(f"context: {args.context_key}")
    print(f"n_patients: {len(member_fhir)}")

    model = dq.Index.create(model=args.model_key, context=args.context_key)

    model.patient_level = build_patient_level_result(
        model=args.model_key, context_key=args.context_key, member_fhir=member_fhir
    )
    model.population_level = model.to_population_level()
    model.population_level.insert(0, 'population', args.population_key)
    model.population_level.insert(0, args.model_key, model.index)
    
    return model


def save_model_result(model: dq.Index) -> None:
    model_key = f"{args.model_key}-{model.index}.{args.population_key}-{args.context_key}"
    
    if args.output:
        out_base = f"{RESULT_BASE}/{args.output}"
        if not os.path.exists(out_base):
            os.makedirs(out_base)
        parquet_path=f"{out_base}/{model_key}.parquet"
        model.population_level.to_parquet(parquet_path)
        print(f"\nResults saved to {parquet_path}\n")
    


if __name__ == "__main__":
    start = time()

    parser = argparse.ArgumentParser(description="Data Quality Index")
    parser.add_argument("population_key", help="Key to identify the population")
    parser.add_argument("model_key", help="Key to identify the model")
    parser.add_argument("context_key", help="Key to identify the context")
    parser.add_argument("--output", help="Directory to save model result .parquet")
    parser.add_argument("--json", help="json output")
    parser.add_argument("--html", help="html output")

    args = parser.parse_args()
    model = main()

    print(f"m_parameters: {model.m:_}")
    print(f"\nData Quality Index: {model.index}\n")
    print(model.population_level)

    if args.output:
        save_model_result(model)

    print(f"\nRuntime: {int(time()-start)} seconds")


# def save_model_result(model: dq.Index) -> None:
#     paths = dict(
#         # patient_level=f"{args.output}/patient_level-{args.population_key}.parquet",
#         population_level=f"{args.output}/{model.index}-{args.population_key}-{args.context_key}.parquet",
#         # result_html=f"{args.output}/result.html",
#         # index=f"{args.output}/index.json",
#     )

#     # model.patient_level.to_parquet(paths["patient_level"])
#     model.population_level.to_parquet(paths["population_level"])
#     # model.visualize().write_html(paths["result_html"])

#     # with open(paths["index"], "w") as f:
#     #     json.dump(
#     #         {
#     #             "index": model.index,
#     #             "population": args.population_key,
#     #             "context": args.context_key,
#     #             "model": args.model_key,
#     #             "shape": model.shape,
#     #             "created": int(start),
#     #         },
#     #         f,
#     #     )

#     print("\nResults available at:")
#     for k, v in paths.items():
#         print(f"{k}: {v}")




    # if args.json:
    #     def to_json(model):
    #         with open(JSON_OUT, "w") as f:
    #             json.dump(
    #                 {
    #                     "index": model.index,
    #                     "population": args.population_key,
    #                     "context": args.context_key,
    #                     "model": args.model_key,
    #                     "shape": model.shape,
    #                     "created": int(start),
    #                 },
    #                 f,
    #             )

    #     to_json(model)
    #     JSON_OUT = f"{args.json}/{model.index}-{args.population_key}-{args.context_key}.parquet"
    #     if not os.path.exists(args.json):
    #         os.makedirs(args.json)
    #     model.population_level.to_parquet(JSON_OUT)

    
    # if args.html:
    #     HTML_OUT = f"{args.html}/{model.index}-{args.population_key}-{args.context_key}.html"
    #     if not os.path.exists(args.html):
    #         os.makedirs(args.html)
    #     model.visualize().write_html(HTML_OUT)
    
    # model.visualize().write_html(paths["result_html"])
    # print("\nResults available at:")
    # for k, v in paths.items():
    #     print(f"{k}: {v}")