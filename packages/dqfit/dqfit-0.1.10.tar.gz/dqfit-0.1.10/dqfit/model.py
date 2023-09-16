import pandas as pd

import dqfit as dq


class DataQualityIndex:
    def __init__(self, context_key: str, dimensions: list) -> None:
        self.context = dq.load_context(context_key=context_key)
        self.dimensions = dimensions

    def fit(self, fhir_resources: list) -> pd.DataFrame:
        self.path_level = self.to_path_level(fhir_resources)
        self.patient_level = self.to_patient_level()
        self.population_level = self.to_population_level()
        self.population_level.insert(0, "DataQualityIndex", self.index)
        return self.population_level

    @property
    def index(self):
        max_score = self.population_level["weight"].sum() * len(self.dimensions)
        total_score = self.population_level["Score"].sum()
        return round(total_score / max_score * 100, 1)

    @property
    def patient_count(self):
        return self.patient_level['patient_id'].nunique()
    
    @property
    def resource_count(self):
        return self.path_level['id'].nunique()

    @property
    def shape(self):
        return (self.patient_count, self.resource_count, len(self.dimensions))

    @property
    def dimension_keys(self):
        return [dim.__name__ for dim in self.dimensions]

    def row_score(self, row: pd.Series):
        return (row[self.dimension_keys] * row["weight"]).sum()

    def to_path_level(self, fhir_resources: list) -> pd.DataFrame:
        """Returns dataframe of conformant fhir paths
        scored with with context and model dimensions"""
        path_level = dq.transform_to_fhir_path(fhir_resources)
        # THOUGHT: Conformant only returns 1s?
        for Dim in self.dimensions:
            path_level = Dim.fit(path_level, self.context)

        # this is a bit overloaded, as requires conformant
        path_level = path_level.query("Conformant == 1").reset_index(drop=True)
        path_level.insert(0, "context", self.context["key"])
        path_level = path_level.sort_values(self.dimension_keys).reset_index(drop=True)
        return path_level

    def to_patient_level(self) -> pd.DataFrame:
        """Takes in a Scored Path Level DataFrame and returns a Patient Level DataFrame based on the Aggregation Rules for each Dimension"""

        weighted_context_path = pd.DataFrame(self.context["dim"])
        weighted_context_path["weight"] = (
            weighted_context_path["weight"] / weighted_context_path["weight"].max()
        )  # normalize weights
        patient_ids = self.path_level[["patient_id"]].drop_duplicates()
        patient_level = patient_ids.merge(weighted_context_path, how="cross")

        frequencies = (
            self.path_level.groupby(["path", "patient_id"])
            .agg(
                patient_count=("patient_id", "nunique"),
                resource_count=("id", "nunique"),
            )
            .reset_index()
        )

        patient_level = patient_level.merge(frequencies, how="left").fillna(0)

        patient_path_dimensions = (
            self.path_level.groupby(["path", "patient_id"])
            .agg({dim.__name__: dim.agg_fn() for dim in self.dimensions})
            .reset_index()
            .fillna(0)
        )

        patient_level = patient_level.merge(patient_path_dimensions, how="left").fillna(
            0
        )

        patient_level = patient_level.fillna(0)
        # patient_level['Plausible'] = patient_level['Plausible'] / patient_level['Complete']
        # patient_level['Complete'] = patient_level['Complete'] / patient_level['Conformant']

        patient_level["Score"] = patient_level.apply(self.row_score, axis=1)
        patient_level.insert(0, "context", self.context["key"])
        patient_level = patient_level.sort_values(self.dimension_keys).reset_index(
            drop=True
        )
        return patient_level

    def to_population_level(self) -> pd.DataFrame:
        agg_fn = {
            **{"weight": "max", "patient_count": "sum", "resource_count": "sum"},
            **{dim.__name__: dim.population_level_agg_fn() for dim in self.dimensions},
        }
        population_level = self.patient_level.groupby("path").agg(agg_fn).reset_index()

        # DRAFT: only tested on DQI-3
        if "Plausible" in population_level.columns:
            population_level["Plausible"] = (
                population_level["Plausible"] / population_level["Complete"]
            )
        population_level["Complete"] = (
            population_level["Complete"] / population_level["Conformant"]
        )
        population_level = population_level.fillna(0)
        # Idea being only what a complete score, given conformant, etc

        population_level["Score"] = population_level.apply(self.row_score, axis=1)
        population_level.insert(0, "context", self.context["key"])
        # population_level = population_level.sort_values(
        #     self.dimension_keys
        # ).reset_index(drop=True)
        return (
            population_level.sort_values('path').reset_index(drop=True)
        )

    def visualize(self):
        return dq.draw_population_path_dimensions(self.population_level)


class Index:
    def create(model: str, context: str):
        ## emulating openai.Completion.create(model="") syntax
        if model == "dqi-2":
            return DataQualityIndex(
                context_key=context, dimensions=[dq.Conformant, dq.Complete]
            )
        elif model == "dqi-3":
            return DataQualityIndex(
                context_key=context,
                dimensions=[dq.Conformant, dq.Complete, dq.Plausible],
            )
        elif model == "dqi-4":
            return DataQualityIndex(
                context_key=context,
                dimensions=[dq.Conformant, dq.Complete, dq.Plausible, dq.Current],
            )
        elif model == "dqi-5":
            return DataQualityIndex(
                context_key=context,
                dimensions=[
                    dq.Conformant,
                    dq.Complete,
                    dq.Plausible,
                    dq.Current,
                    dq.Longitudinal,
                ],
            )
