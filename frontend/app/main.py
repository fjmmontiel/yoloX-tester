import streamlit as st
import requests
import pandas as pd
import altair as alt
import os

# Set the page config to set up the layout and title
st.set_page_config(page_title='Object Detection APP', layout='wide')

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<h1>Object Detection App</h1>", unsafe_allow_html=True)

api_url = os.environ.get("API_URL")

# Define the navigation for different views
tab1, tab2, tab3 = st.tabs(["Data Processing", "Sample examinator", "Data summary"])

with tab1:
    # Layout for Data Processing
    col1, col2 = st.columns([1, 2])

    with col1:
        file = st.file_uploader("Select your image", type=["jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff"], key='file_uploader')
        
        # Button to trigger the upload process
        if st.button("Upload Image"):
            if file is not None:
                with st.spinner('Processing... Please wait'):
                    # Sending the image to the backend for processing
                    response = requests.post(f"http://{api_url}/upload-image/", files={"file": (file.name, file.getvalue())})
                    
                    if response.status_code == 200:
                        # Display the processed image from the backend in col2
                        col2.image(response.content, caption="Processed Image", use_column_width=True)
                    else:
                        # Display error if something went wrong during processing
                        col2.error("Failed to process image")



with tab2:
    col1, col2 = st.columns([1,2])

    # A button in col1 to manually trigger a refresh of the image list
    with col1:
        if st.button('Refresh Images'):
            # Clear existing image data from session state when button is pressed
            if 'images' in st.session_state:
                del st.session_state['images']
            
            # Fetch new image data from the backend and update the session state
            new_images = requests.get(f"http://{api_url}/list-images").json()
            st.session_state.images = new_images

    # Display images if available in col2
    with col1:
        if 'images' in st.session_state and st.session_state.images:
            # Generate list of image names for selection
            image_names = ["Select an image"] + [img["originalFileName"] for img in st.session_state.images]
            selected_image_name = st.selectbox("Select an image to view", image_names)

            # Display the selected image
            if selected_image_name and selected_image_name != "Select an image":
                selected_image = next((img for img in st.session_state.images if img["originalFileName"] == selected_image_name), None)
                if selected_image:
                    selected_image_id = selected_image["id"]
                    response = requests.get(f"http://{api_url}/get-image/{selected_image_id}")
                    col2.image(response.content, caption="Selected Image", use_column_width=True)
                    if response.status_code == 200:
                        # Fetch and display histogram
                        histogram_response = requests.get(f"http://{api_url}/get-histogram-data/{selected_image_id}")
                        if histogram_response.status_code == 200:
                            histogram_data = histogram_response.json()
                            df = pd.DataFrame.from_dict(histogram_data, orient='index', columns=['Count'])
                            st.write("Histogram of Predicted Classes:")
                            st.bar_chart(df)
                        else:
                            st.error("Failed to fetch histogram data")


with tab3:
    col1, col2 = st.columns([1, 2])

    # Fetch summary data when entering tab3
    summary_response = requests.get(f"http://{api_url}/get-summary")
    
    if summary_response.status_code == 200:
        summary_data = summary_response.json()
        
        if summary_data:  # Check if the data is not empty
            # Convert the summary data to a DataFrame
            image_summaries = pd.DataFrame(summary_data)
            
            if not image_summaries.empty:
                # Explode the crops field to get detailed crop data
                crops = image_summaries.explode('crops').reset_index(drop=True)
                
                if not crops.empty:
                    crops_details = pd.json_normalize(crops['crops'])
                    
                    if not crops_details.empty:
                        # Create a dashboard of different graphics
                        with col1:
                            st.write("## Distribution of Classes")
                            class_distribution = crops_details['class'].value_counts().sort_values(ascending=False)
                            class_distribution_df = class_distribution.reset_index()
                            class_distribution_df.columns = ['Class', 'Count']

                            class_chart = alt.Chart(class_distribution_df).mark_bar().encode(
                                x=alt.X('Class', sort=None),
                                y='Count'
                            )

                            st.altair_chart(class_chart, use_container_width=True)

                            st.write("## Average Confidence Levels per Class")
                            confidence_levels = crops_details.groupby('class')['confidence'].mean().reset_index()
                            confidence_levels.columns = ['Class', 'Average Confidence']

                            confidence_chart = alt.Chart(confidence_levels).mark_bar().encode(
                                x=alt.X('Class', sort=None),
                                y='Average Confidence'
                            )

                            st.altair_chart(confidence_chart, use_container_width=True)

                        with col2:
                            st.write("## Number of Predictions per Image")
                            num_predictions = image_summaries.set_index('originalFileName')['imageSummary'].apply(lambda x: sum(x.values()))
                            num_predictions_df = num_predictions.reset_index()
                            num_predictions_df.columns = ['Image', 'Number of predictions']

                            predictions_chart = alt.Chart(num_predictions_df).mark_bar().encode(
                                x=alt.X('Image', sort=None),
                                y='Number of predictions'
                            )

                            st.altair_chart(predictions_chart, use_container_width=True)

                            st.write("## Confidence Summary Statistics")
                            confidence_distribution = crops_details['confidence']
                            confidence_summary = confidence_distribution.describe().reset_index()
                            confidence_summary.columns = ['Statistic', 'Value']
                            st.table(confidence_summary)
                    else:
                        st.warning("Crops details are empty.")
                else:
                    st.warning("Crops data is empty.")
            else:
                st.warning("Image summaries are empty.")
        else:
            st.warning("No images were predicted yet!")
    else:
        st.error("Failed to fetch summary data")
