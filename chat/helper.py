import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from chat.few_shots import few_shots


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found in .env"
    )


# ============================================================
# 2. LOCATE SQLITE DATABASE
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

DB_PATH = (
    BASE_DIR
    / "database"
    / "ppe_detection.db"
)


if not DB_PATH.exists():

    raise FileNotFoundError(
        f"Database not found: {DB_PATH}"
    )


# ============================================================
# 3. CONNECT LANGCHAIN TO SQLITE
# ============================================================

db = SQLDatabase.from_uri(
    f"sqlite:///{DB_PATH}",
    sample_rows_in_table_info=3
)


# ============================================================
# 4. CREATE GROQ LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    api_key=GROQ_API_KEY,
)


# ============================================================
# 5. DATABASE INFORMATION
# ============================================================

def get_database_info():

    return db.get_table_info()


# ============================================================
# 6. GENERATE SQL FROM NATURAL LANGUAGE
# ============================================================

def generate_sql(question: str):

    # --------------------------------------------------------
    # Convert few-shot examples into text
    # --------------------------------------------------------

    few_shot_text = ""

    for example in few_shots:

        few_shot_text += f"""
Example:
User question: {example["question"]}
SQL: {example["sql"]}
"""


    # --------------------------------------------------------
    # SQL generation prompt
    # --------------------------------------------------------

    prompt = ChatPromptTemplate.from_template(
        """
You are an expert SQLite SQL generator for a PPE detection system.

The database contains exactly one table:

ppe_detections(
    id,
    timestamp,
    source,
    track_id,
    person_index,
    helmet_status,
    helmet_score,
    vest_status,
    vest_score,
    safety_shoes_status,
    safety_shoes_score,
    safety_goggles_status,
    safety_goggles_score,
    overall_status
)


============================================================
VALID DATABASE VALUES
============================================================

overall_status:

- COMPLIANT
- NON-COMPLIANT
- PARTIAL
- UNKNOWN


helmet_status:

- HELMET
- NO-HELMET
- UNKNOWN


vest_status:

- VEST
- NO-VEST
- UNKNOWN


safety_shoes_status:

- SAFETY-SHOES
- NO-SAFETY-SHOES
- UNKNOWN


safety_goggles_status:

- WITH-GOGGLES
- WITHOUT-GOGGLES
- UNKNOWN


============================================================
NATURAL LANGUAGE MAPPINGS
============================================================

HELMET:

"wearing helmet"
"wearing a helmet"
"has helmet"
"with helmet"
"people wearing helmets"

    -> helmet_status = 'HELMET'


NO HELMET:

"not wearing helmet"
"not wearing a helmet"
"without helmet"
"no helmet"
"missing helmet"
"helmet violation"
"not wearing helmets"

    -> helmet_status = 'NO-HELMET'


VEST:

"wearing vest"
"wearing a vest"
"has vest"
"with vest"
"people wearing vests"

    -> vest_status = 'VEST'


NO VEST:

"not wearing vest"
"not wearing a vest"
"without vest"
"no vest"
"missing vest"
"vest violation"

    -> vest_status = 'NO-VEST'


SAFETY SHOES:

"wearing safety shoes"
"has safety shoes"
"with safety shoes"
"wearing safety-shoes"

    -> safety_shoes_status = 'SAFETY-SHOES'


NO SAFETY SHOES:

"not wearing safety shoes"
"without safety shoes"
"no safety shoes"
"missing safety shoes"
"safety shoe violation"

    -> safety_shoes_status = 'NO-SAFETY-SHOES'


GOGGLES:

"wearing goggles"
"wearing safety goggles"
"with goggles"
"has goggles"
"people wearing goggles"

    -> safety_goggles_status = 'WITH-GOGGLES'


NO GOGGLES:

"not wearing goggles"
"not wearing safety goggles"
"without goggles"
"without safety goggles"
"no goggles"
"missing goggles"
"goggle violation"

    -> safety_goggles_status = 'WITHOUT-GOGGLES'


============================================================
DOUBLE-NEGATIVE RULE
============================================================

If the user says:

"not without goggles"
"not without safety goggles"

interpret this as:

    safety_goggles_status = 'WITH-GOGGLES'


Do NOT use:

    safety_goggles_status != 'WITHOUT-GOGGLES'

because that would include UNKNOWN records.


============================================================
OVERALL STATUS RULES
============================================================

"compliant"
"compliant detections"
"people who are compliant"

    -> overall_status = 'COMPLIANT'


"non-compliant"
"non compliant"
"noncompliant"
"violations"
"non-compliant detections"

    -> overall_status = 'NON-COMPLIANT'


"partial"
"partially compliant"

    -> overall_status = 'PARTIAL'


"unknown"

    -> overall_status = 'UNKNOWN'


============================================================
TIMESTAMP RULES
============================================================

If the user asks:

"latest timestamp"
"most recent timestamp"
"recent timestamp"
"what is the timestamp"

and no particular record is specified:

    SELECT MAX(timestamp)
    FROM ppe_detections;


If the user asks:

"latest detection"
"most recent detection"

use:

    ORDER BY timestamp DESC
    LIMIT 1


If the user explicitly asks for all timestamps:

    return all timestamps.


Do NOT assume a timezone.


============================================================
IMAGE / SOURCE RULES
============================================================

The image filename/path is stored in:

    source


If the user asks:

"latest image"
"most recent image"
"recent detection image"

use:

    ORDER BY timestamp DESC
    LIMIT 1


and return:

    source


If the user asks for the image associated with a particular
record, return the source column for that record.


============================================================
CONFIDENCE SCORE RULES
============================================================

Helmet confidence:

    helmet_score


Vest confidence:

    vest_score


Safety shoe confidence:

    safety_shoes_score


Safety goggle confidence:

    safety_goggles_score


If the user asks for an average confidence score:

    use AVG()


If the user asks for the highest confidence:

    use MAX()


If the user asks for the lowest confidence:

    use MIN()


============================================================
COUNT RULES
============================================================

If the user asks:

"how many"
"how much"
"number of"

use COUNT() when counting records.


For PPE violations, use the exact violation status.

For example:

"people not wearing helmets"

    -> helmet_status = 'NO-HELMET'


"people not wearing vests"

    -> vest_status = 'NO-VEST'


"people without safety shoes"

    -> safety_shoes_status = 'NO-SAFETY-SHOES'


"people without goggles"

    -> safety_goggles_status = 'WITHOUT-GOGGLES'


============================================================
RECORDS VS UNIQUE IMAGES
============================================================

IMPORTANT:

A row in ppe_detections represents a detection/person record.

The source column identifies the image or video source associated
with that detection.

Therefore:

COUNT(*)

means the number of matching detection/person records.

COUNT(DISTINCT source)

means the number of unique image/source files.

If the user asks:

"how many people"
"how many detections"
"number of detections"
"how many records"

use:

    COUNT(*)


If the user asks:

"how many unique images"
"how many unique image files"
"number of unique images"

use:

    COUNT(DISTINCT source)


If the user asks:

"give me unique images"
"give me unique image files"
"show me unique images"

return:

    SELECT DISTINCT source


Do NOT count individual records when the user explicitly asks
for unique images.


If the user asks for a specific number of unique image files,
for example:

"give me 20 unique image files with safety shoes"

use:

    SELECT DISTINCT source
    FROM ppe_detections
    WHERE safety_shoes_status = 'SAFETY-SHOES'
    LIMIT 20


If fewer than the requested number of unique images exist,
return all available unique images.

Do NOT duplicate the same source path to reach the requested
number.


============================================================
LATEST RECORD RULE
============================================================

For:

"latest record"
"most recent record"
"latest detection"
"most recent detection"

use:

    ORDER BY timestamp DESC
    LIMIT 1


============================================================
FEW-SHOT EXAMPLES
============================================================

The following examples show how natural-language questions
should be converted into SQLite SQL.

Use these examples as patterns.

Pay special attention to the difference between:

COUNT(*)

and:

COUNT(DISTINCT source)

and:

SELECT DISTINCT source

The first counts detection/person records.

The second counts unique source files.

The third returns unique source files.

Do not blindly copy an example. Apply the same reasoning
to the user's current question.

{few_shot_text}


============================================================
SQL SAFETY RULES
============================================================

1. Generate ONLY ONE SQL SELECT query.

2. Never generate:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   CREATE
   REPLACE
   TRUNCATE
   ATTACH
   DETACH
   PRAGMA

3. Do not use MySQL syntax.

4. Use SQLite-compatible SQL.

5. Use only the table and columns provided above.

6. Never invent columns.

7. Use status values EXACTLY as written.

8. Do not use != for explicit PPE violation questions.

9. Do not assume a timezone.

10. Do not invent data.

11. Do not return Markdown.

12. Do not return explanations.

13. Generate only the SQL query.

14. Do not generate multiple SQL statements.


============================================================
USER QUESTION
============================================================

{question}
"""
    )


    # --------------------------------------------------------
    # Create chain
    # --------------------------------------------------------

    chain = prompt | llm


    # --------------------------------------------------------
    # Generate SQL
    # --------------------------------------------------------

    response = chain.invoke(
        {
            "question": question,
            "few_shot_text": few_shot_text
        }
    )


    return response.content.strip()


