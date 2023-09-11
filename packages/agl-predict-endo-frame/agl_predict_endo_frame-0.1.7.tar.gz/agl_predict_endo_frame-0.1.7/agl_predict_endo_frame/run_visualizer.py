# run_visualize.py

import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="Visualize Predictions")
    parser.add_argument("--file", type=str, help="Path to JSON file containing predictions", required=True)
    args = parser.parse_args()

    # Replace this with the path where prediction_visualizer.py resides
    streamlit_script_path = "prediction_visualizer.py"
    
    # Using subprocess to run the Streamlit command
    subprocess.run(f'streamlit run {streamlit_script_path} -- --file {args.file}', shell=True)

if __name__ == "__main__":
    main()

