import time
import os
from datetime import datetime

from hw_fault_simulation import set_pwm_duty_cycle, get_tacho_reading, \
    reset_all_faults, simulate_fan_stall, simulate_fan_degradation, \
    simulate_disconnected_tacho, simulate_disconnected_pwm, \
    set_tacho_noise_level


from logger import get_logger
from csv_logger import CsvLogger
import logging

logger = get_logger(log_level=logging.INFO)

# Default test configuration
PWM_CHANNEL = 0
TACHO_CHANNEL = 0
PWM_STABILIZATION_TIME = 1.0
RPM_TOLERANCE_PERCENT = 10
NUM_SAMPLES = 3

def validate_pwm_vs_tacho(
        pwm_value: int,
        expected_rpm: int,
        tolerance_percent: int = RPM_TOLERANCE_PERCENT,
        stabilization_time: float = PWM_STABILIZATION_TIME,
        number_samples: int = NUM_SAMPLES,
        csv_logger=None
) -> dict:
    """
    Validates the relationship between PWM setting and tachometer reading.

    Test Specification
    ------------------
    This function sets a PWM value, waits for the fan to stabilize and then measures
    the tachometer signal to verify it's within expected range.

    :param pwm_value: 'PASS' or 'FAIL'
    :param error_message: List of error mesages if result is 'FAIL'
    :param pwm_value: The PWM value tested
    :param measured_rmp: The measured RPM
    :param expected_rpm: The expected RPM

    """
    # Validate test parameters before executing any step.
    if pwm_value < 0 or pwm_value > 100:
        result = {"result": "FAIL", "error_message": "Invalid PWM value", "pwm_value": pwm_value, "measured_rpm": None, "expected_rpm": expected_rpm}
        if csv_logger:
            csv_logger.log_row(pwm_value, expected_rpm, '', 'FAIL')
        return result
    if expected_rpm is None or expected_rpm < 0:
        result = {"result": "FAIL", "error_message": "Invalid expected RPM", "pwm_value": pwm_value, "measured_rpm": None, "expected_rpm": expected_rpm}
        if csv_logger:
            csv_logger.log_row(pwm_value, expected_rpm, '', 'FAIL')
        return result
    if tolerance_percent < 0 or tolerance_percent > 100:
        result = {"result": "FAIL", "error_message": "Invalid tolerance percentage", "pwm_value": pwm_value, "measured_rpm": None, "expected_rpm": expected_rpm}
        if csv_logger:
            csv_logger.log_row(pwm_value, expected_rpm, '', 'FAIL')
        return result
    if stabilization_time < 0:
        result = {"result": "FAIL", "error_message": "Invalid stabilization time", "pwm_value": pwm_value, "measured_rpm": None, "expected_rpm": expected_rpm}
        if csv_logger:
            csv_logger.log_row(pwm_value, expected_rpm, '', 'FAIL')
        return result
    if number_samples < 1:
        result = {"result": "FAIL", "error_message": "Invalid number of samples", "pwm_value": pwm_value, "measured_rpm": None, "expected_rpm": expected_rpm}
        if csv_logger:
            csv_logger.log_row(pwm_value, expected_rpm, '', 'FAIL')
        return result
    
    # Set PWM duty cycle
    set_pwm_duty_cycle(PWM_CHANNEL, pwm_value)

    # Wait for fan speed to stabilize
    logger.debug(f"Waiting {stabilization_time}s for fan speed to stabilize...")
    time.sleep(stabilization_time)

    # Take multiple RPM measurements and average them
    rpm_readings = []
    for i in range(number_samples):
        logger.debug(f"Reading tachometer - Sample {i + 1}...")
        rpm_readings.append(get_tacho_reading(TACHO_CHANNEL))
        time.sleep(0.1)  # Short delay between readings

    # Calculate average and take the integer part
    measured_rpm = int(sum(rpm_readings) / len(rpm_readings))

    # Prepare results dictionary
    results = {
        "result": "PASS",
        "error_message": [],
        "pwm_value": pwm_value,
        "measured_rpm": measured_rpm,
        "expected_rpm": expected_rpm
    }

    # Check for fan stall condition (PWM active but RPM low)
    # Run test and continue
    if pwm_value >= 20 and measured_rpm < 100:
        results["result"] = "FAIL"
        msg = f"ERROR: Fan stall detected at PWM {pwm_value}%"
        results["error_message"].append(msg)
        logger.error(msg)

    # Avoid division by 0
    if expected_rpm > 0:
        deviation = ((measured_rpm - expected_rpm) / expected_rpm) * 100
        if abs(deviation) <= tolerance_percent:
            results["result"] = "PASS"
        else:
            results["result"] = "FAIL"


    return results