# ============================================================
# 7. CLEAN GENERATED SQL
# ============================================================

def clean_sql(sql: str):

    sql = sql.strip()


    # Remove Markdown SQL code fences
    sql = re.sub(
        r"```sql",
        "",
        sql,
        flags=re.IGNORECASE
    )


    sql = re.sub(
        r"```",
        "",
        sql
    )


    sql = sql.strip()


    # Remove accidental "SQLQuery:" prefix
    if sql.lower().startswith("sqlquery:"):

        sql = sql[
            len("SQLQuery:"):
        ].strip()


    return sql


# ============================================================
# 8. VALIDATE GENERATED SQL
# ============================================================

def validate_sql(sql: str):

    sql = clean_sql(sql)


    # Only SELECT statements are allowed
    if not sql.lower().startswith("select"):

        raise ValueError(
            "Unsafe SQL rejected. "
            "Only SELECT queries are allowed."
        )


    # Prevent multiple SQL statements
    sql_without_final_semicolon = sql.rstrip(";")

    if ";" in sql_without_final_semicolon:

        raise ValueError(
            "Multiple SQL statements are not allowed."
        )


    # Dangerous SQL keywords
    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "replace",
        "truncate",
        "attach",
        "detach",
        "pragma"
    ]


    sql_lower = sql.lower()


    for keyword in forbidden_keywords:

        if re.search(
            rf"\b{keyword}\b",
            sql_lower
        ):

            raise ValueError(
                f"Unsafe SQL keyword detected: "
                f"{keyword}"
            )


    return sql


