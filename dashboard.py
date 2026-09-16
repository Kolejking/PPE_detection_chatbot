import sqlite3
import re
from pathlib import Path

import streamlit as st

from chat.helper import process_query_with_result
from chat.voice_input import transcribe_audio
from chat.corrective_actions import (
    get_warning_for_question
)


# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = Path(
    "database/ppe_detection.db"
)

OUTPUT_IMAGE_DIR = Path(
    "outputs/images"
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PPE Detection System",
    page_icon="🦺",
    layout="wide"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(
        DB_PATH
    )


# ============================================================
# DATABASE SUMMARY
# ============================================================

def get_summary():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT

            COUNT(*) AS total,

            SUM(
                CASE
                    WHEN overall_status = 'COMPLIANT'
                    THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN overall_status = 'NON-COMPLIANT'
                    THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN overall_status = 'PARTIAL'
                    THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN overall_status = 'UNKNOWN'
                    THEN 1
                    ELSE 0
                END
            )

        FROM ppe_detections
        """
    )

    row = cursor.fetchone()

    connection.close()

    return {

        "total": row[0] or 0,

        "compliant": row[1] or 0,

        "non_compliant": row[2] or 0,

        "partial": row[3] or 0,

        "unknown": row[4] or 0
    }


# ============================================================
# PPE VIOLATIONS
# ============================================================

def get_violations():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT

            SUM(
                CASE
                    WHEN helmet_status = 'NO-HELMET'
                    THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN vest_status = 'NO-VEST'
                    THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN safety_shoes_status =
                         'NO-SAFETY-SHOES'
                    THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN safety_goggles_status =
                         'WITHOUT-GOGGLES'
                    THEN 1
                    ELSE 0
                END
            )

        FROM ppe_detections
        """
    )

    row = cursor.fetchone()

    connection.close()

    return {

        "helmet": row[0] or 0,

        "vest": row[1] or 0,

        "shoes": row[2] or 0,

        "goggles": row[3] or 0
    }


# ============================================================
# RECENT RECORDS
# ============================================================

