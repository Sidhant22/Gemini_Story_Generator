import streamlit as st
from story_generator import generate_story, narrate_story
# To process the images (uploaded)
from PIL import Image
st.title("Story Generator with Google Generative AI")
st.markdown("Upload images (1-10) and generate a story based on them and its narration.")


# Sidebar for image upload
with st.sidebar:
    st.header("Controls")
    uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    # Story genere:
    story_style = st.selectbox("Select Story Style", ["Adventure", "Mystery", "Fantasy", "Sci-Fi", "Horror"])

    # Button to generate story
    generate_button = st.button("Generate Story and Narration", type="primary")

# Main logic:
if generate_button:
    if not uploaded_files:
        st.warning("Please upload at least one image.")
    elif len(uploaded_files) > 10:
        st.warning("You can upload a maximum of 10 images.")
    else:
        with st.spinner("Generating the story... this may take a few moments."):
            try:
                pil_images = [Image.open(uploaded_file) for uploaded_file in uploaded_files]
                # Before sendingthese images we will display them the selection in column format
                st.subheader("Uploaded Images:")
                image_cols = st.columns(len(pil_images))

                for i, image in enumerate(pil_images):
                    with image_cols[i]:
                        st.image(image, use_container_width=True)
                # Generate story
                story_text = generate_story(pil_images, story_style)
                # If there is any issue while generation display an error message
                if "Error" in story_text or "Failed" in story_text or "API key" in story_text:
                    st.error("Failed to generate story. Please try again.")
                
                else:
                    st.subheader(f"Generated Story ({story_style}):")
                    st.success(story_text)

                # Audio narration:
                st.subheader("Story Narration:")
                audio_file = narrate_story(story_text)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")
                else:
                    st.error("Failed to generate narration. Please try again.")

            except Exception as e:
                st.error(f"An error occurred while processing images: {e}")
