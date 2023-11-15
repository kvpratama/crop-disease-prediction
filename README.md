# Crop Disease Prediction Web App
#### Video Demo:  https://youtu.be/o4mBi-VXlFU

## Description:
This web app, built using Flask, allows users to predict crop diseases from images. It utilizes a machine learning model hosted on Hugging Face, which was trained on a dataset obtained from Kaggle. The main features include image uploading, predicting crop diseases, viewing prediction history, submitting feedback, and an admin page for managing user feedback.

## Features

- **Crop Disease Prediction:** Users can upload images of crops, and the web app predicts the likelihood of crop diseases using a pre-trained machine learning model.

- **Prediction History:** Users can view a history of their uploaded images alongside the corresponding predictions.

- **Feedback Submission:** Users can submit feedback if they believe the prediction is incorrect.

- **Admin Page:** Administrators can access an admin page to review user feedback about predictions.

## Dataset
The dataset used for training the machine learning model was sourced from Kaggle. It consists of images labeled with various crop diseases.

## Model Training
The machine learning model was trained on the dataset, and the resulting model was uploaded to the Hugging Face model repository.

## Web App
- The Flask web application allows users to upload images of crops.
- The uploaded images are sent to Hugging Face through the Gradio API to obtain predictions using the pre-trained model.

#### Predict Function
- Handles the prediction process for uploaded crop images.
- Upon receiving a POST request with an uploaded image, the function:
    - Checks for the presence of the image file.
    - Generates a timestamp, creates a new filename, and saves the file to the uploads folder.
    - Utilizes the Hugging Face Gradio API to obtain predictions for the uploaded image.
    - Inserts the image information, prediction, and JSON result into the database.
    - Extracts labels and confidences from the prediction result.
    - Renders the result page with the image, labels, and a chart displaying prediction confidences.
- Returns:
    - Renders the 'result.html' template with the prediction result.

#### History Page
- Displays the prediction history for the logged-in user.
- Retrieves and displays the user's uploaded images and their corresponding predictions from the database. Additionally, retrieves information about available classes for potential user's feedback.
- Returns:
    - Renders the 'history.html' template with the user's image history and available classes.

#### Detail Page
- Displays detailed information about a specific image prediction.
- If the request method is POST, retrieves the image details based on the provided image_id.
- Extracts information such as file path, labels, and confidences from the prediction result JSON.
- Renders the 'result.html' template with the detailed information.
- Returns:
    - Renders the 'result.html' template with the detailed information for the selected image.

#### Suggest function
- Handles user suggestions for correcting predictions.
- If the request method is POST, retrieves the image_id and suggested prediction from the form.
- Updates the database with the user-suggested prediction for the corresponding image_id.
- Redirects the user to the '/feedback' page.
- Returns:
    - Redirects to the '/feedback' page after processing the user suggestion.

#### User's Feedback
- Displays the feedback history for the logged-in user.
- Retrieves and displays images for which users have provided feedback, indicating a disagreement with the prediction.
- Only includes images with non-null values in the 'prediction_user' column.
- Returns:
    - Renders the 'feedback.html' template with the user's feedback history.

#### Admin's user's feedback page
- Displays the feedback history for all users (admin-only view).
- Retrieves and displays images for which users have provided feedback, indicating a disagreement with the prediction.
-Includes additional information such as the image path, original prediction, user-suggested prediction, and the username of the uploader.
-Returns:
    - Renders the 'feedback-users.html' template with the feedback history for all users.

## Design Choices
- Hugging Face Integration: Leveraging the Hugging Face model repository allows for easy model deployment and updates without the need to host the model locally.

- Gradio API: The use of Gradio simplifies the integration with the Hugging Face model and provides a user-friendly interface for predictions.

- Feedback System: Including a feedback system enables users to contribute to model improvement, enhancing the accuracy of predictions over time.

## Acknowledgments
- Kaggle for providing the dataset.
- Hugging Face for hosting the machine learning model.
