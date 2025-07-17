import click
from tacho_test import run_validation_sweep, reset_all_faults, simulate_fan_stall, simulate_fan_degradation, simulate_disconnected_tacho, simulate_disconnected_pwm, set_tacho_noise_level, CsvLogger

# Theoretical mapping between PWM and expected tachometer RPM
pwm_tacho_map = {
    0: 0,
    10: 400,
    20: 800,
    30: 1200,
    40: 1600,
    50: 2000,
    60: 2400,
    70: 2800,
    80: 3200,
    90: 3600,
    100: 4000
}

@click.command()
@click.option('--pwm-min', default=0, show_default=True, help='Minimum PWM value')
@click.option('--pwm-max', default=100, show_default=True, help='Maximum PWM value')
@click.option('--pwm-step', default=20, show_default=True, help='PWM step size')
@click.option('--tolerance', default=10, show_default=True, help='RPM tolerance percent')
@click.option('--stabilization', default=1.0, show_default=True, help='PWM stabilization time (s)')
@click.option('--samples', default=3, show_default=True, help='Number of samples')
@click.option('--fan-stall/--no-fan-stall', default=False, show_default=True, help='Enable/disable fan stall fault')
@click.option('--fan-degradation', default=0.0, show_default=True, help='Fan degradation level (0-1)')
@click.option('--disconnected-tacho/--no-disconnected-tacho', default=False, show_default=True, help='Enable/disable disconnected tacho fault')
@click.option('--disconnected-pwm/--no-disconnected-pwm', default=False, show_default=True, help='Enable/disable disconnected PWM fault')
@click.option('--noise', default=0.0, show_default=True, help='Tacho noise level (0-1)')
def run(
    pwm_min, pwm_max, pwm_step, tolerance, stabilization, samples,
    fan_stall, fan_degradation, disconnected_tacho, disconnected_pwm, noise
):
    reset_all_faults()
    if fan_stall:
        simulate_fan_stall(True)
    if fan_degradation > 0:
        simulate_fan_degradation(fan_degradation)
    if disconnected_tacho:
        simulate_disconnected_tacho(True)
    if disconnected_pwm:
        simulate_disconnected_pwm(True)
    if noise > 0:
        set_tacho_noise_level(noise)
    csv_dir = 'csv_logs'
    csv_logger = CsvLogger(csv_dir)
    failures, results = run_validation_sweep(
        pwm_min=pwm_min,
        pwm_max=pwm_max,
        pwm_step=pwm_step,
        expected_rpm_map=pwm_tacho_map,
        tolerance_percent=tolerance,
        stabilization_time=stabilization,
        number_samples=samples,
        csv_logger=csv_logger
    )
    print(f"Test complete: {failures} failures. Results saved to {csv_logger.get_path()}")

if __name__ == '__main__':
    run()
