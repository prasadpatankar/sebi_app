## Merge PDF
import streamlit as st
from PyPDF2 import PdfMerger
import os
from io import BytesIO  # Import BytesIO
import pandas as pd

st.title("PDF Merger")

uploaded_files = st.file_uploader("Choose your PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    merger = PdfMerger()
    filenames = []

    for uploaded_file in uploaded_files:
        try:
            with open(os.path.join("temp", uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            filenames.append(uploaded_file.name)
            merger.append(os.path.join("temp", uploaded_file.name))
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")
    if filenames:
        st.success(f"Successfully uploaded and merged: {', '.join(filenames)}")

        # Use BytesIO to store the merged PDF in memory
        buffer = BytesIO()
        merger.write(buffer)
        merger.close()

        # Get the bytes from the buffer
        merged_pdf = buffer.getvalue()


        # Clean up temporary files
        for filename in filenames:
            os.remove(os.path.join("temp", filename))

        # Provide download button
        st.download_button(
            label="Download Merged PDF",
            data=merged_pdf,
            file_name="merged_output.pdf",
            mime="application/pdf",
        )


    if not os.path.exists("temp"):
        os.makedirs("temp")
