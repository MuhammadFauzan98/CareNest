from ml_model import health_predictor

if __name__ == "__main__":
    print("Training health risk prediction model...")
    health_predictor.train_model()
    print("Model training completed!")