# ============================================================
# 9. EXECUTE SQL
# ============================================================

def execute_sql(sql: str):

    sql = validate_sql(sql)

    result = db.run(sql)

    return result


# ============================================================
# 10. GENERATE NATURAL-LANGUAGE ANSWER
# ============================================================

def generate_answer(
    question: str,
    sql: str,
    result: str
):

    prompt = ChatPromptTemplate.from_template(
        """
You are an AI assistant for a PPE detection system.

Answer the user's question using ONLY the database result.

User question:
{question}


SQL query:
{sql}


Database result:
{result}


Rules:

1. Answer the user's question directly.

2. Use ONLY information contained in the database result.

3. Never invent information.

4. Never assume a timezone.

5. Never label a timestamp as UTC unless UTC
   is explicitly present in the database result.

6. Do not mention SQL unless the user asks about SQL.

7. Do not mention the internal database implementation.

8. Do not add information that was not returned
   by the database.

9. Keep the answer concise and easy to understand.

10. If the result is empty, say that no matching
    records were found.

11. If a confidence value is between 0 and 1,
    you may provide both the decimal and percentage.

12. Do not change the meaning of the database result.

13. If the result contains multiple records,
    summarize them accurately.

14. Do not assume that different detection records
    represent different unique people unless the
    database provides a reliable unique person identity.

15. If the database result contains unique source/image
    paths, preserve them accurately.

16. If the user asked for a specific number of unique
    images but fewer unique images were returned,
    clearly state the number of unique images actually
    available instead of duplicating paths.

17. If the result contains image/source paths, list
    the paths accurately and do not invent additional
    image files.
"""
    )


    chain = prompt | llm


    response = chain.invoke(
        {
            "question": question,
            "sql": sql,
            "result": result
        }
    )


    return response.content.strip()


