# ============================================================
# PPE CORRECTIVE ACTIONS
# ============================================================


CORRECTIVE_ACTIONS = {

    "NO-HELMET": (
        "Affected personnel need to wear an approved "
        "safety helmet before continuing work."
    ),

    "NO-VEST": (
        "Affected personnel need to wear the required "
        "high-visibility safety vest."
    ),

    "NO-SAFETY-SHOES": (
        "Affected personnel need to wear the required "
        "safety footwear before starting work."
    ),

    "WITHOUT-GOGGLES": (
        "Affected personnel need to wear the required "
        "safety goggles or appropriate eye protection."
    )
}


# ============================================================
# DISPLAY NAMES
# ============================================================

DISPLAY_NAMES = {

    "NO-HELMET": "Helmet",

    "NO-VEST": "Safety Vest",

    "NO-SAFETY-SHOES": "Safety Shoes",

    "WITHOUT-GOGGLES": "Safety Goggles"
}


# ============================================================
# GET ACTION FOR A SINGLE VIOLATION
# ============================================================

def get_corrective_action(status):

    return CORRECTIVE_ACTIONS.get(
        status,
        "No corrective action is defined for this status."
    )


# ============================================================
# DETECT VIOLATION TYPE FROM USER QUESTION
# ============================================================

def detect_violation_type(question):

    question = question.lower().strip()


    # --------------------------------------------------------
    # HELMET
    # --------------------------------------------------------

    helmet_phrases = [

        "without helmet",

        "without a helmet",

        "not wearing helmet",

        "not wearing a helmet",

        "no helmet",

        "missing helmet",

        "helmet violation",

        "helmet violations",

        "don't wear helmet",

        "do not wear helmet"
    ]


    for phrase in helmet_phrases:

        if phrase in question:

            return "NO-HELMET"


    # --------------------------------------------------------
    # SAFETY VEST
    # --------------------------------------------------------

    vest_phrases = [

        "without vest",

        "without a vest",

        "not wearing vest",

        "not wearing a vest",

        "no vest",

        "missing vest",

        "vest violation",

        "vest violations",

        "don't wear vest",

        "do not wear vest"
    ]


    for phrase in vest_phrases:

        if phrase in question:

            return "NO-VEST"


    # --------------------------------------------------------
    # SAFETY SHOES
    # --------------------------------------------------------

    shoes_phrases = [

        "without safety shoes",

        "without safety shoe",

        "not wearing safety shoes",

        "not wearing safety shoe",

        "no safety shoes",

        "no safety shoe",

        "missing safety shoes",

        "missing safety shoe",

        "safety shoes violation",

        "safety shoe violation",

        "safety shoes violations",

        "safety shoe violations"
    ]


    for phrase in shoes_phrases:

        if phrase in question:

            return "NO-SAFETY-SHOES"


    # --------------------------------------------------------
    # SAFETY GOGGLES
    # --------------------------------------------------------

    goggles_phrases = [

        "without goggles",

        "without safety goggles",

        "not wearing goggles",

        "not wearing safety goggles",

        "no goggles",

        "no safety goggles",

        "missing goggles",

        "missing safety goggles",

        "goggle violation",

        "goggles violation",

        "goggle violations",

        "goggles violations"
    ]


    for phrase in goggles_phrases:

        if phrase in question:

            return "WITHOUT-GOGGLES"


    return None


# ============================================================
# CHECK WHETHER QUESTION IS ABOUT NON-COMPLIANCE
# ============================================================

def is_noncompliance_question(question):

    question = question.lower().strip()


    keywords = [

        "non-compliant",

        "non compliant",

        "noncompliant",

        "violation",

        "violations",

        "without",

        "not wearing",

        "missing",

        "what action",

        "what actions",

        "corrective action",

        "corrective actions",

        "what should they wear",

        "what do they need to wear"
    ]


    for keyword in keywords:

        if keyword in question:

            return True


    return False


# ============================================================
# GET WARNING FOR USER QUESTION
# ============================================================

def get_warning_for_question(
    question,
    violations
):

    # --------------------------------------------------------
    # Find the specific PPE violation mentioned
    # in the user's question
    # --------------------------------------------------------

    status = detect_violation_type(
        question
    )


    # ========================================================
    # SPECIFIC VIOLATION
    # ========================================================

    if status:

        count_mapping = {

            "NO-HELMET":
                violations.get(
                    "helmet",
                    0
                ),

            "NO-VEST":
                violations.get(
                    "vest",
                    0
                ),

            "NO-SAFETY-SHOES":
                violations.get(
                    "shoes",
                    0
                ),

            "WITHOUT-GOGGLES":
                violations.get(
                    "goggles",
                    0
                )
        }


        count = count_mapping.get(
            status,
            0
        )


        # ----------------------------------------------------
        # No violation
        # ----------------------------------------------------

        if count <= 0:

            return None


        display_name = DISPLAY_NAMES.get(
            status,
            status
        )


        action = get_corrective_action(
            status
        )


        return {

            "status": status,

            "name": display_name,

            "count": count,

            "action": action
        }


    # ========================================================
    # GENERAL NON-COMPLIANCE QUESTION
    # ========================================================

    if is_noncompliance_question(
        question
    ):

        warnings = []


        mappings = [

            (
                "helmet",
                "NO-HELMET"
            ),

            (
                "vest",
                "NO-VEST"
            ),

            (
                "shoes",
                "NO-SAFETY-SHOES"
            ),

            (
                "goggles",
                "WITHOUT-GOGGLES"
            )
        ]


        for violation_key, status in mappings:

            count = violations.get(
                violation_key,
                0
            )


            if count > 0:

                warnings.append(
                    {

                        "status": status,

                        "name": DISPLAY_NAMES[
                            status
                        ],

                        "count": count,

                        "action": get_corrective_action(
                            status
                        )
                    }
                )


        if warnings:

            return warnings


    return None
    