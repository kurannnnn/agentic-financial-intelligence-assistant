import streamlit as st
from rag import ask_question


st.set_page_config(
    page_title="Agentic Financial Intelligence Assistant",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Agentic Financial Intelligence Assistant")

st.markdown("""
### Ask questions about:

- Infosys Annual Report
- Infosys Investor Presentation
- IMF World Economic Outlook
- World Bank Global Economic Prospects
""")

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:

    st.header("Options")

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()

# Display Previous Messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Box
query = st.chat_input(
    "Ask a financial question..."
)

if query:

    # User Message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    # Assistant Response
    with st.chat_message("assistant"):

        with st.spinner(
            "🔍 Analyzing financial documents..."
        ):

            answer, sources = ask_question(query)

            st.markdown(answer)

            st.markdown("### Sources")

            source_lines = []

            seen = set()

            for source in sources:

                line = (
                    f"📄 {source['file']} "
                    f"(Page {source['page']})"
                )

                if line not in seen:

                    st.markdown(line)

                    source_lines.append(line)

                    seen.add(line)

            final_response = (
                answer
                + "\n\n### Sources\n"
                + "\n".join(source_lines)
            )

    # Save Assistant Response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": final_response
        }
    )