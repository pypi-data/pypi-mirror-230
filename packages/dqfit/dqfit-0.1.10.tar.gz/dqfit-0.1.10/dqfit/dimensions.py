from abc import ABC, abstractmethod
from typing import Any, List

import pandas as pd

from dqfit import helpers, io, constants


class ModelDimension(ABC):
    def __name__(self) -> str:
        return self.__name__
    
    @staticmethod
    def population_level_agg_fn():
        # enable override, as introduced by Longitudinal
        return ModelDimension.agg_fn()
    
    @staticmethod
    def agg_fn():
        return "mean"

    @staticmethod
    @abstractmethod
    def fit(path_level: pd.DataFrame, self):
        pass


class Conformant(ModelDimension):
    @staticmethod
    def agg_fn():
        return "mean"
    
    @staticmethod
    def population_level_agg_fn():
        return "mean"

    @staticmethod
    def fit(path_level: pd.DataFrame, context: dict) -> pd.DataFrame:
        # """Takes in path_level, returns path_level with Conformant vector"""
        context_paths = list(
            pd.DataFrame(context["dim"])["path"]
        )  # just make this np array
        path_level["Conformant"] = path_level["path"].isin(context_paths).astype(float)
        return path_level


class Complete(ModelDimension):

    def defintion():
        return "present (1) or absent (0) without regard to values"

    @staticmethod
    def population_level_agg_fn():
        return "mean"
    
    @staticmethod
    def agg_fn():
        return "mean"

    @staticmethod
    def fit(path_level: pd.DataFrame, context: dict) -> pd.DataFrame:
        """Score Conformant paths for Completeness"""

        def _score_dim(dim: pd.Series) -> int:
            # this could use a rethink
            """
            Effective nulls
            """
            value = dim["value"]
            if dim["Conformant"] == 0:
                return None
            elif type(value) == list and len(value) > 0:
                return 1
            elif pd.isna(value):
                return 0
            elif value == {}:
                return 0
            elif value in ["UNK", "unk", "", "unknown"]:
                return 0
            elif len(str(value)) > 0:  # primary case?
                return 1
            else:
                return 0

        path_level["Complete"] = path_level.query("Conformant == 1").apply(
            _score_dim, axis=1
        ).astype(float) # rest are floats
        return path_level


