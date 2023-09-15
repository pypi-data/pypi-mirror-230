# -*- coding: utf-8 -*-
# Copyright 2018-2019 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This demo lets you to explore the Udacity self-driving car image dataset.
# More info: https://github.com/streamlit/demo-self-driving

import cv2

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


# Streamlit encourages well-structured code, like starting execution in a main() function.
def main():
    # Render the readme as markdown using st.markdown.
    # readme_text = 'readme'  # st.markdown(get_file_content_as_string("instructions.md"))

    # Once we have the dependencies, add a selector for the app mode on the sidebar.
    st.sidebar.title("What to do")
    app_mode = st.sidebar.selectbox("Choose the app mode",
                                    ["Run the app"])

    if app_mode == "Show instructions":
        st.sidebar.success('To continue select "Run the app".')
    elif app_mode == "Run the app":
        # readme_text.empty()
        run_the_app()


# This is the main app app itself, which appears when the user selects "Run the app".
def run_the_app():

    # To make Streamlit fast, st.cache allows us to reuse computation across runs.
    # In this common pattern, we download data from an endpoint only once.
    @st.cache
    def load_metadata(path):
        return pd.read_csv(path)

    # This function uses some Pandas magic to summarize the metadata Dataframe.
    @st.cache
    def create_summary(metadata):
        one_hot_encoded = pd.get_dummies(metadata[["filepath", "label"]], columns=["label"])
        summary = one_hot_encoded.groupby(["filepath"]).sum().rename(columns={
            "detected_barcode": "barcode",
            "detected_digits": "digits",
            "detected_stamp": "stamp"
        })
        return summary

    # An amazing property of st.cached functions is that you can pipe them into
    # one another to form a computation DAG (directed acyclic graph). Streamlit
    # recomputes only whatever subset is required to get the right answer!
    metadata = load_metadata("/ECIPs/ecips_testing/notebooks/demo/metadata.csv")
    summary = create_summary(metadata)

    combined = load_metadata("/ECIPs/ecips_testing/notebooks/demo/all-data.csv")
    # Uncomment these lines to peek at these DataFrames.
    st.write('## Metadata', combined, '## Summary', summary)

    # Draw the UI elements to search for objects (pedestrians, cars, etc.)
    selected_frame_index, selected_frame = frame_selector_ui(summary)
    if selected_frame_index is None:
        st.error("No frames fit the criteria. Please select different label or number.")
        return

    # Load the image
#     image_url = os.path.join(DATA_URL_ROOT, selected_frame)
    image = load_image(selected_frame)

    # Add boxes for objects on the image. These are the boxes for the ground image.
    boxes = metadata[metadata.filepath == selected_frame][["bbox", "label"]]
    row = combined[combined.filepath == selected_frame].iloc[0]
    draw_image_with_boxes(image, boxes, row, "Dangerous Mailpiece %i" % selected_frame_index,
                          "**filepath** " + str(selected_frame) + "  \n**site name** " +
                          str(row['site_name']) + "  \n**risk score** " +
                          str(row['overall_risk_score']))


# This sidebar UI is a little search engine to find certain object types.
def frame_selector_ui(summary):
    st.sidebar.markdown("# Frame")

    # The user can pick which type of object to search for.
    object_type = st.sidebar.selectbox("Search for which objects?", summary.columns, 2)

    # The user can select a range for how many of the selected objecgt should be present.
    min_elts, max_elts = st.sidebar.slider("How many %ss (select a range)?" % object_type, 0, 25, [0, 25])
    selected_frames = get_selected_frames(summary, object_type, min_elts, max_elts)
    if len(selected_frames) < 1:
        return None, None

    # Choose a frame out of the selected frames.
    selected_frame_index = st.sidebar.slider("Choose a frame (index)", 0, len(selected_frames) - 1, 0)

    # Draw an altair chart in the sidebar with information on the frame.
    objects_per_frame = summary.loc[selected_frames, object_type].reset_index(drop=True).reset_index()
    chart = alt.Chart(objects_per_frame, height=120).mark_area().encode(
        alt.X("index:Q", scale=alt.Scale(nice=False)),
        alt.Y("%s:Q" % object_type))
    selected_frame_df = pd.DataFrame({"selected_frame": [selected_frame_index]})
    vline = alt.Chart(selected_frame_df).mark_rule(color="red").encode(x="selected_frame")
    st.sidebar.altair_chart(alt.layer(chart, vline))

    selected_frame = selected_frames[selected_frame_index]
    return selected_frame_index, selected_frame


# Select frames based on the selection in the sidebar
@st.cache(hash_funcs={np.ufunc: str})
def get_selected_frames(summary, label, min_elts, max_elts):
    return summary[np.logical_and(summary[label] >= min_elts, summary[label] <= max_elts)].index


