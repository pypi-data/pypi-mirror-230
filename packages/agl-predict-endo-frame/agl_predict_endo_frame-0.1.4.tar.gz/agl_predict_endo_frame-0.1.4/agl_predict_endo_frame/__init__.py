# agl_visualization/__init__.py
import argparse

def run_visualization():
    from .prediction_visualizer import main
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Visualize Predictions")
    parser.add_argument("--file", type=str, help="Path to JSON file containing predictions", required=True)
    args = parser.parse_args()  # assuming your Streamlit script is named visualize.py

    main(args.file)