import time

from hw_fault_simulation import set_pwm_duty_cycle, get_tacho_reading, \
    reset_all_faults, simulate_fan_stall, simulate_fan_degradation, \
    simulate_disconnected_tacho, simulate_disconnected_pwm, \
    set_tacho_noise_level

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
        number_samples: int = NUM_SAMPLES
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
    print("\nValidating PWM vs Tachometer")
    # Validate test parameters before executing any step.
    if pwm_value < 0 or pwm_value > 100:
        return {"result": "FAIL", "error_message": "Invalid PWM value"}
    if expected_rpm is None or expected_rpm < 0:
        return {"result": "FAIL", "error_message": "Invalid expected RPM"}
    if tolerance_percent < 0 or tolerance_percent > 100:
        return {"result": "FAIL", "error_message": "Invalid tolerance percentage"}
    if stabilization_time < 0:
        return {"result": "FAIL", "error_message": "Invalid stabilization time"}
    if number_samples < 1:
        return {"result": "FAIL", "error_message": "Invalid number of samples"}
    
    # Set PWM duty cycle
    set_pwm_duty_cycle(PWM_CHANNEL, pwm_value)

    # Wait for fan speed to stabilize
    print(f"Waiting {stabilization_time}s for fan speed to stabilize...")
    time.sleep(stabilization_time)

    # Take multiple RPM measurements and average them
    rpm_readings = []
    for _ in range(number_samples):
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
        print(msg)

    # Avoid division by 0
    if expected_rpm > 0:
        deviation = ((measured_rpm - expected_rpm) / expected_rpm) * 100
        if abs(deviation) <= tolerance_percent:
            results["result"] = "PASS"
        else:
            results["result"] = "FAIL"

    # Print results
    print(f"Result: {results['result']}, PWM: {pwm_value}%, Measured RPM: {measured_rpm}, Expected RPM: {expected_rpm}")

    return results

def run_validation_sweep(
        pwm_min: int,
        pwm_max: int,
        pwm_step: int,
        expected_rpm_map: dict[int, int],
        tolerance_percent: int = RPM_TOLERANCE_PERCENT,
        stabilization_time: float = PWM_STABILIZATION_TIME,
        number_samples: int = NUM_SAMPLES
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

    print("\n\nPWM-Tachometer Validation Sweep")
    print("===============================")

    for pwm in range(pwm_min, pwm_max + 1, pwm_step):
        try:
            expected_rpm = expected_rpm_map.get(pwm)
        except KeyError:
            results[pwm] = {"result": "FAIL",
                            "error_message": [f"Invalid expected RPM: {pwm}"]}
            
        result = validate_pwm_vs_tacho(
            pwm_value=pwm,
            expected_rpm=expected_rpm,
            tolerance_percent=tolerance_percent,
            stabilization_time=stabilization_time,
            number_samples=number_samples
        )
        results[pwm] = result

        if result["result"] == "FAIL":
            failures += 1

    print("===============================")
    print(f"Test complete: {failures} failures")

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

    simulate_disconnected_pwm()
    #simulate_disconnected_tacho()
    #simulate_fan_degradation()
    #simulate_fan_stall()
    #set_tacho_noise_level()

    # Run full test
    failures, results = run_validation_sweep(
        pwm_min=0,
        pwm_max=100,
        pwm_step=20,
        expected_rpm_map=pwm_tacho_map
    )