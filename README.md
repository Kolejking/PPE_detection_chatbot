# PPE Detection System

A computer-vision-based PPE (Personal Protective Equipment) detection system built using YOLO11, BoT-SORT tracking, spatial PPE-to-person association, SQLite, Streamlit, and a natural-language AI assistant powered by Groq.

The system detects PPE conditions for workers, stores person-level detection results in a local SQLite database, provides a Streamlit dashboard, and allows users to query the stored detection data using natural-language questions.

---

## 1. Features

### Computer Vision

- YOLO11-based PPE detection
- Person detection
- Helmet / No-Helmet detection
- Vest / No-Vest detection
- Safety Shoes / No-Safety-Shoes detection
- Safety Goggles / Without-Safety-Goggles detection
- Image inference
- Video inference
- BoT-SORT object tracking
- Persistent tracking IDs for video processing
- Spatial PPE-to-person association
- Person-level PPE status generation

### Database

- Local SQLite database
- Stores person-level PPE detection records
- Stores detection confidence scores
- Stores timestamps
- Stores source image/video paths
- Stores overall PPE compliance status

### Dashboard

- Streamlit-based web dashboard
- Detection summary
- PPE violation summary
- Recent detection records
- Processed image viewer
- AI assistant

### AI Assistant

The system includes a natural-language chatbot that allows users to ask questions about the detection database.

Example:

> How many people are not wearing helmets?

The chatbot converts the question into SQL, executes the SQL against SQLite, and converts the result into a natural-language answer.

The chatbot can also retrieve relevant image paths from database results and display the corresponding images in the dashboard.

---

# 2. System Architecture

## Overall Pipeline

```text
                    IMAGE / VIDEO INPUT
                            |
                            v
                     YOLO11 Detection
                            |
                            v
                   Person / PPE Detections
                            |
                 +----------+----------+
                 |                     |
              Image                  Video
                 |                     |
                 |              BoT-SORT Tracking
                 |                     |
                 |              Persistent Track IDs
                 |                     |
                 +----------+----------+
                            |
                            v
                 PPE-to-Person Association
                            |
                            v
                  Person-level PPE Status
                            |
                            v
                       SQLite Database
                            |
                            v
                   Streamlit Dashboard
                            |
                            v
                     AI Assistant
                            |
                            v
              Natural Language -> SQL
                            |
                            v
                       SQLite Query
                            |
                            v
                    Query Result
                            |
                            v
                 Natural Language Answer
                 