def show_crop(img, bbox, bar_w, bar_h, dig_w, dig_h):
    if bbox is not None:
        ratio = [img.shape[0] / bar_w, img.shape[1] / bar_h]
        bbox = ((bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2), (bbox[2], bbox[3]), bbox[4])
        box = cv2.boxPoints(bbox)
        box[:, 0] *= ratio[1]
        box[:, 1] *= ratio[0]
        box = np.int0(box)

        src_pts = box.astype("float32")

        # Get height and width of barcode
        height = int(bbox[1][1] * ratio[1])
        width = int(bbox[1][0] * ratio[0])

        # corrdinate of the points in box points after the rectangle has been
        # straightened
        dst_pts = np.array([[0, height - 1],
                            [0, 0],
                            [width - 1, 0],
                            [width - 1, height - 1]], dtype="float32")

        # the perspective transformation matrix
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)

        # directly warp the rotated rectangle to get the straightened rectangle
        img = cv2.warpPerspective(img, M, (width, height))
        img = cv2.resize(img, (dig_w, dig_h))

    else:
        print("no cropped image to show")
    return img


def results_summary(risky_row):
    risky_row['pvi'] = ''
    metadata = risky_row[['basename', 'filepath', 'ecip_ip', 'mpe_device_ip',
                          'mpe_device', 'site_name', 'site_type',
                          'dateProcessed']].to_frame()
    new_columns = metadata.columns.values
    new_columns = ['metadata']
    metadata.columns = new_columns

    detections = risky_row[['pvi', 'zipcode', 'package', 'stamp_count',
                            'barcode', 'bcr_data']].to_frame().reset_index()
    risk_scores = risky_row[['pvi_risk_score', 'zipcode_risk_score',
                             'package_risk_score', 'stamp_risk_score',
                             'barcode_risk_score',
                             'overall_risk_score']].to_frame().reset_index()
    results_df = pd.concat([detections, risk_scores], axis=1)
    new_columns = results_df.columns.values
    new_columns = ['model', 'detection', 'risk score', 'value']
    results_df.columns = new_columns
    results_df = results_df.set_index('model')

    return metadata, results_df


# Draws an image with boxes overlayed to indicate the presence of cars, pedestrians etc.
def draw_image_with_boxes(image, boxes, metadata, header, description):
    # Superpose the semi-transparent object detection boxes.    # Colors for the boxes
    LABEL_COLORS = {
        "detected_barcode": [255, 0, 0],
        "detected_stamp": [0, 255, 0],
        "detected_digits": [0, 0, 255],
    }
    image = cv2.resize(image, (1280, 1280))
    image_with_boxes = image.astype(np.float64)
    for _, (bbox, label) in boxes.iterrows():
        try:
            import ast
            bbox = ast.literal_eval(bbox)
            bbox = np.array(bbox)

            bbox = bbox.astype(np.float)

            if label != 'detected_digits':

                if label == 'detected_barcode':
                    bbox = bbox[0]
                    angle = bbox[4]
                else:
                    angle = 0

                bbox = ((bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2), (bbox[2], bbox[3]), angle)
                box = cv2.boxPoints(bbox)
                box = np.int0(box)

                image_with_boxes = cv2.drawContours(image_with_boxes.copy(), [box], -1, LABEL_COLORS[label], 2)
            else:
                bbox_bc = metadata['detected_barcode']

                img_crop = show_crop(image, bbox_bc, bar_w=1280, bar_h=1280, dig_w=1280, dig_h=1280)
#                 img_dig = show_bbox(img_crop, bbox_dig, model='digit')
                angle = 0
                image_with_boxes = img_crop
                bbox = ((bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2), (bbox[2], bbox[3]), angle)
                box = cv2.boxPoints(bbox)
                box = np.int0(box)

                image_with_boxes = cv2.drawContours(image_with_boxes.copy(), [box], -1, LABEL_COLORS[label], 2)

    #         image_with_boxes[int(ymin):int(ymax),int(xmin):int(xmax),:] += LABEL_COLORS[label]
    #         image_with_boxes[int(ymin):int(ymax),int(xmin):int(xmax),:] /= 2
        except Exception:
            pass

    st.header(header)
    metadata, results_df = results_summary(metadata)

    st.write('### Image Metadata', metadata)
    st.write('### Detections and Risk Scores', results_df)

    # Draw the header and image.
    st.markdown(description)
    st.image(image_with_boxes.astype(np.uint8), use_column_width=True)

#     st.image(image_with_boxes_dig.astype(np.uint8), use_column_width=True)


@st.cache(show_spinner=False)
def load_image(image):
    image = cv2.imread(image, cv2.IMREAD_COLOR)
    image = image[:, :, [2, 1, 0]]  # BGR -> RGB
    return image


if __name__ == "__main__":
    main()
