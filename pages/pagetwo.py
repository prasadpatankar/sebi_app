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




# Sample data (replace with your actual data)
data = pd.DataFrame({
    'Category': ['A', 'B', 'C', 'A', 'B', 'A'],
    'Subcategory': ['X', 'Y', 'Z', 'X', 'Z', 'Y'],
    'Value': [10, 20, 30, 40, 50, 60]
})

st.title("DataFrame Filtering with Auto-Prompt Text Boxes")
# Get unique values for each categorical column for auto-prompt
categorical_cols = data.select_dtypes(include=['object']).columns
unique_values = {col: data[col].unique().tolist() for col in categorical_cols}

# Create filter text boxes with auto-prompt
filters = {}
for column, unique_vals in unique_values.items():
    selected_values = st.multiselect(
        f"Filter {column}:",
        unique_vals,  # Options for auto-complete
        key=f"multiselect_{column}"  # Important for unique keys
    )
    filters[column] = selected_values  # Store selected values for filtering
 
#"""Filters the DataFrame based on the provided filter dictionary."""
filtered_df = data.copy()
for column, values in filters.items():
    if values:  # Check if there are any filter values for this column
        filtered_df = filtered_df[filtered_df[column].isin(values)]

# Display the filtered DataFrame
st.write("Filtered DataFrame:")
st.dataframe(filtered_df)
