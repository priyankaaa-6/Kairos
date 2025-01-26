import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt
import pandas as pd
import os

# Page Configurations
st.set_page_config(
    page_title="Kairos Student Report Card",  # Updated page title to Kairos for consistency
    page_icon="📄",
    layout="wide",  # Changed to wide layout for better visualization of graphs
    initial_sidebar_state="collapsed",
)

# Welcome Header
st.header("AI-Powered Learning Companion - Kairos!")  # Added header for uniformity across apps

# Custom styles using markdown
def set_custom_styles():
    st.markdown(
        """
        <style>
        .stButton button {
            background-color: #FF5722;
            color: white;
            border-radius: 8px;
            padding: 10px;
        }
        .stButton button:hover {
            background-color: #E64A19;
            color: white;
        }
        .stTitle {
            color: #4CAF50;
            font-size: 36px;
        }
        .stHeader {
            color: #1E88E5;
            font-size: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

set_custom_styles()

# Function to generate graphs
def generate_graphs():
    # Sample data for the graphs
    data = {
        "Question Number": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Correctness": [1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
        "Time Taken": [2.1, 3.4, 1.2, 4.0, 3.5, 2.9, 3.0, 3.2, 2.7, 2.8],
    }

    df = pd.DataFrame(data)

    # Pie Chart
    fig1, ax1 = plt.subplots()
    ax1.pie(
        [df["Correctness"].sum(), len(df) - df["Correctness"].sum()],
        labels=["Correct", "Wrong"],
        autopct="%1.1f%%",
        colors=["#4CAF50", "#FF5722"],
    )
    ax1.set_title("Correct vs Wrong Answers")
    plt.savefig("pie_chart.png")
    plt.close(fig1)

    # Violin Plot
    fig2, ax2 = plt.subplots()
    ax2.violinplot(df["Time Taken"], showmeans=True)
    ax2.set_title("Violin Plot of Time Taken")
    ax2.set_xlabel("Questions")
    ax2.set_ylabel("Time Taken (seconds)")
    plt.savefig("violin_plot.png")
    plt.close(fig2)

    # Line Plot
    fig3, ax3 = plt.subplots()
    ax3.plot(df["Question Number"], df["Time Taken"], marker="o")
    ax3.set_title("Line Plot of Time Taken")
    ax3.set_xlabel("Question Number")
    ax3.set_ylabel("Time Taken (seconds)")
    plt.savefig("line_plot.png")
    plt.close(fig3)

    # Scatter Plot
    fig4, ax4 = plt.subplots()
    scatter = ax4.scatter(
        df["Question Number"], df["Time Taken"], c=df["Correctness"], cmap="coolwarm"
    )
    ax4.set_title("Scatter Plot: Time Taken and Correctness")
    ax4.set_xlabel("Question Number")
    ax4.set_ylabel("Time Taken (seconds)")
    plt.colorbar(scatter, ax=ax4, label="Correctness")
    plt.savefig("scatter_plot.png")
    plt.close(fig4)

# Function to create a PDF report card
def create_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.set_font("Arial", style="B", size=20)
    pdf.set_text_color(76, 175, 80)  # Green color
    pdf.cell(0, 10, txt="Student Report Card", ln=True, align="C")

    # Add motivational message
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)  # Black color
    pdf.multi_cell(
        0,
        10,
        txt="Congratulations on completing your test! Remember, every challenge is an opportunity to learn and grow.",
        align="C",
    )

    # Add Pie Chart
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, txt="Performance Overview", ln=True, align="L")
    pdf.image("pie_chart.png", x=50, y=50, w=110)

    # Add Violin Plot
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, txt="Time Analysis", ln=True, align="L")
    pdf.image("violin_plot.png", x=50, y=50, w=110)

    # Add Line Plot
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, txt="Time Taken by Questions", ln=True, align="L")
    pdf.image("line_plot.png", x=50, y=50, w=110)

    # Add Scatter Plot
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, txt="Time vs Correctness", ln=True, align="L")
    pdf.image("scatter_plot.png", x=50, y=50, w=110)

    # Save PDF
    pdf.output("report_card.pdf")

    return "report_card.pdf"

# Generate the page content
st.markdown('<div class="stTitle">Student Report Card Download Page</div>', unsafe_allow_html=True)
st.markdown('<div class="stHeader">Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle.</div>', unsafe_allow_html=True)

# Footer with Project Description
st.markdown(
        """
    <div style="position: fixed; bottom: 20px; right: 20px; font-size: 12px; color: grey; text-align: right;">
        <b>About Kairos:</b> An AI-powered educational tool for PDF analysis, quiz generation, and enhanced learning.
    </div>
    """,
        unsafe_allow_html=True
    )
    
    
# Placeholder for download button
placeholder = st.empty()

if st.button("Generate Report Card for your last Quiz"):
    generate_graphs()
    pdf_path = create_pdf()
    st.success("Report card generated successfully! 🎉")

    # Show download button
    with open(pdf_path, "rb") as file:
        placeholder.download_button(
            label="Download Report Card",
            data=file,
            file_name="report_card.pdf",
            mime="application/pdf",
        )
