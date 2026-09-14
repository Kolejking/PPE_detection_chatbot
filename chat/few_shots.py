# ============================================================
# FEW-SHOT EXAMPLES FOR PPE DATABASE CHATBOT
# ============================================================

few_shots = [

    # --------------------------------------------------------
    # HELMET
    # --------------------------------------------------------

    {
        "question": "How many people are wearing helmets?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE helmet_status = 'HELMET';
""",
    },

    {
        "question": "How many people are not wearing helmets?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE helmet_status = 'NO-HELMET';
""",
    },

    {
        "question": "Which images contain people without helmets?",
        "sql": """
SELECT DISTINCT source
FROM ppe_detections
WHERE helmet_status = 'NO-HELMET';
""",
    },


    # --------------------------------------------------------
    # VEST
    # --------------------------------------------------------

    {
        "question": "How many people are wearing safety vests?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE vest_status = 'VEST';
""",
    },

    {
        "question": "How many people are not wearing safety vests?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE vest_status = 'NO-VEST';
""",
    },

    {
        "question": "Which unique images contain people without safety vests?",
        "sql": """
SELECT DISTINCT source
FROM ppe_detections
WHERE vest_status = 'NO-VEST';
""",
    },


    # --------------------------------------------------------
    # SAFETY SHOES
    # --------------------------------------------------------

    {
        "question": "How many people have safety shoes?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE safety_shoes_status = 'SAFETY-SHOES';
""",
    },

    {
        "question": "How many people are wearing safety shoes?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE safety_shoes_status = 'SAFETY-SHOES';
""",
    },

    {
        "question": "How many people are not wearing safety shoes?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE safety_shoes_status = 'NO-SAFETY-SHOES';
""",
    },

    {
        "question": "How many unique images contain safety shoes?",
        "sql": """
SELECT COUNT(DISTINCT source)
FROM ppe_detections
WHERE safety_shoes_status = 'SAFETY-SHOES';
""",
    },

    {
        "question": "Give me the unique image files that contain safety shoes.",
        "sql": """
SELECT DISTINCT source
FROM ppe_detections
WHERE safety_shoes_status = 'SAFETY-SHOES';
""",
    },


    # --------------------------------------------------------
    # SAFETY GOGGLES
    # --------------------------------------------------------

    {
        "question": "How many people are wearing safety goggles?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE safety_goggles_status = 'WITH-GOGGLES';
""",
    },

    {
        "question": "How many people have safety goggles?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE safety_goggles_status = 'WITH-GOGGLES';
""",
    },

    {
        "question": "How many people are not wearing safety goggles?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE safety_goggles_status = 'WITHOUT-GOGGLES';
""",
    },

    {
        "question": "Which images contain people wearing safety goggles?",
        "sql": """
SELECT DISTINCT source
FROM ppe_detections
WHERE safety_goggles_status = 'WITH-GOGGLES';
""",
    },

    {
        "question": "Which images contain people without safety goggles?",
        "sql": """
SELECT DISTINCT source
FROM ppe_detections
WHERE safety_goggles_status = 'WITHOUT-GOGGLES';
""",
    },


    # --------------------------------------------------------
    # COMPLIANCE
    # --------------------------------------------------------

    {
        "question": "How many people are compliant?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE overall_status = 'COMPLIANT';
""",
    },

    {
        "question": "How many people are non-compliant?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections
WHERE overall_status = 'NON-COMPLIANT';
""",
    },

    {
        "question": "Show the non-compliant detection records.",
        "sql": """
SELECT id, timestamp, source, person_index, overall_status
FROM ppe_detections
WHERE overall_status = 'NON-COMPLIANT'
ORDER BY id DESC;
""",
    },


    # --------------------------------------------------------
    # LATEST DETECTION
    # --------------------------------------------------------

    {
        "question": "What is the latest detection?",
        "sql": """
SELECT id, timestamp, source, person_index, overall_status
FROM ppe_detections
ORDER BY id DESC
LIMIT 1;
""",
    },

    {
        "question": "What is the latest timestamp?",
        "sql": """
SELECT timestamp
FROM ppe_detections
ORDER BY id DESC
LIMIT 1;
""",
    },


    # --------------------------------------------------------
    # DATABASE RECORDS
    # --------------------------------------------------------

    {
        "question": "How many detection records are in the database?",
        "sql": """
SELECT COUNT(*)
FROM ppe_detections;
""",
    },

    {
        "question": "How many unique images are in the database?",
        "sql": """
SELECT COUNT(DISTINCT source)
FROM ppe_detections;
""",
    },
]