def run_validation_sweep(
        pwm_min: int,
        pwm_max: int,
        pwm_step: int,
        expected_rpm_map: dict[int, int],
        tolerance_percent: int = RPM_TOLERANCE_PERCENT,
        stabilization_time: float = PWM_STABILIZATION_TIME,
        number_samples: int = NUM_SAMPLES,
        csv_logger=None
) -> tuple[int, dict]:
    """
    Run validation across a range of PWM values.

    :param pwm_min: Minimum PWM value to test.
    :param pwm_max: Maximum PWM value to test.
    :param pwm_step: PWM step size
    :param expected_rpm_map: Dictionary mapping PWM values to expected RPM.

    :returns: number of failures, test results dictionary
    """
    failures = 0
    results = {}

    logger.info("\n\nPWM-Tachometer Validation Sweep")
    logger.info("\n===============================")

    for pwm in range(pwm_min, pwm_max + 1, pwm_step):
        try:
            expected_rpm = expected_rpm_map.get(pwm)
        except KeyError:
            logger.error(f"Invalid expected RPM for PWM {pwm}%. Expected RPM map: {expected_rpm_map}")
            results[pwm] = {"result": "FAIL", "error_message": [f"Invalid expected RPM: {pwm}"]}
        else:
            result = validate_pwm_vs_tacho(
                pwm_value=pwm,
                expected_rpm=expected_rpm,
                tolerance_percent=tolerance_percent,
                stabilization_time=stabilization_time,
                number_samples=number_samples,
                csv_logger=csv_logger
            )
            results[pwm] = result

        # Print results
        logger.info(f"Result: {result['result']}, PWM: {pwm}%, Measured RPM: {result['measured_rpm']}, Expected RPM: {expected_rpm}")
        if csv_logger:
            csv_logger.log_row(pwm, expected_rpm, result['measured_rpm'], result["result"])

        if result["result"] == "FAIL":
            failures += 1

    logger.info("===============================")
    logger.info(f"Test complete: {failures} failures")

    return failures, results


if __name__ == "__main__":
    # Input mapping between PWM and expected tachometer RPM
    pwm_tacho_map = {
        0: 0,     # Fan stopped
        20: 800,  # Minimum speed (cold start threshold)
        40: 1600,
        60: 2400,
        80: 3200,
        100: 4000    # Maximum speed
    }

    # Reset all faults
    reset_all_faults()

    # simulate_disconnected_pwm()
    # simulate_disconnected_tacho()
    # simulate_fan_degradation(0.12)  # Simulate 12% degradation
    # simulate_fan_stall()  # Ensure fan stall is disabled
    set_tacho_noise_level(0.12)  # Set noise level to 5%

    # CSV setup
    # Keep the CSV logger outside to enable mocking
    csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'csv_logs')
    csv_logger = CsvLogger(csv_dir)

    # Run full test
    failures, results = run_validation_sweep(
        pwm_min=0,
        pwm_max=100,
        pwm_step=20,
        expected_rpm_map=pwm_tacho_map,
        csv_logger=csv_logger
    )
