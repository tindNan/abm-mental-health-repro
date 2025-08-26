#!/usr/bin/env python3
"""
Main entry point for the Nairobi Youth Mental Health ABM Dashboard.

Run with:
    uv run python main.py

Or install dependencies first:
    uv pip install -r requirements.txt
    uv run python main.py
"""

import sys
import subprocess
import os


def main():
    """Launch the Streamlit dashboard."""

    print("🧠 Starting Nairobi Youth Mental Health ABM Dashboard...")
    print("-" * 50)
    print("This model simulates mental health transmission among youth")
    print("aged 15-24 in Nairobi, Kenya using agent-based modeling.")
    print("-" * 50)
    print("\nLaunching dashboard in your browser...")
    print("\nTo stop the server, press Ctrl+C\n")

    # Run the streamlit app
    streamlit_args = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/dashboard/app.py",
        "--server.port",
        "8501",
        "--server.address",
        "localhost",
        "--browser.gatherUsageStats",
        "false",
        "--theme.base",
        "light",
        "--theme.primaryColor",
        "#FF6B6B",
    ]

    try:
        subprocess.run(streamlit_args)
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard stopped successfully.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        print("\nPlease make sure you have installed dependencies:")
        print("  uv pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
