import streamlit as st
import cv2
import numpy as np
import os
from PIL import Image

# Global variables
drawing = False
ix, iy = -1, -1
bbox_coords = []
bbox_labels = []
img = None
img_copy = None

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, img, bbox_coords, bbox_labels

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img = img_copy.copy()
            cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 2)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 2)
        bbox_coords.append((ix, iy, x, y))
        label = st.session_state.get('selected_label', 'No label')
        bbox_labels.append(label)

def main():
    st.title("Image Annotation Tool")

    if 'labels' not in st.session_state:
        st.session_state['labels'] = []

    new_label = st.text_input("Enter a new label:")
    if st.button("Add Label"):
        if new_label and new_label not in st.session_state['labels']:
            st.session_state['labels'].append(new_label)

    if st.session_state['labels']:
        st.session_state['selected_label'] = st.selectbox("Select the label:", st.session_state['labels'])

    folder_path = st.text_input("Enter the folder path containing images:")

    if folder_path and os.path.isdir(folder_path):
        files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
        file_index = st.slider("Select image index:", 0, len(files) - 1, 0)

        if files:
            img_path = os.path.join(folder_path, files[file_index])
            image = Image.open(img_path)
            st.image(image, caption=files[file_index], use_column_width=True)

            if st.button("Annotate"):
                global img, img_copy, bbox_coords, bbox_labels, drawing, ix, iy
                img = cv2.imread(img_path)
                img_copy = img.copy()
                bbox_coords = []
                bbox_labels = []
                drawing = False

                cv2.namedWindow('image')
                cv2.setMouseCallback('image', draw_rectangle)

                while True:
                    cv2.imshow('image', img)
                    key = cv2.waitKey(1) & 0xFF

                    if key == ord('q'):
                        break
                    elif key == ord('c'):
                        if bbox_coords:
                            bbox_coords.pop()
                            bbox_labels.pop()
                            img = img_copy.copy()
                            for (ix, iy, x, y), label in zip(bbox_coords, bbox_labels):
                                cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 2)

                cv2.destroyAllWindows()

                if bbox_coords:
                    annotation_path = os.path.join(folder_path, os.path.splitext(files[file_index])[0] + ".txt")
                    annotations = []
                    for (ix, iy, x, y), label in zip(bbox_coords, bbox_labels):
                        x_center = (ix + x) / 2 / img.shape[1]
                        y_center = (iy + y) / 2 / img.shape[0]
                        width = (x - ix) / img.shape[1]
                        height = (y - iy) / img.shape[0]
                        label_id = st.session_state['labels'].index(label)
                        annotations.append(f"{label_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

                    with open(annotation_path, 'a') as f:
                        for annotation in annotations:
                            f.write(annotation + '\n')
                    st.success(f"Annotations saved for {files[file_index]}")

if __name__ == "__main__":
    main()
