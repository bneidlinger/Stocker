#!/usr/bin/env python3
import os
import sys


def export_project_files(project_dir, output_file):
    """Export only the relevant project Python files to a markdown file."""

    # Define the exact files we want to include, in the desired order
    target_files = [
        "main.py",
        "config.py",
        "data/data_fetcher.py",
        "trading/backtester.py",
        "trading/strategies/sma_cross.py",
        "trading/strategies/rsi_oscillator.py",
        "trading/strategies/volatility_breakout.py",
        "trading/strategies/fake_moon_strategy.py",
        "trading/strategies/real_moon_strategy.py",
        "trading/strategies/macd_strategy.py",
        "trading/strategies/bollinger_bands_strategy.py",
        "trading/strategies/ichimoku_strategy.py",
        "trading/strategies/donchian_channel_strategy.py",
        "trading/strategies/day_of_week_strategy.py",
        "trading/ml/__init__.py",
        "trading/ml/features.py",
        "trading/ml/models.py",
        "trading/ml/service.py",
        "gui/app.py",
        "gui/widgets/dot_matrix.py",
        "gui/widgets/vintage_indicators.py"
    ]

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("# Stock Trading App Code Export\n\n")

        for file_path in target_files:
            full_path = os.path.join(project_dir, file_path)

            # Check if the file exists
            if not os.path.exists(full_path):
                print(f"Warning: File not found: {file_path}")
                continue

            out.write(f"## {file_path}\n\n")
            out.write("```python\n")

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    out.write(content)
                    # Ensure there's a newline at the end
                    if not content.endswith('\n'):
                        out.write('\n')
            except Exception as e:
                out.write(f"# Error reading file: {str(e)}\n")

            out.write("```\n\n")

        print(f"Successfully exported the specified Python files to {output_file}")


def main():
    # Get the directory where this script is executed
    project_dir = os.getcwd()

    # Output file path
    output_file = os.path.join(project_dir, "stock_trading_app_code.md")

    # Export only the relevant files
    export_project_files(project_dir, output_file)


if __name__ == "__main__":
    main()