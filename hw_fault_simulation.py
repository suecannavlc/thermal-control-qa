"""
This module provides HW simulation function with several available faults.
"""

import random

from logger import get_logger
import logging

logger = get_logger(log_level=logging.DEBUG)

_current_pwm = 0

# Global fault configuration
_fan_stall_enabled = False
_fan_degradation = 0.0
_tacho_disconnected = False
_pwm_disconnected = False
_noise_level = 0.0

# Regular functions without faults
def _set_pwm_duty_cycle(channel: int, duty_cycle: int) -> None:
    """
    Simulate setting PWM duty cycle without faults
    """
    global _current_pwm
    _current_pwm = duty_cycle
    logger.debug(f"Setting PWM channel {channel} to {duty_cycle}%")

def _get_tacho_reading(channel: int) -> int:
    """
    Simulate reading tachometer without RPM faults
    """
    if _current_pwm < 20:
        return 0
    
    rpm = _current_pwm * 40
    return rpm

# Modified HW simulation functions including faults
def get_tacho_reading(channel: int) -> int:
    """
    Get tachometer reading with simulated faults
    """
    global _current_pwm

    # If the fan is stalled or the tacho is disconnected return 0
    if _fan_stall_enabled or _tacho_disconnected:
        logger.error(f"[FAULT] Fan stalled or tachometer disconnected")
        return 0
    
    base_rpm = _get_tacho_reading(channel=channel)
    logger.debug(f"Base RPM: {base_rpm}")

    # Apply degradation
    if _fan_degradation > 0:
        base_rpm = base_rpm * (1 - _fan_degradation)

    # Apply noise
    std_dev = base_rpm * _noise_level
    noise = random.gauss(0, std_dev)
    logger.debug(f"Noise: {noise}")

    return max(0, int(base_rpm + noise))

def set_pwm_duty_cycle(channel: int, duty_cycle: int) -> None:
    """
    Set PWM duty cycle with simulated faults
    """
    global _current_pwm

    if _pwm_disconnected:
        logger.error(f"[FAULT] PWM signal disconnected")
        return
    
    _set_pwm_duty_cycle(channel=channel, duty_cycle=duty_cycle)

# Functions to configure faults
def simulate_fan_stall(enable: bool = True) -> None:
    """
    Simulate a fan stall condition
    """
    global _fan_stall_enabled
    _fan_stall_enabled = enable
    logger.info(f"Fan stall simulation {'enabled' if enable else 'disabled'}.")

def simulate_fan_degradation(degradation_level: float = 0.3) -> None:
    """
    Simulate fan degradation
    """
    global _fan_degradation
    if degradation_level < 0.0 or degradation_level > 1.0:
        raise ValueError("Degradation level must be between 0.0 and 1.0")
    
    _fan_degradation = degradation_level
    logger.info(f"Fan degradation set to {degradation_level*100:.1f}%")

def simulate_disconnected_tacho(enable: bool = True) -> None:
    """
    Simulate a disconnected tachometer signal
    """
    global _tacho_disconnected
    _tacho_disconnected = enable
    logger.info(f"Disconnected tachometer simulation {'enabled' if enable else 'disabled'}")


def simulate_disconnected_pwm(enable: bool = True) -> None:
    """
    Simulate disconnected PWM signal.
    """
    global _pwm_disconnected
    _pwm_disconnected = enable
    logger.info(f"Disconnected PWM simulation {'enabled' if enable else 'disabled'}")

def set_tacho_noise_level(noise_factor: float = 0.05) -> None:
    """
    Set noise level for tachometer readings
    """
    global _noise_level

    if noise_factor < 0.0:
        raise ValueError("Noise factor must be non-negative")
    
    _noise_level = noise_factor
    logger.info(f"Tachometer noise level set to {noise_factor*100:.1f}%")

def reset_all_faults() -> None:
    """
    Reset all faults
    """
    global _fan_stall_enabled, _fan_degradation, _tacho_disconnected
    global _pwm_disconnectedç, _noise_level

    _fan_stall_enabled = False
    _fan_degradation = 0.0
    _tacho_disconnected = False
    _pwm_disconnected = False
    _noise_level = 0.0

    logger.info("All fault simulations reset to normal operation")