class Plausible(ModelDimension):

    """
    Plausible is a bit more complicated and where I could use the most help

    Idea: I could imagine plausibility models being a fn(research_journal)

    """

    @staticmethod
    def population_level_agg_fn():
        return "mean"

    @staticmethod
    def agg_fn():
        return "mean"

    MIN_DATE = "1903-01-01"
    TODAY_ISO = str(pd.to_datetime("today"))[0:10]

    ##
    DATETIME_PATHS = [
        "Procedure.performed[x]",
        "Condition.onset[x]",
        "Condition.abatement[x]",
        "Condition.recordedDate",
        "Patient.birthDate",
        "Observation.effective[x]",
        "MedicationDispense.whenHandedOver",
    ]

    DISCRETE_SETS = {
        "Procedure.status": [
            "preparation",
            "in-progress",
            "not-done",
            "on-hold",
            "stopped",
            "completed",
            "entered-in-error",
            "unknown",
        ],
        "Observation.status": [
            "registered",
            "preliminary",
            "final",
            "amended",
            "corrected",
            "cancelled",
            "entered-in-error",
            "unknown",
        ],
        "Patient.gender": ["male", "female", "other", "unknown"],
    }

    

    UCUM = set(io.load_reference("ucum")['units'])

    def period_score(period: dict):
        # DRAFT
        score = 0
        if len(period.keys()) == 1:
            score += Plausible.dt_score(period.get("start"))
        else:
            if "start" in period.keys():
                score += Plausible.dt_score(period["start"]) / 2
            if "end" in period.keys():
                yr = int(period["end"][0:4])
                if yr <= 2024:
                    score += 0.5
        return score

    def dt_score(dt: str) -> int:
        if pd.isna(dt):
            return 0
        date = dt[0:10]
        if Plausible.MIN_DATE < date <= Plausible.TODAY_ISO:
            return 1
        else:
            return 0

    def discrete_score(fhir_path: str, value: Any) -> int:
        "For in range"
        # this could use a better name
        if value in Plausible.DISCRETE_SETS[fhir_path]:
            return 1
        else:
            return 0

    def codeable_concept_score(codeable_concept, context: dict):
        # sample object
        # {
        #     "coding": [{"system": "http://loinc.org", "code": "4548-4"}]
        # }
        
        score = 0
        if "coding" not in codeable_concept.keys():
            return score
        
        for coding in codeable_concept.get("coding", []):
            if coding["system"] in constants.SYSTEMS:
                score += .25

            if coding["code"] in context["code"]:
                score += 0.75

                
        return min(score, 1)

    def observation_value_score(value):
        # WIP
        score = 0
        if isinstance(value, dict):
            if value.get("system") == 'http://unitsofmeasure.org':
                score += .25
            if value.get("code") in Plausible.UCUM:
                # NB: proper usage places the UCUM unit in the 'code' field
                score += .25

            if value.get("unit") in Plausible.UCUM:
                # however the availability of th unit field in valueQuantity
                # leads folks to this usage
                score += .1
            
            if value.get("value"):
                pass

        return min(score, 1)

    def type_score(type: dict):
        #
        if "coding" in type.keys():
            return 1
        else:
            return 0

    def subject_score(subject: dict, patient_ids: List[str]):
        # print(subject)
        score = 0
        patient_id = (
            subject.get("reference").replace("Patient/", "").replace("urn:uuid:", "")
        )
        if type(subject) != dict:
            return 0
        elif patient_id in patient_ids:
            # referential integrity check
            score += 1
        return score

    def clinical_status_score(clinical_status: dict):
       
        score = 0
        if "coding" not in clinical_status.keys():
            return score
        for coding in clinical_status.get("coding", []):
            if coding["code"] in constants.VALID_CLINICAL_STATUS_CODES:
                score += 1
        return score

    def coverage_type_score(clinical_status: dict):
        
        score = 0
        if "coding" not in clinical_status.keys():
            return score
        for coding in clinical_status.get("coding", []):
            if coding["code"] in constants.VALID_COVERAGE_TYPE_CODES:
                score += 1
        return score
    
    def meta_score(value: dict) -> float:
        score = 0
        if isinstance(value, dict):
            if 'lastUpdated' in value.keys():
                score += 0.1
            if 'source' in value.keys():
                score += 0.5
        return score

    @staticmethod
    def fit(path_level: pd.DataFrame, context: dict) -> pd.DataFrame:
        """Score Conformant paths for Plausibility"""
        patient_ids = path_level["patient_id"].unique()

        def _score_dim(dim: pd.Series):
            try:
                key = dim["path"]
                value = dim["value"]
                if dim["Complete"] in [None, 0]:
                    return 0
                elif key in Plausible.DATETIME_PATHS:
                    if type(value) == str:
                        return Plausible.dt_score(value)
                    elif type(value) == dict:
                        return Plausible.period_score(value)
                elif key == "patient_id":
                    return 1  # todo handle
                elif key.endswith(".clinicalStatus"):
                    return Plausible.clinical_status_score(value)
                elif key in Plausible.DISCRETE_SETS.keys():
                    return Plausible.discrete_score(key, value)
                elif key.endswith(".code"):
                    # todo handle medicationCodeableConcept
                    return Plausible.codeable_concept_score(value, context)
                elif key.endswith(".subject"):
                    return Plausible.subject_score(subject=value, patient_ids=patient_ids)
                elif key.endswith(".period"):
                    return Plausible.period_score(value)
                elif key == "Coverage.type":
                    return Plausible.coverage_type_score(value)
                elif key == "Observation.value[x]":
                    return Plausible.observation_value_score(value)
                elif key.endswith(".meta"):
                    return Plausible.meta_score(value)
                else:
                    return 0
            except Exception as e:
                # hmm how to handle nothings
                # print(dim, e)
                # print(path_level)
                return 0

        path_level = path_level.query("Conformant == 1").reset_index(drop=True) #.query("Complete == 1")
        path_level["Plausible"] = path_level.apply(
            _score_dim, axis=1
        ).fillna(0)
        return path_level


class Current(ModelDimension):

    # DRAFT

    def definition():
        return "0 to 1 measure where 0 is the min_date of the context and 1 is today"

    @staticmethod
    def population_level_agg_fn():
        return "mean"
    
    @staticmethod
    def agg_fn():
        return "max"

    @staticmethod
    def fit(path_level: pd.DataFrame, context: dict) -> pd.DataFrame:
        path_level["Date"] = path_level.apply(helpers.get_date, axis=1)
        time_horizon = helpers.time_horizon_matrix(
            min_date=context["min_date"], key="Current"
        )
        path_level = path_level.merge(time_horizon, on="Date", how="left")
        path_level["Current"] = path_level["Current"].fillna(0)
        path_level['Date'] = path_level['Date'].astype(str)
        return path_level


class Longitudinal(ModelDimension):

    """Measure of the Longitudinal Range"""

    @staticmethod
    def population_level_agg_fn():
        return "mean"
    
    @staticmethod
    def agg_fn():
        return lambda x: x.max() - x.min()

    @staticmethod
    def fit(path_level: pd.DataFrame, context: dict) -> pd.DataFrame:
        # hm rerun get_date or depend on Current
        path_level["Date"] = path_level.apply(helpers.get_date, axis=1)
        time_horizon = helpers.time_horizon_matrix(
            min_date=context["min_date"], key="Longitudinal"
        )
        path_level = path_level.merge(time_horizon, on="Date", how="left")
        return path_level
