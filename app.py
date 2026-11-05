# Import the libraries required for our colorful file organizer dashboard.
import streamlit as st 
import pandas as pd
import plotly.express as px 
from pathlib import Path 
import shutil 
import hashlib


#Configure the Streamlit page 
st.set_page_config(
    page_title="smart File Organizer",
    page_icon="🗂️",
    layout="wide"
)


# Add custom CSS to give the dashboard a colorful, modern look
st.markdown("""
<style>

/* Apply a colorful gradient to the complete app background */
.stApp {
    background: linear-gradient(
        135deg,
        #E9D5FF 0%,
        #DBEAFE 35%,
        #FCE7F3 70%,
        #EDE9FE 100%
    ) !important;
}

/* Make the main content background transparent */
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: transparent !important;
}

/* Add spacing around the dashboard */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Style the main dashboard title */
.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #54278F;
}

/* Style the dashboard subtitle */
.subtitle {
    color: #6B6480;
    font-size: 17px;
}

/* Style metric cards */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid #E5D8FF;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(84, 39, 143, 0.12);
}

</style>
""", unsafe_allow_html=True)


# Display the app title and introduction 
st.markdown('<div class="main-title"> 🗂️ smart File Organizer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle"> A colorful dashboard to inspect and organize files automatically.</div>', unsafe_allow_html=True)
st.divider()

# Let the user choose the folder to inspect
default_folder = Path.cwd() / "Test_Files"
folder_path = st.text_input(
     "📁 Folder to scan",
     value=str(default_folder),
     help="Choose your test folder first. We will only inspect files in this folder."
)

#Scan the selected folder and collect file information
folder = Path(folder_path)

