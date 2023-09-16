SYSTEMS = set(
    [
        "http://loinc.org",
        "http://snomed.info/sct",
        "http://hl7.org/fhir/sid/icd-10",
        "http://www.nlm.nih.gov/research/umls/rxnorm",
        "http://www.ama-assn.org/go/cpt",
        "http://hl7.org/fhir/sid/ndc",
        "http://unitsofmeasure.org",
        "http://terminology.hl7.org/CodeSystem/v2-0203",
        "https://www.cms.gov/Medicare/Coding/HCPCSReleaseCodeSets"
    ]
)

VALID_COVERAGE_TYPE_CODES = set(
    [
        "pay",
        "EHCPOL",
        "HSAPOL",
        "AUTOPOL",
        "COL",
        "UNINSMOT",
        "PUBLICPOL",
        "DENTPRG",
        "DISEASEPRG",
        "CANPRG",
        "ENDRENAL",
        "HIVAIDS",
        "MANDPOL",
        "MENTPRG",
        "SAFNET",
        "SUBPRG",
        "SUBSIDIZ",
        "SUBSIDMC",
        "SUBSUPP",
        "WCBPOL",
        "DENTAL",
        "DISEASE",
        "DRUGPOL",
        "HIP",
        "LTC",
        "MCPOL",
        "POS",
        "HMO",
        "PPO",
        "MENTPOL",
        "SUBPOL",
        "VISPOL",
        "DIS",
        "EWB",
        "FLEXP",
        "LIFE",
        "ANNU",
        "TLIFE",
        "ULIFE",
        "PNC",
        "REI",
        "SURPL",
        "UMBRL",
        "CHAR",
        "CRIME",
        "EAP",
        "GOVEMP",
        "HIRISK",
        "IND",
        "MILITARY",
        "RETIRE",
        "SOCIAL",
        "VET",
    ]
)


VALID_CLINICAL_STATUS_CODES = set(
    [
        "active",
        "recurrence",
        "relapse",
        "inactive",
        "remission",
        "resolved",
    ]
)


OBSERVATION_STATUS = set(
    [
        "registered",
        "preliminary",
        "final",
        "amended",
        "corrected",
        "cancelled",
        "entered-in-error",
        "unknown",
    ]
)
