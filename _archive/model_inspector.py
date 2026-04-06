import os
import joblib
import pandas as pd
from datetime import datetime

# Get the models directory
models_dir = '/mnt/c/projects/stocker/data/models/'

# Get all model files and sort by modification time (most recent first)
model_files = [(f, os.path.getmtime(os.path.join(models_dir, f))) 
               for f in os.listdir(models_dir) if f.endswith('.joblib')]
model_files.sort(key=lambda x: x[1], reverse=True)

if model_files:
    # Get the most recent model
    most_recent_model_file = model_files[0][0]
    most_recent_model_path = os.path.join(models_dir, most_recent_model_file)
    
    print(f"Loading most recent model: {most_recent_model_file}")
    print(f"Last modified: {datetime.fromtimestamp(model_files[0][1])}")
    
    # Load the model
    model = joblib.load(most_recent_model_path)
    
    print("\nModel type:", type(model))
    
    # Try to access different model attributes to find feature information
    if hasattr(model, 'feature_names_in_'):
        print("\nFeature names from feature_names_in_:")
        for feature in model.feature_names_in_:
            print(f"  - {feature}")
    
    # For some scikit-learn models that have feature_importances_
    if hasattr(model, 'feature_importances_'):
        print("\nFeature importances:")
        if hasattr(model, 'feature_names_in_'):
            for feature, importance in zip(model.feature_names_in_, model.feature_importances_):
                print(f"  - {feature}: {importance}")
    
    # Look for other common attributes that might contain feature information
    for attr in ['features_', 'feature_names', 'named_steps']:
        if hasattr(model, attr):
            print(f"\nFound attribute: {attr}")
            print(model.__getattribute__(attr))
    
    # For pipeline models
    if hasattr(model, 'steps'):
        print("\nModel is a pipeline with steps:")
        for step_name, step_obj in model.steps:
            print(f"  - {step_name}: {type(step_obj)}")
            # Check if this step has feature names
            if hasattr(step_obj, 'feature_names_in_'):
                print(f"    Features for {step_name}:")
                for feature in step_obj.feature_names_in_:
                    print(f"      - {feature}")
                    
    # Let's also look at one more model for comparison
    if len(model_files) > 1:
        print("\n\n" + "="*50)
        print("Loading another model for comparison:")
        second_model_file = model_files[1][0]
        second_model_path = os.path.join(models_dir, second_model_file)
        print(f"Model file: {second_model_file}")
        
        second_model = joblib.load(second_model_path)
        
        if hasattr(second_model, 'feature_names_in_'):
            print("\nFeature names from second model:")
            for feature in second_model.feature_names_in_:
                print(f"  - {feature}")
else:
    print("No .joblib files found in the models directory.")