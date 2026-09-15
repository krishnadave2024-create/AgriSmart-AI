# Training on Google Colab

To train the multi-crop disease detection model quickly (in under 1 hour) using a GPU, use the Google Colab workflow.

## Steps to Train
1. Open Google Colab (colab.research.google.com).
2. Click **Upload** and upload `docs/AgriSmart_AI_Colab_Training.ipynb`.
3. In Colab, go to **Runtime > Change runtime type** and select **T4 GPU**.
4. Zip your entire local project directory (excluding the massive `data/external` raw images).
5. Upload the ZIP into the Colab file explorer.
6. Run the cells sequentially. The notebook will automatically download the dataset natively at ultra-high speeds, run preflight leakage checks, train the model, evaluate it on the hold-out test set, and prompt you to download the trained `colab_artifacts.zip`.

## What You Get
Inside `colab_artifacts.zip`, you will find:
- `best_model.pth`: The highest validation F1 checkpoint.
- `training_history.json`: Loss and accuracy curves.
- Metrics and Confusions matrices for analysis.

Place `best_model.pth` back into your local `model/artifacts/plant_disease_multiclass/` directory when finished.
