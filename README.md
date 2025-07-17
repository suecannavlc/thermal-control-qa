# thermal-control-qa

## Setup

This project uses pip as the dependency manager. To install dependencies, run:

```
pip install -r requirements.txt
```

## Usage

Run the main test script:

```
python tacho_test.py
```

## CLI Usage

You can also run tests and configure faults using the command-line interface:

```
python tacho_cli.py --help
```

Example usage:

```
python tacho_cli.py --pwm-min 0 --pwm-max 100 --pwm-step 20 --tolerance 10 --stabilization 1.0 --samples 3 --fan-stall --fan-degradation 0.12 --disconnected-tacho --noise 0.05
```

All parameters can be set interactively via command-line options. See `--help` for details.

## Project Structure

- `tacho_test.py`: Main test runner
- `hw_fault_simulation.py`: Hardware simulation and fault injection
- `logger.py`: Logging setup
- `csv_logger.py`: CSV logging utility
- `requirements.txt`: Python dependencies
- `csv_logs/`: Output folder for CSV logs
- `tacho_cli.py`: Command-line interface for running and configuring tests