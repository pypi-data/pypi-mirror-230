from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd


def transform_to_fhir_path(fhir_resources: List[dict]) -> pd.DataFrame:
    def _get_fhir_paths(resource: dict) -> List[dict]:
        """
        Path is the atomic resource of a FHIR Resource
        defined in Implementation Guides
        Inspired by FHIRPath where applicable
        """

        def _get_patient_id(resource):
            # TODO Need to support:
            # Location
            # Practitioner
            # Organization
            # PractitionerRole
            # Provenance
            # Medication
            def _clean_id(id: str) -> str:
                # todo: research reference requirements
                # Synthea prefixing resources with urn:uuid:f11ade6b-fae3-c20d-0a46-e344db669410
                return id.replace("Patient/", "").replace("urn:uuid:", "")

            resourceType = resource["resourceType"]
            if resourceType == "Patient":
                return resource["id"]
            elif "subject" in resource.keys():
                return _clean_id(resource["subject"]["reference"])
            elif "patient" in resource.keys():
                return _clean_id(resource["patient"]["reference"])
            elif "beneficiary" in resource.keys():
                return _clean_id(resource["beneficiary"]["reference"])

        def _get_path_name(resource, k) -> str:
            resourceType = resource["resourceType"]
            k = k.replace("Period", "[x]")
            k = k.replace("DateTime", "[x]")
            k = k.replace("valueQuantity", "value[x]")
            k = k.replace("valueRange", "value[x]")
            k = k.replace("valueCodeableConcept", "value[x]")
            k = k.replace("valueString", "value[x]")
            return f"{resourceType}.{k}"

        resource_paths = []

        for k, v in resource.items():
            path_obj = {}
            path_obj["patient_id"] = _get_patient_id(resource)
            path_obj["id"] = resource["id"]
            path_obj["path"] = _get_path_name(resource, k)
            path_obj["value"] = v
            resource_paths.append(path_obj)
        return resource_paths

    fhir_path = []
    for resource in fhir_resources:
        fhir_path.extend(_get_fhir_paths(resource))
    fhir_path = pd.DataFrame(fhir_path)
    return fhir_path


# this really slowed process down :(
# @dataclass
# class FHIRPath:
#     """
#     FHIR Path is defined as ___:
#     1) _ref: Patient ID, the patient to which the resource belongs
#     2) id: Resource ID, the resource to which the path belongs
#     3) path: FHIR Path, the path name

#     """
#     patient_id: str
#     id: str
#     path: str
#     value: Any


        # dataclass really slowed process down :(
        # for k, v in resource.items():
        #     resource_paths.append(FHIRPath(
        #         patient_id=_get_patient_id(resource),
        #         id=resource['id'],
        #         path=_get_path_name(resource, k),
        #         value=v
        #     ))