def get_recent_records(
    limit=20
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT

            id,
            timestamp,
            source,
            person_index,
            helmet_status,
            vest_status,
            safety_shoes_status,
            safety_goggles_status,
            overall_status

        FROM ppe_detections

        ORDER BY id DESC

        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# EXTRACT IMAGE PATHS FROM DATABASE RESULT
# ============================================================

def extract_image_paths(result):

    image_paths = []

    if not result:

        return image_paths


    # --------------------------------------------------------
    # Case 1:
    # SQLDatabase returns a string
    # --------------------------------------------------------

    if isinstance(
        result,
        str
    ):

        matches = re.findall(
            r"inputs[\\/]+images[\\/]+[^,\]\)\s]+"
            r"\.(?:jpg|jpeg|png|webp)",
            result,
            flags=re.IGNORECASE
        )


        for path in matches:

            path = path.replace(
                "\\",
                "/"
            )


            if path not in image_paths:

                image_paths.append(
                    path
                )


    # --------------------------------------------------------
    # Case 2:
    # Result is a list of tuples
    # --------------------------------------------------------

    elif isinstance(
        result,
        list
    ):

        for row in result:

            if isinstance(
                row,
                (tuple, list)
            ):

                for value in row:

                    if isinstance(
                        value,
                        str
                    ):

                        normalized = value.replace(
                            "\\",
                            "/"
                        )


                        if (
                            normalized.lower().endswith(
                                (
                                    ".jpg",
                                    ".jpeg",
                                    ".png",
                                    ".webp"
                                )
                            )
                            and normalized not in image_paths
                        ):

                            image_paths.append(
                                normalized
                            )


    return image_paths


# ============================================================
# DISPLAY CHAT IMAGES
# ============================================================

def display_chat_images(
    image_paths
):

    if not image_paths:

        return


    st.subheader(
        "🖼️ Related Images"
    )


    # Maximum 3 images per row

    image_columns = st.columns(
        min(
            3,
            len(image_paths)
        )
    )


    for index, image_path in enumerate(
        image_paths
    ):

        relative_path = Path(
            image_path
        )


        full_path = (
            Path(".")
            /
            relative_path
        )


        if full_path.exists():

            with image_columns[
                index % len(image_columns)
            ]:

                st.image(
                    str(full_path),
                    caption=relative_path.name,
                    use_container_width=True
                )

        else:

            st.warning(
                f"Image not found: {image_path}"
            )


# ============================================================
# DISPLAY PPE SAFETY WARNING
# ============================================================

def display_ppe_warning(
    question,
    violations
):

    warning_data = get_warning_for_question(
        question,
        violations
    )


    # --------------------------------------------------------
    # No relevant violation
    # --------------------------------------------------------

    if not warning_data:

        return


    # --------------------------------------------------------
    # Multiple PPE violations
    # --------------------------------------------------------

    if isinstance(
        warning_data,
        list
    ):

        for warning in warning_data:

            st.warning(
                f"⚠️ **SAFETY WARNING — "
                f"{warning['name']}**\n\n"
                f"**{warning['count']} violation(s) detected.**\n\n"
                f"🛠️ **Required Action:** "
                f"{warning['action']}"
            )

        return


    # --------------------------------------------------------
    # Single PPE violation
    # --------------------------------------------------------

    st.warning(
        f"⚠️ **SAFETY WARNING — "
        f"{warning_data['name']}**\n\n"
        f"**{warning_data['count']} violation(s) detected.**\n\n"
        f"🛠️ **Required Action:** "
        f"{warning_data['action']}"
    )


# ============================================================
# HEADER
# ============================================================

st.title(
    "🦺 PPE Detection System"
)

st.caption(
    "YOLO11-based Personal Protective Equipment Monitoring"
)

st.divider()


# ============================================================
# CHECK DATABASE
# ============================================================

if not DB_PATH.exists():

    st.error(
        "Database not found: "
        f"{DB_PATH}"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

summary = get_summary()

violations = get_violations()

records = get_recent_records()


# ============================================================
# OVERALL STATUS
# ============================================================

st.subheader(
    "Overall Status"
)


col1, col2, col3, col4, col5 = st.columns(
    5
)


with col1:

    st.metric(
        "Total Records",
        summary["total"]
    )


with col2:

    st.metric(
        "Compliant",
        summary["compliant"]
    )


with col3:

    st.metric(
        "Non-Compliant",
        summary["non_compliant"]
    )


with col4:

    st.metric(
        "Partial",
        summary["partial"]
    )


with col5:

    st.metric(
        "Unknown",
        summary["unknown"]
    )


# ============================================================
# PPE VIOLATIONS
# ============================================================

st.divider()

st.subheader(
    "⚠️ PPE Violations"
)


col1, col2, col3, col4 = st.columns(
    4
)


with col1:

    st.metric(
        "No Helmet",
        violations["helmet"]
    )


with col2:

    st.metric(
        "No Vest",
        violations["vest"]
    )


with col3:

    st.metric(
        "No Safety Shoes",
        violations["shoes"]
    )


with col4:

    st.metric(
        "Without Goggles",
        violations["goggles"]
    )


# ============================================================
# PROCESSED IMAGE VIEWER
# ============================================================

st.divider()

st.subheader(
    "🖼️ Processed PPE Images"
)


processed_images = sorted(
    OUTPUT_IMAGE_DIR.glob(
        "*_refined_ppe_association.jpg"
    )
)


if processed_images:

    image_names = [

        image.name

        for image in processed_images
    ]


    selected_image = st.selectbox(
        "Select a processed image",
        image_names
    )


    selected_path = (
        OUTPUT_IMAGE_DIR
        /
        selected_image
    )


    st.image(
        str(selected_path),
        caption=selected_image,
        use_container_width=True
    )


else:

    st.info(
        "No processed PPE images found."
    )


# ============================================================
# RECENT RECORDS
# ============================================================

st.divider()

st.subheader(
    "📋 Recent PPE Records"
)


if records:

    table_data = []


    for record in records:

        table_data.append(
            {

                "ID": record[0],

                "Timestamp": record[1],

                "Source": record[2],

                "Person": record[3],

                "Helmet": record[4],

                "Vest": record[5],

                "Safety Shoes": record[6],

                "Safety Goggles": record[7],

                "Overall Status": record[8]
            }
        )


    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "No PPE detection records found."
    )


# ============================================================
# AI ASSISTANT
# ============================================================

st.divider()

st.subheader(
    "🤖 PPE Detection AI Assistant"
)

st.caption(
    "Ask questions about detection records, PPE status, "
    "confidence scores, timestamps, violations, and images."
)


# ============================================================
# CHAT HISTORY
# ============================================================

if (
    "dashboard_messages"
    not in st.session_state
):

    st.session_state.dashboard_messages = []


# ============================================================
# VOICE INPUT STATE
# ============================================================

if (
    "last_voice_audio_id"
    not in st.session_state
):

    st.session_state.last_voice_audio_id = None


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.dashboard_messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


        # ----------------------------------------------------
        # Display warning saved with this message
        # ----------------------------------------------------

        if (
            message["role"] == "assistant"
            and message.get("warning_data")
        ):

            warning_data = message[
                "warning_data"
            ]


            if isinstance(
                warning_data,
                list
            ):

                for warning in warning_data:

                    st.warning(
                        f"⚠️ **SAFETY WARNING — "
                        f"{warning['name']}**\n\n"
                        f"**{warning['count']} "
                        f"violation(s) detected.**\n\n"
                        f"🛠️ **Required Action:** "
                        f"{warning['action']}"
                    )

            else:

                st.warning(
                    f"⚠️ **SAFETY WARNING — "
                    f"{warning_data['name']}**\n\n"
                    f"**{warning_data['count']} "
                    f"violation(s) detected.**\n\n"
                    f"🛠️ **Required Action:** "
                    f"{warning_data['action']}"
                )


        # ----------------------------------------------------
        # Display images belonging to this message
        # ----------------------------------------------------

        if (
            message["role"] == "assistant"
            and "image_paths" in message
        ):

            display_chat_images(
                message["image_paths"]
            )


# ============================================================
# CHAT INPUT AREA
# ============================================================

voice_column, text_column = st.columns(
    [1, 1]
)


# ============================================================
# VOICE INPUT
# ============================================================

with voice_column:

    audio = st.audio_input(
        "🎤 Ask using your voice",
        key="voice_recorder"
    )


# ============================================================
# TEXT INPUT
# ============================================================

with text_column:

    with st.form(
        "text_question_form",
        clear_on_submit=True
    ):

        typed_question = st.text_input(
            "Ask your question",
            placeholder=(
                "e.g. How many people are without helmet?"
            )
        )


        send_button = st.form_submit_button(
            "📤 Send",
            use_container_width=True
        )


# ============================================================
# DETERMINE QUESTION SOURCE
# ============================================================

voice_question = None

text_question = None


# ------------------------------------------------------------
# Process a new voice recording
# ------------------------------------------------------------

if audio:

    audio_id = hash(
        audio.getvalue()
    )


    if (
        audio_id
        !=
        st.session_state.last_voice_audio_id
    ):

        st.session_state.last_voice_audio_id = (
            audio_id
        )


        with st.spinner(
            "🎤 Converting speech to text..."
        ):

            try:

                voice_question = transcribe_audio(
                    audio
                )

            except Exception as e:

                st.error(
                    "Voice transcription failed: "
                    f"{e}"
                )

                voice_question = None


# ------------------------------------------------------------
# Process typed question
# ------------------------------------------------------------

if (
    send_button
    and
    typed_question
    and
    typed_question.strip()
):

    text_question = typed_question.strip()


# ============================================================
# SELECT FINAL QUESTION
# ============================================================

question = (
    voice_question
    if voice_question
    else text_question
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # --------------------------------------------------------
    # Display user question
    # --------------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )


    # --------------------------------------------------------
    # Save user message
    # --------------------------------------------------------

    st.session_state.dashboard_messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # --------------------------------------------------------
    # Generate AI answer
    # --------------------------------------------------------

    try:

        with st.spinner(
            "Analyzing detection records..."
        ):

            query_data = process_query_with_result(
                question
            )


            answer = query_data[
                "answer"
            ]


            result = query_data[
                "result"
            ]


            # ------------------------------------------------
            # Extract related images
            # ------------------------------------------------

            image_paths = extract_image_paths(
                result
            )


            # ------------------------------------------------
            # Determine safety warning
            # ------------------------------------------------

            warning_data = get_warning_for_question(
                question,
                violations
            )


    except Exception as e:

        answer = (
            "Sorry, I couldn't process your question.\n\n"
            f"Error: {e}"
        )

        image_paths = []

        warning_data = None


    # ========================================================
    # DISPLAY ASSISTANT RESPONSE
    # ========================================================

    with st.chat_message(
        "assistant"
    ):

        # ----------------------------------------------------
        # 1. AI DATABASE RESULT
        # ----------------------------------------------------

        st.markdown(
            answer
        )


        # ----------------------------------------------------
        # 2. SAFETY WARNING
        # ----------------------------------------------------

        if warning_data:

            # ------------------------------------------------
            # Multiple violations
            # ------------------------------------------------

            if isinstance(
                warning_data,
                list
            ):

                for warning in warning_data:

                    st.warning(
                        f"⚠️ **SAFETY WARNING — "
                        f"{warning['name']}**\n\n"
                        f"**{warning['count']} "
                        f"violation(s) detected.**\n\n"
                        f"🛠️ **Required Action:** "
                        f"{warning['action']}"
                    )


            # ------------------------------------------------
            # Single violation
            # ------------------------------------------------

            else:

                st.warning(
                    f"⚠️ **SAFETY WARNING — "
                    f"{warning_data['name']}**\n\n"
                    f"**{warning_data['count']} "
                    f"violation(s) detected.**\n\n"
                    f"🛠️ **Required Action:** "
                    f"{warning_data['action']}"
                )


        # ----------------------------------------------------
        # 3. RELATED IMAGES
        # ----------------------------------------------------

        display_chat_images(
            image_paths
        )


    # ========================================================
    # SAVE ASSISTANT MESSAGE
    # ========================================================

    st.session_state.dashboard_messages.append(
        {
            "role": "assistant",

            "content": answer,

            "image_paths": image_paths,

            "warning_data": warning_data
        }
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "PPE Detection System • Local SQLite Database • AI Assistant"
)
