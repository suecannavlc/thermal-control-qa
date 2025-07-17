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