if folder.exists() and folder.is_dir():

    # scan files inside the selected folder and all its subfolders
    files = [
        item 
        for item in folder.rglob("*")
        if item.is_file()
    ]


    file_rows = []
    for file in files:
        # Determine a category from the file extension
        extension = file.suffix.lower()

        if extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
            category = "Images"
        elif extension in [".pdf", ".doc", ".docx", ".txt", ".md"]:
            category = "Documents"
        elif extension in [".mp4", ".mov", ".mkv", ".avi"]:
            category = "videos"
        elif extension in [".mp3", ".wav", ".m4a", ".flac"]:
            category = "Audio"
        elif extension in [".zip", ".rar", ".7z", ".tar"]:
            category = "Archives"
        elif extension in [".csv", ".xlsx", ".xls"]:
            category = "Spreadsheets"
        else:
            category = "Others"

        # Store file name, category, entension, and size or the dashboard 
        file_rows.append({
            "File name": file.name,
            "Category": category,
            "Extension": extension if extension else "No extension",
            "Size (KB)": round(file.stat().st_size / 1024, 2)
        })


    # Convert collected information into a table 
    df = pd.DataFrame(file_rows)

   
    # Display colorful summary cards with custom HTML and CSS
    st.markdown("""
    <style>
    .category-card {
        padding: 20px;
        border-radius: 18px;
        color: white;
        min-height: 135px;
        box-shadow: 0 6px 18px rgba(50, 30, 90, 0.12);
        margin-bottom: 12px;
    }
    .category-card h4 {
        color: white;
        margin: 0;
        font-size: 17px;
    }
    .category-card h2 {
        color: white;
        margin: 12px 0 4px 0;
        font-size: 32px;
    }
    .category-card p {
        color: white;
        margin: 0;
        opacity: 0.9;
    }
    </style>
    """, unsafe_allow_html=True)

    # Show the main dashboard statistics
    total_files = len(df)
    total_size = df["Size (KB)"].sum() if total_files else 0
    total_categories = df["Category"].nunique() if total_files else 0

    st.subheader("✨ Your File Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="category-card" style="background: linear-gradient(135deg,#7657E8,#B06AF3);">
            <h4>📁 Total Files</h4>
            <h2>{total_files}</h2>
            <p>Files scanned</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="category-card" style="background: linear-gradient(135deg,#008F95,#35C6A5);">
            <h4>💾 Total Storage</h4>
            <h2>{total_size:.1f} KB</h2>
            <p>Combined file size</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="category-card" style="background: linear-gradient(135deg,#F05A8A,#FF9B76);">
            <h4>🎨 Categories</h4>
            <h2>{total_categories}</h2>
            <p>File types detected</p>
        </div>
        """, unsafe_allow_html=True)

    # Show a colorful card for each file category
    st.subheader("🗂️ File Categories")

    category_colors = {
        "Images": "#4776E6",
        "Documents": "#8E44AD",
        "Videos": "#E84393",
        "Audio": "#E67E22",
        "Archives": "#16A085",
        "Spreadsheets": "#27AE60",
        "Others": "#546E7A"
    }

    if total_files:
        counts = df["Category"].value_counts()
        category_columns = st.columns(3)

        for index, (category, count) in enumerate(counts.items()):
            color = category_colors.get(category, "#546E7A")

            with category_columns[index % 3]:
                st.markdown(f"""
                <div class="category-card" style="background: linear-gradient(135deg,{color},{color}CC);">
                    <h4>📂 {category}</h4>
                    <h2>{count}</h2>
                    <p>{count / total_files * 100:.1f}% of all files</p>
                </div>
                """, unsafe_allow_html=True)

    # Smart Auto-Organize feature 
    st.subheader("🗂️ Smart Auto-Organize")

    if total_files:
        #Show the files and their destination folders before moving
        organize_preview = df[["File name", "Category"]].copy()

        organize_preview["Destination Folder"] = (
            organize_preview["Category"]
        )

        st.write("Preview: Files will be moved into these folders.")
        st.dataframe(
            organize_preview,
            width="stretch",
            hide_index=True 
        )

        #Ask for confirmation before moving files
        confirm_organize = st.checkbox(
            "I confirm that I want ti organize these files."
        )

        if st.button("🗂️ Organize Files"):
            if confirm_organize:
                moved_count = 0

                for _, row in df.iterrows():
                    file_name = row["File name"]
                    category = row["Category"]

                    source = folder / file_name
                    destination_folder = folder / category
                    destination = destination_folder / file_name

                    # Skip files that no longer exist
                    if not source.exists():
                        continue

                    # Create the category folder
                    destination_folder.mkdir(
                        parents=True,
                        exist_ok=True 
                    )

                    # Avoid overwritting an existing file
                    if destination.exists():
                        st.warning(
                            f"Skipped {file_name}:"
                            "file already exists in destination."
                        )
                        continue

                    #Move the file into its category folder
                    shutil.move(
                        str(source),
                        str(destination)
                    )

                    moved_count += 1
                
                st.success(
                    f"Successfully organized {moved_count} files!"
                )
                st.rerun()

            else:
                st.warning(
                    "Please confirm before organizing files."
                )

    # Duplicate File Detection
    st.subheader("🔍 Duplicate File Detection")

    # Create a dictionary to group files with identical content
    file_hashes = {}

    # Check every files in the scanned folder
    for file in files:
        try:
            # Create a SHA-256 hash using the file content
            file_hash = hashlib.sha256()

            with open(file, "rb") as file_object:
                #Read the file in small chunks to save memory
                for chunk in iter(lambda: file_object.read(4096), b""):
                    file_hash.update(chunk)

            # Store the file  path using its content hash
            file_hashes.setdefault(file_hash.hexdigest(), []).append(file)

        except OSError:
            # Skip files that cannot be accessed
            continue 
    
    # keep only groups containing more than ane file
    duplicate_groups = {
        file_hash: duplicate_files
        for file_hash, duplicate_files in file_hashes.items()
        if len(duplicate_files) > 1
    }

    # Display duplicate results
    if duplicate_groups:

        # Create a list to store duplicate file details
        duplicate_rows = []

        # Loop through each duplicate group
        for file_hash, duplicate_files in duplicate_groups.items():

            #Loop through files with identical content
            for duplicate_file in duplicate_files:

                #Store files detail in a dictionary
                duplicate_rows.append({
                    "File Name": duplicate_file.name,
                    "File Path": str(duplicate_file),
                    "Group": file_hash[:12],
                    "Size (KB)": round(
                        duplicate_file.stat().st_size / 1024, 2
                    )
                })

            # Convert duplicate information into a DataFrame
            duplicate_df = pd.DataFrame(duplicate_rows)

            #Display the number of duplicate groups and files
            st.warning(
                f"Found {len(duplicate_groups)} duplicate groups "
                f"containing {len(duplicate_rows)} files."
            )

            # Display duplicate files in a table
            st.dataframe(
                duplicate_df,
                width="stretch",
                hide_index=True 
            )
        else:
            # Show a message when no duplicate files are found
            st.success("🎉 No duplicate files found!")



    # Display the colorful category distribution chart
    st.subheader("📊 Files by Category")

    if total_files:
        category_counts = df["Category"].value_counts().reset_index()
        category_counts.columns = ["Category", "Count"]

        chart = px.pie(
            category_counts,
            names="Category",
            values="Count",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        chart.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title="File type"
        )
        st.plotly_chart(chart, width="stretch")

        # Search and view file details
        st.subheader("🔎 File Details")
        search = st.text_input("Search by file name")
        filtered_df = df[df["File name"].str.contains(search, case=False, na=False)]
        st.dataframe(filtered_df, width="stretch", hide_index=True)

        # Download the scan report
        csv_report = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download File Report",
            data=csv_report,
            file_name="file_scan_report.csv",
            mime="text/csv"
        )
    else:
        st.info("No files found in this folder yet. Add a few sample files and refresh.")

st.divider()

st.caption(
    "🛡️ Preview dashboard only: this version scans files "
    "and creates a report. It does not move, rename, or delete files."
)
