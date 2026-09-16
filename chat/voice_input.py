import json
import wave

import streamlit as st
from vosk import Model, KaldiRecognizer


# ============================================================
# VOSK MODEL
# ============================================================

MODEL_PATH = (
    "models/vosk-model-small-en-us-0.15"
)


# ============================================================
# PPE VOICE GRAMMAR
# ============================================================
#
# These phrases guide Vosk toward the vocabulary
# used by the PPE Detection System.
#
# [unk] allows words outside this list.
# ============================================================

VOICE_GRAMMAR = [

    # --------------------------------------------------------
    # GENERAL QUESTIONS
    # --------------------------------------------------------

    "how many people",

    "how many persons",

    "how many detections",

    "how many records",

    "show me",

    "tell me",

    "give me",

    "what is",

    "what are",

    "which people",

    "which person",

    "show",

    "list",

    "find",


    # --------------------------------------------------------
    # HELMET
    # --------------------------------------------------------

    "helmet",

    "helmets",

    "wearing helmet",

    "wearing a helmet",

    "wearing helmets",

    "wearing a helmet",

    "without helmet",

    "without a helmet",

    "not wearing helmet",

    "not wearing a helmet",

    "no helmet",

    "missing helmet",

    "helmet violation",

    "helmet violations",

    "people wearing helmet",

    "people wearing helmets",

    "people without helmet",

    "people without helmets",

    "people not wearing helmet",

    "people not wearing helmets",


    # --------------------------------------------------------
    # VEST
    # --------------------------------------------------------

    "vest",

    "vests",

    "safety vest",

    "safety vests",

    "wearing vest",

    "wearing a vest",

    "wearing safety vest",

    "wearing a safety vest",

    "wearing vests",

    "without vest",

    "without a vest",

    "without safety vest",

    "without a safety vest",

    "not wearing vest",

    "not wearing a vest",

    "not wearing safety vest",

    "not wearing a safety vest",

    "no vest",

    "no safety vest",

    "missing vest",

    "missing safety vest",

    "vest violation",

    "vest violations",

    "safety vest violation",

    "safety vest violations",

    "people wearing vest",

    "people wearing vests",

    "people wearing safety vest",

    "people without vest",

    "people without vests",

    "people without safety vest",

    "people not wearing vest",

    "people not wearing vests",

    "people not wearing safety vest",


    # --------------------------------------------------------
    # SAFETY SHOES
    # --------------------------------------------------------

    "shoes",

    "shoe",

    "safety shoes",

    "safety shoe",

    "wearing shoes",

    "wearing safety shoes",

    "wearing safety shoe",

    "without shoes",

    "without safety shoes",

    "without safety shoe",

    "not wearing shoes",

    "not wearing safety shoes",

    "not wearing safety shoe",

    "no shoes",

    "no safety shoes",

    "missing shoes",

    "missing safety shoes",

    "safety shoe violation",

    "safety shoes violation",

    "safety shoe violations",

    "safety shoes violations",

    "people wearing safety shoes",

    "people without safety shoes",

    "people not wearing safety shoes",


    # --------------------------------------------------------
    # GOGGLES
    # --------------------------------------------------------

    "goggles",

    "goggle",

    "safety goggles",

    "safety goggle",

    "wearing goggles",

    "wearing safety goggles",

    "wearing a safety goggles",

    "without goggles",

    "without safety goggles",

    "not wearing goggles",

    "not wearing safety goggles",

    "no goggles",

    "no safety goggles",

    "missing goggles",

    "missing safety goggles",

    "goggle violation",

    "goggle violations",

    "goggles violation",

    "goggles violations",

    "people wearing goggles",

    "people wearing safety goggles",

    "people without goggles",

    "people without safety goggles",

    "people not wearing goggles",

    "people not wearing safety goggles",


    # --------------------------------------------------------
    # OVERALL STATUS
    # --------------------------------------------------------

    "compliant",

    "compliance",

    "non compliant",

    "noncompliant",

    "non compliance",

    "partial",

    "partially compliant",

    "unknown",

    "violation",

    "violations",


    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------

    "what action",

    "what actions",

    "corrective action",

    "corrective actions",

    "what should they wear",

    "what do they need to wear",

    "what action should be taken",

    "what actions should be taken",

    "what action is required",

    "what actions are required",

    "what should be done",


    # --------------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------------

    "timestamp",

    "timestamps",

    "time",

    "latest timestamp",

    "most recent timestamp",

    "recent timestamp",

    "latest detection",

    "most recent detection",


    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    "image",

    "images",

    "photo",

    "photos",

    "picture",

    "pictures",

    "latest image",

    "most recent image",

    "recent image",


    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    "confidence",

    "confidence score",

    "confidence scores",

    "average confidence",

    "highest confidence",

    "lowest confidence",


    # --------------------------------------------------------
    # DATABASE / RECORD
    # --------------------------------------------------------

    "record",

    "records",

    "detection",

    "detections",

    "source",

    "sources",

    "person",

    "people",

    # --------------------------------------------------------
    # UNKNOWN WORDS
    # --------------------------------------------------------

    "[unk]"
]


# ============================================================
# LOAD VOSK MODEL
# ============================================================

@st.cache_resource
def load_vosk_model():

    return Model(
        MODEL_PATH
    )


# ============================================================
# TRANSCRIBE AUDIO
# ============================================================

def transcribe_audio(
    audio_file
):

    # --------------------------------------------------------
    # Reset file pointer
    # --------------------------------------------------------

    audio_file.seek(0)


    # --------------------------------------------------------
    # Open WAV file
    # --------------------------------------------------------

    wf = wave.open(
        audio_file,
        "rb"
    )


    # --------------------------------------------------------
    # Validate audio format
    # --------------------------------------------------------

    if wf.getnchannels() != 1:

        wf.close()

        raise ValueError(
            "Voice input must be mono audio."
        )


    if wf.getsampwidth() != 2:

        wf.close()

        raise ValueError(
            "Voice input must use 16-bit PCM audio."
        )


    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = load_vosk_model()


    # --------------------------------------------------------
    # Convert grammar to JSON
    # --------------------------------------------------------

    grammar = json.dumps(
        VOICE_GRAMMAR
    )


    # --------------------------------------------------------
    # Create grammar-based recognizer
    # --------------------------------------------------------

    recognizer = KaldiRecognizer(
        model,
        wf.getframerate(),
        grammar
    )


    # --------------------------------------------------------
    # Enable word confidence information
    # --------------------------------------------------------

    recognizer.SetWords(
        True
    )


    # --------------------------------------------------------
    # Process audio
    # --------------------------------------------------------

    while True:

        data = wf.readframes(
            4000
        )


        if not data:

            break


        recognizer.AcceptWaveform(
            data
        )


    # --------------------------------------------------------
    # Get final result
    # --------------------------------------------------------

    result = json.loads(
        recognizer.FinalResult()
    )


    # --------------------------------------------------------
    # Close WAV
    # --------------------------------------------------------

    wf.close()


    # --------------------------------------------------------
    # Extract text
    # --------------------------------------------------------

    text = result.get(
        "text",
        ""
    ).strip()


    return text
