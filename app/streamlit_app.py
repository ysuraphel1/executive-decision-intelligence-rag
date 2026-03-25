import streamlit as st
from rag import ask_rag

st.title("Leadership Decision Intelligence Explorer")

question = st.text_input("Ask a question")

if st.button("Run") and question:
    result = ask_rag(question)

    st.subheader("Answer")
    st.write(result["answer"])

    st.subheader("Sources")
    for s in result["sources"]:
        st.write(s)
