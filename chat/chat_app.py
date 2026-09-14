import streamlit as st

from chat.helper import process_query


# --------------------------------------------------
# 1. Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="PPE Detection AI Assistant",
    page_icon="🦺",
    layout="centered"
)


# --------------------------------------------------
# 2. Page title
# --------------------------------------------------

st.title("🦺 PPE Detection AI Assistant")

st.write(
    "Ask questions about PPE detection records, "
    "statuses, confidence scores, timestamps, and violations."
)


# --------------------------------------------------
# 3. Initialize chat history
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# 4. Display previous messages
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# 5. Chat input
# --------------------------------------------------

question = st.chat_input(
    "Ask about the PPE detection records..."
)


# --------------------------------------------------
# 6. Process new question
# --------------------------------------------------

if question:

    # Display user's question
    with st.chat_message("user"):
        st.markdown(question)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Generate answer
    try:

        answer = process_query(question)

    except Exception as e:

        answer = f"Sorry, I couldn't process that question: {e}"

    # Display assistant answer
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
    