# ============================================================
# 11. COMPLETE QUESTION-ANSWER PIPELINE
# ============================================================

def process_query(question: str):

    if not question or not question.strip():

        raise ValueError(
            "Question cannot be empty."
        )


    # --------------------------------------------------------
    # Step 1: Generate SQL
    # --------------------------------------------------------

    sql = generate_sql(
        question
    )


    # --------------------------------------------------------
    # Step 2: Clean SQL
    # --------------------------------------------------------

    sql = clean_sql(
        sql
    )


    # --------------------------------------------------------
    # Step 3: Validate SQL
    # --------------------------------------------------------

    sql = validate_sql(
        sql
    )


    # --------------------------------------------------------
    # Step 4: Execute SQL
    # --------------------------------------------------------

    result = execute_sql(
        sql
    )


    # --------------------------------------------------------
    # Step 5: Generate final answer
    # --------------------------------------------------------

    answer = generate_answer(
        question,
        sql,
        result
    )


    return answer


# ============================================================
# 11A. COMPLETE QUERY WITH DATABASE RESULT
# ============================================================

def process_query_with_result(question: str):

    if not question or not question.strip():

        raise ValueError(
            "Question cannot be empty."
        )


    # --------------------------------------------------------
    # Step 1: Generate SQL
    # --------------------------------------------------------

    sql = generate_sql(
        question
    )


    # --------------------------------------------------------
    # Step 2: Clean SQL
    # --------------------------------------------------------

    sql = clean_sql(
        sql
    )


    # --------------------------------------------------------
    # Step 3: Validate SQL
    # --------------------------------------------------------

    sql = validate_sql(
        sql
    )


    # --------------------------------------------------------
    # Step 4: Execute SQL
    # --------------------------------------------------------

    result = execute_sql(
        sql
    )


    # --------------------------------------------------------
    # Step 5: Generate final answer
    # --------------------------------------------------------

    answer = generate_answer(
        question,
        sql,
        result
    )


    # --------------------------------------------------------
    # Return everything needed by the UI
    # --------------------------------------------------------

    return {
        "answer": answer,
        "sql": sql,
        "result": result
    }


# ============================================================
# 12. BACKEND TEST
# ============================================================

if __name__ == "__main__":

    question = (
        "How many people are not wearing a helmet?"
    )


    print(
        "\nUser Question:"
    )


    print(
        question
    )


    sql = generate_sql(
        question
    )


    sql = validate_sql(
        sql
    )


    print(
        "\nGenerated SQL:"
    )


    print(
        sql
    )


    result = execute_sql(
        sql
    )


    print(
        "\nSQL Result:"
    )


    print(
        result
    )


    answer = generate_answer(
        question,
        sql,
        result
    )


    print(
        "\nFinal Answer:"
    )


    print(
        answer
    )
    