import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64  
import uuid 
import numpy as np
from pywaffle import Waffle
from reportlab.pdfgen import canvas
import io
from datetime import datetime
from textwrap import wrap
from PIL import Image

# Session state initialization
if 'app_started' not in st.session_state:
    st.session_state['app_started'] = False
if 'fig_created' not in st.session_state:
    st.session_state['fig_created'] = False
if 'fig' not in st.session_state:
    st.session_state['fig'] = None
if 'remarks' not in st.session_state:
    st.session_state['remarks'] = ""
if 'pdf_ready' not in st.session_state:
    st.session_state['pdf_ready'] = False
if 'pdf_data' not in st.session_state:
    st.session_state['pdf_data'] = None
if 'chart_png' not in st.session_state:
    st.session_state['chart_png'] = None
if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None

def main():
    # Advanced Page Configuration
    st.set_page_config(
        page_title="Zaun Analytics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="auto",
    )

    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
        /* Custom color palette */
        :root {
            --primary-color: #3498db;
            --secondary-color: #2ecc71;
            --background-color: #f4f6f7;
            --text-color: #2c3e50;
        }

        /* Enhanced header styling */
        .stMarkdown h1 {
            color: var(--primary-color);
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
        }

        /* Improved container styling */
        .stContainer {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }

        /* Sidebar enhancements */
        .css-1aumxhk {
            background-color: var(--background-color);
        }

        /* Button styling */
        .stButton > button {
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Initial box-shadow */
            transition: box-shadow 0.3s ease;  /* For smooth transition */
        }

        .stButton > button:hover {
            transform: none;  /* Prevents scaling */
            box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.2); /* Slightly darker box-shadow on hover */
        }
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state['app_started']:
        # Display the homepage
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1 style='color: #3498db;'>Welcome to Zaun Analytics</h1>
            <p style='color: #7f8c8d; font-size: 18px;'>
                Unlock insights from your data with powerful visualizations and intuitive analysis tools.
            </p>
            <img src='https://img.icons8.com/external-flaticons-lineal-color-flat-icons/128/external-data-analytics-marketing-technology-flaticons-lineal-color-flat-icons.png' 
                style='max-width: 200px; margin-top: 20px;'>
            <br><br>
        </div>
        """, unsafe_allow_html=True)

        # "Let's Get Started" button
        col1, col2, col3, col4, col5, col6= st.columns([1.8, 1.5, 1, 1, 1 ,1])
        with col3:
            if st.button("Let's Get Started"):
                st.session_state['app_started'] = True
                st.rerun()
            
    else:
        # Header with improved design
        st.markdown("""
        <div style='text-align: center; padding: 20px; border-radius: 10px;'>
            <h1 style='color: #3498db; margin-bottom: 10px;'>📊 Zaun Analytics</h1>
            <p style='color: #7f8c8d; font-size: 16px;'>
            Unlock insights from your data with powerful visualizations and intuitive analysis tools
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Sidebar Layout
        with st.sidebar:
            st.image("https://img.icons8.com/external-flat-vol-2-vectorslab/68/external-Data-Visualization-web-marketing-flat-vol-2-vectorslab.png", width=68)
            
            # File Uploader with improved UI
            st.header("📤 Data Upload")
            uploaded_file = st.file_uploader(
                "Choose a CSV file", 
                type=["csv"],
                help="Upload a clean CSV file to start your analysis",
                accept_multiple_files=False,
                key='uploaded_file_key'  # Unique key
            )

            # Additional sidebar information
            st.markdown("---")
            st.info("""
            💡 Tips:
            - Ensure your CSV is clean and well-formatted
            - Select appropriate columns for visualization
            - Use chart options to customize your view
            """)

        # Main Content Area
        # Assign the uploaded file to session state
        if uploaded_file is not None:
            st.session_state['uploaded_file'] = uploaded_file

        # Main Content Area
        if st.session_state['uploaded_file'] is not None:
            # Load and process data
            try:
                data = pd.read_csv(st.session_state['uploaded_file'])

                # Tabs for different views
                tab1, tab2, tab3 = st.tabs(["📊 Visualize", "📋 Data View", "🔍 Insights"])

                with tab1:
                    st.header("Visualization Studio")

                    chart_type = st.selectbox(
                        "Select Visualization Type",
                        ["Column Chart", "Cumulative Line Chart", "Heatmap", "Stacked Bar Chart", "Waffle Chart"]
                    )

                    columns = data.columns.tolist()
                    col1, col2 = st.columns(2)
                    with col1:
                        x_axis = st.selectbox("X-Axis Column", columns)
                    with col2:
                        y_axis = st.selectbox("Y-Axis Column", columns)

                    if st.button("Create Visualization"):
                        with st.spinner("Generating visualization..."):
                            fig = None  # Initialize fig

                            if chart_type == "Column Chart":
                                fig, ax = plt.subplots(figsize=(10, 5))
                                sns.barplot(x=x_axis, y=y_axis, data=data, ax=ax)
                                ax.set_title(f"{chart_type} for {x_axis} and {y_axis}")

                            elif chart_type == "Cumulative Line Chart":
                                if pd.api.types.is_numeric_dtype(data[y_axis]):
                                    data_copy = data.copy()
                                    data_copy.sort_values(by=x_axis, inplace=True)  # Sort the copy
                                    data_copy['Cumulative'] = data_copy[y_axis].cumsum()
                                    fig, ax = plt.subplots(figsize=(10, 5))
                                    ax.plot(data_copy[x_axis], data_copy['Cumulative'], marker='o', label="Cumulative")
                                    ax.set_title(f"Cumulative Line Chart for {x_axis} and {y_axis}")
                                    ax.legend()
                                else:
                                    st.warning("Cumulative Line Chart requires a numeric Y-column.")

                            elif chart_type == "Heatmap":
                                if data[x_axis].nunique() <= 20 and data[y_axis].nunique() <= 20:
                                    try: # Handle ValueErrors for empty data
                                        pivot_table = data.pivot_table(index=y_axis, columns=x_axis, aggfunc="size", fill_value=0)
                                        fig, ax = plt.subplots(figsize=(10, 5))
                                        sns.heatmap(pivot_table, annot=True, fmt="d", cmap="coolwarm", ax=ax)
                                        ax.set_title(f"Heatmap for {x_axis} and {y_axis}")
                                    except ValueError as e:
                                        st.warning(f"ValueError: {e}. This might be because the selected combination of rows and columns results in empty data. Please try a different combination")
                                        fig = None
                                else:
                                    st.warning("Heatmap is best suited for categorical data with fewer unique values.")

                            elif chart_type == "Stacked Bar Chart":
                                if data[x_axis].nunique() <= 20:
                                    try:
                                        grouped_data = data.groupby([x_axis, y_axis]).size().unstack(fill_value=0)
                                        fig, ax = plt.subplots(figsize=(10, 5))
                                        grouped_data.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")
                                        ax.set_title(f"Stacked Bar Chart for {x_axis} and {y_axis}")
                                    except ValueError as e:
                                        st.warning(f"ValueError: {e}. This could because there is not enough data for your selections. Please try a different selection.")
                                        fig = None # So you can handle the conditional pyplot call and the download button. 
                                else:
                                    st.warning("Stacked Bar Chart is best suited for data with fewer unique X-values.")

                            elif chart_type == "Waffle Chart":
                                if pd.api.types.is_numeric_dtype(data[y_axis]):
                                    proportions = data.groupby(x_axis)[y_axis].sum()
                                    fig = plt.figure(FigureClass=Waffle, rows=10, values=proportions,
                                                    legend={"loc": "upper left", "bbox_to_anchor": (1, 1)}, figsize=(10, 5))
                                else:
                                    st.warning("Waffle Chart requires numeric data for Y-column.")
                                    
                            if fig:  # If chart creation successful
                                st.session_state['fig_created'] = True
                                st.session_state['fig'] = fig

                                # Save chart as PNG in session state
                                buf = io.BytesIO()
                                fig.savefig(buf, format="png", bbox_inches='tight')
                                buf.seek(0)
                                st.session_state['chart_png'] = buf.getvalue()

                                st.session_state['pdf_ready'] = False  # Reset PDF ready state
                                
                    # Check if a visualization has been created and display it
                    if st.session_state['fig_created']:
                        st.header("Visualization")
                        st.pyplot(st.session_state['fig'], use_container_width=True)

                        # Download Chart as PNG
                        st.download_button(
                            label="Download Chart as PNG",
                            data=st.session_state['chart_png'],
                            file_name="chart.png",
                            mime="image/png"
                        )

                        # Generate Report Section
                        st.subheader("Generate Report")

                        # Capture remarks using session state
                        remarks = st.text_area(
                            "Remarks for the report",
                            value=st.session_state['remarks'],
                            height=100,
                            key='remarks',
                        )
                        
                        st.caption("Please press 'cmd/ctrl + Enter' or click outside the text area to ensure your remarks are captured before generating the PDF.")
                        
                        # Prepare the prompt for the AI service
                        prompt = f"""
                                    I have created a {chart_type} using the following data:

                                    - X-Axis ({x_axis}): {data[x_axis].unique().tolist()[:10]}...
                                    - Y-Axis ({y_axis}): {data[y_axis].unique().tolist()[:10]}...

                                    Please provide a brief analysis and remarks about this visualization.
                                    """

                        # Display the prompt
                        st.write("### Generate Remarks with Gemini or ChatGPT")
                        st.info("You can use the prompt below to generate remarks using Gemini or ChatGPT. Copy the prompt, open the AI service in a new tab, and paste it there to get your remarks.")

                        # Display the prompt with copy-to-clipboard functionality
                        st.code(prompt, language='')

                        st.write("Click the **Copy** button in the top-right corner of the code block to copy the prompt.")

                        # Display the buttons in a row
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("""
                            <style>
                            .chatgpt-button {
                                background-color: #f4f6f7;
                                color: white;
                                padding: 10px 24px;
                                font-size: 16px;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                                text-align: center;
                                text-decoration: none;
                                display: inline-block;
                                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                                transition: box-shadow 0.3s ease;
                            }
                            .chatgpt-button:hover {
                                background-color: #f4f6f7;
                                box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.2);
                            }
                            </style>
                            <a href="https://chat.openai.com/" target="_blank" class="chatgpt-button">Open ChatGPT</a>
                            """, unsafe_allow_html=True)

                        with col2:
                            st.markdown("""
                            <style>
                            .gemini-button {
                                background-color: #f4f6f7;
                                color: white;
                                padding: 10px 24px;
                                font-size: 16px;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                                text-align: center;
                                text-decoration: none;
                                display: inline-block;
                                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                                transition: box-shadow 0.3s ease;
                            }
                            .gemini-button:hover {
                                background-color: #f4f6f7;
                                box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.2);
                            }
                            </style>
                            <a href="https://gemini.google.com/" target="_blank" class="gemini-button">Open Google Gemini</a>
                            """, unsafe_allow_html=True)

                        # Instructions for the user
                        st.write("""
                            1. Click the **Copy** button above the prompt to copy it.
                            2. Click **Open ChatGPT** or **Open Google Gemini** to open the AI service in a new tab.
                            3. Paste the prompt into the AI chat and get your generated remarks.
                            4. Copy the generated remarks and paste them into the **'Remarks for the report'** text area.
                            """)
                        
                        # Button to generate PDF
                        if st.button("Generate PDF Report"):
                            # Generate the PDF using st.session_state['fig'] and st.session_state['remarks']
                            pdf_buffer = io.BytesIO()
                            p = canvas.Canvas(pdf_buffer, pagesize=(595, 842))

                            # Modern styling colors
                            header_color = (52/255, 152/255, 219/255)  # Blue (#3498db)
                            text_color = (44/255, 62/255, 80/255)      # Dark gray (#2c3e50)
                            accent_color = (46/255, 204/255, 113/255)  # Green (#2ecc71)

                            # Header with background
                            p.setFillColor(header_color)
                            p.rect(0, 700, 612, 142, fill=True)

                            # White text for header
                            p.setFillColor('white')
                            p.setFont("Helvetica-Bold", 24)
                            p.drawString(50, 780, "Zaun Analytics Report")
                            p.setFont("Helvetica", 14)
                            p.drawString(50, 750, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                            # Decorative line
                            p.setStrokeColor(accent_color)
                            p.setLineWidth(3)
                            p.line(50, 730, 550, 730)

                            # Chart section
                            p.setFillColor(text_color)
                            p.setFont("Helvetica-Bold", 16)
                            p.drawString(50, 670, "Visualization")

                            # Use the image from session state without saving to a file
                            img_buffer = io.BytesIO(st.session_state['chart_png'])
                            img = Image.open(img_buffer)
                            img_width, img_height = img.size
                            aspect = img_height / img_width
                            img_output_width = 500
                            img_output_height = img_output_width * aspect

                            # Add chart with border
                            p.setStrokeColor(header_color)
                            p.setLineWidth(1)
                            p.rect(45, 320, 510, 340, stroke=True)
                            p.drawInlineImage(img, 50, 325, width=img_output_width, height=img_output_height)

                            # Remarks Section
                            p.setFont("Helvetica-Bold", 16)
                            p.drawString(50, 300, "Analysis & Remarks:")

                            p.setFont("Helvetica", 10)
                            if st.session_state['remarks'].strip():
                                remarks_text = st.session_state['remarks']
                                lines = remarks_text.split('\n')  # Split text by line breaks
                                y_position = 280
                                for line in lines:
                                    if line.strip().startswith(('-', '*')):
                                        indent = 60  # Indent bullet points
                                    else:
                                        indent = 50
                                    wrapped_lines = wrap(line, width=115)
                                    for wrapped_line in wrapped_lines:
                                        if y_position < 50:
                                            p.showPage()
                                            y_position = 800
                                            # Re-draw header or other necessary elements on the new page if needed
                                            p.setFont("Helvetica", 10)  # Reset font after page break
                                        p.drawString(50, y_position, wrapped_line)
                                        y_position -= 15  # Adjust line spacing as needed
                            else:
                                p.setFont("Helvetica", 12)
                                p.drawString(50, 180, "No remarks provided.")

                            # Modern footer
                            p.setFillColor(header_color)
                            p.rect(0, 0, 612, 50, fill=True)
                            p.setFillColor('white')
                            p.setFont("Helvetica", 10)
                            p.drawString(50, 20, "Zaun Analytics | Developed by Zaun Team")
                            p.drawString(400, 20, f"Report ID: ZA{datetime.now().strftime('%Y%m%d%H%M')}")

                            # Save and prepare for download
                            p.save()
                            pdf_buffer.seek(0)
                            st.session_state['pdf_data'] = pdf_buffer.getvalue()
                            st.session_state['pdf_ready'] = True

                        # Display the download button if PDF is ready
                        if st.session_state.get('pdf_ready', False):
                            st.success("PDF Report generated successfully!")

                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=st.session_state['pdf_data'],
                                file_name=f"Zaun_Analytics_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                            )                   
                                    
                with tab2:
                    st.header("Raw Data Explorer")
                    st.dataframe(data, use_container_width=True)
                    
                    # Basic data statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Rows", len(data))
                    with col2:
                        st.metric("Total Columns", len(data.columns))
                    with col3:
                        st.metric("Memory Usage", f"{data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

                with tab3:
                    st.header("Quick Insights")

                    # Data Types
                    st.subheader("Data Types")
                    st.write(data.dtypes)

                    # Numerical Columns Summary
                    st.subheader("Numerical Columns Summary")
                    st.dataframe(data.describe(), use_container_width=True)

                    # Correlation Matrix
                    st.subheader("Correlation Matrix")
                    # Select only numeric columns
                    numeric_cols = data.select_dtypes(include=['float64', 'int64'])
                    corr = numeric_cols.corr()
                    fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
                    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax_corr)
                    st.pyplot(fig_corr)

                    # Missing Values Analysis
                    st.subheader("Missing Values Analysis")
                    missing_values = data.isnull().sum()
                    missing_percent = (missing_values / len(data)) * 100
                    mv_df = pd.DataFrame({
                        'Missing Values': missing_values,
                        'Percentage (%)': missing_percent
                    })
                    st.dataframe(mv_df)

                    # Top Categories for Categorical Variables
                    st.subheader("Top Categories in Categorical Variables")
                    categorical_cols = data.select_dtypes(include=['object', 'category']).columns
                    for col in categorical_cols:
                        st.write(f"**{col}**")
                        top_categories = data[col].value_counts().head(5)
                        st.bar_chart(top_categories)

                    # Automated Text Insights
                    st.subheader("Automated Insights")
                    insights = generate_automated_insights(data)
                    st.write(insights)

                    # Button to generate Quick Insights PDF
                    if st.button("Download Quick Insights PDF"):
                        pdf_data = generate_quick_insights_pdf(data, fig_corr, insights)
                        st.download_button(
                            label="⬇️ Download Quick Insights PDF",
                            data=pdf_data,
                            file_name=f"Quick_Insights_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                        )

                # ... [Rest of your code]

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.warning("Please check your CSV file format and try again.")

        else:
            # Enhanced welcome screen
            st.markdown("""
            <div style='text-align: center; padding: 50px; background-color: #f0f2f6; border-radius: 10px;'>
                <h2 style='color: #3498db;'>Welcome to Zaun Analytics</h2>
                <p style='color: #7f8c8d;'>
                    Upload a CSV file to begin your data exploration journey
                </p>
                <img src='https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/external-data-visualization-marketing-technology-flaticons-lineal-color-flat-icons-2.png' 
                    style='max-width: 100%; border-radius: 10px; margin-top: 20px;'>
            </div>
            """, unsafe_allow_html=True)

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #7f8c8d;'>
        <strong>Zaun Analytics</strong> | Developed by Zaun Team | Powered by Streamlit
        </div>
        """, unsafe_allow_html=True)

    # Function to generate automated insights
    def generate_automated_insights(data):
        insights = ""
        numerical_cols = data.select_dtypes(include=['float64', 'int64']).columns
        if len(numerical_cols) > 0:
            # Variable with highest mean
            mean_values = data[numerical_cols].mean().sort_values(ascending=False)
            highest_mean_col = mean_values.index[0]
            highest_mean_value = mean_values.iloc[0]
            insights += f"- The variable with the highest mean is **{highest_mean_col}** ({highest_mean_value:.2f}).\n"

            # Most correlated variables
            corr_matrix = data[numerical_cols].corr().abs()
            corr_matrix.values[np.tril_indices_from(corr_matrix)] = 0  # Set lower triangle and diagonal to zero
            max_corr = corr_matrix.unstack().sort_values(ascending=False)
            if not max_corr.empty:
                most_corr_pair = max_corr.index[0]
                most_corr_value = max_corr.iloc[0]
                insights += f"- The most correlated variables are **{most_corr_pair[0]}** and **{most_corr_pair[1]}** with a correlation of {most_corr_value:.2f}.\n"
        else:
            insights = "No numerical columns available for analysis."
        return insights

    # Function to generate Quick Insights PDF
    def generate_quick_insights_pdf(data, fig_corr, insights):
        pdf_buffer = io.BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=(595, 842))

        # Modern styling colors
        header_color = (52/255, 152/255, 219/255)  # Blue (#3498db)
        text_color = (44/255, 62/255, 80/255)      # Dark gray (#2c3e50)
        accent_color = (46/255, 204/255, 113/255)  # Green (#2ecc71)

        # Header with background
        p.setFillColor(header_color)
        p.rect(0, 770, 612, 72, fill=True)

        # White text for header
        p.setFillColor('white')
        p.setFont("Helvetica-Bold", 24)
        p.drawString(50, 800, "Zaun Analytics Quick Insights")
        p.setFont("Helvetica", 14)
        p.drawString(50, 780, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Decorative line
        p.setStrokeColor(accent_color)
        p.setLineWidth(3)
        p.line(50, 770, 550, 770)

        y_position = 750

        # Automated Insights
        p.setFillColor(text_color)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y_position, "Automated Insights:")
        y_position -= 20

        p.setFont("Helvetica", 10)
        insights_lines = insights.split('\n')
        for line in insights_lines:
            wrapped_lines = wrap(line, width=115)
            for wrapped_line in wrapped_lines:
                if y_position < 50:
                    p.showPage()
                    y_position = 800
                    p.setFont("Helvetica", 10)
                p.drawString(50, y_position, wrapped_line)
                y_position -= 15

        # Correlation Matrix Image
        y_position -= 20
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y_position, "Correlation Matrix:")
        y_position -= 10

        # Save the correlation matrix figure to a buffer
        corr_img_buffer = io.BytesIO()
        fig_corr.savefig(corr_img_buffer, format="png", bbox_inches='tight')
        corr_img_buffer.seek(0)
        corr_img = Image.open(corr_img_buffer)

        # Add the image to the PDF
        p.drawInlineImage(corr_img, 50, y_position - 300, width=500, height=300)
        y_position -= 320

        # Modern footer
        p.setFillColor(header_color)
        p.rect(0, 0, 612, 50, fill=True)
        p.setFillColor('white')
        p.setFont("Helvetica", 10)
        p.drawString(50, 20, "Zaun Analytics | Developed by Zaun Team")
        p.drawString(400, 20, f"Report ID: ZA{datetime.now().strftime('%Y%m%d%H%M')}")

        # Save and prepare for download
        p.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

if __name__ == "__main__":
    main()