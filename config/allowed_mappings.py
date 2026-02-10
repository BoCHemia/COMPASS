# Convention: (reference_space, target_space)
ALLOWED_MAPPINGS: set[tuple[str, str]] = {
    # ("ZeroPM", "ZeroPM"),
    ("ZeroPM", "DrugBank"),
    ("ZeroPM", "PFAS"),
    ("ZeroPM", "PlastChem"),
    ("ZeroPM", "Coconut"),
    ("ZeroPM", "AgroTrak"),

    # Coconut
#     ("Coconut", "Coconut"),
    ("Coconut", "DrugBank"),
    ("Coconut", "AgroTrak"),

    # PlastChem
#     ("PlastChem", "PlastChem"),
    ("PlastChem", "PFAS"),

    # DrugBank
#    ("DrugBank", "DrugBank"),
    ("DrugBank", "PFAS"),

}


def is_mapping_allowed(reference_space: str, target_space: str) -> bool:
    """Return True if (reference_space, target_space) is an allowed mapping."""
    return (reference_space, target_space) in ALLOWED_MAPPINGS