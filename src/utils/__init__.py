
def get_delay_in_samples(delay: float, sampling_rate: float) -> int:
    return int(delay * 1e-6 * sampling_rate)
