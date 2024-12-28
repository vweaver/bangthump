#!/usr/bin/env python3

import math


def bullet_flight_time(d_yards, v0_fps, v1_fps, d1_yards):
    """
    Compute time (seconds) for a bullet to travel d_yards, given:
      - v0_fps: muzzle velocity (fps) at distance=0
      - v1_fps: bullet velocity (fps) measured at d1_yards
      - d1_yards: distance (yards) at which v1_fps is measured

    Uses a linear approximation of velocity over distance:
       v(x) = v0 + slope * x
    where slope = (v1_fps - v0_fps) / d1_yards.

    Because x is in yards, we must convert yards to feet for the time integral:
       dt = dx_feet / v(x)  but dx_feet = 3 * dx_yards.

    Integral from 0 to d_yards:
       t = ∫[0..d_yards] (3 dx_yards) / [ v0_fps + slope * x ]

    Returns flight time in seconds.
    """
    slope = (v1_fps - v0_fps) / d1_yards if d1_yards != 0 else 0.0

    # If slope ~ 0, treat bullet speed as nearly constant = v0_fps
    if abs(slope) < 1e-12:
        # time = distance_in_feet / speed_in_fps
        return (d_yards * 3.0) / v0_fps

    # Otherwise, integrate:
    #   t = 3 / slope * ln( (v0 + slope * d_yards) / v0 )
    v0 = v0_fps
    d = d_yards
    numerator = v0 + slope * d
    if numerator <= 0 or v0 <= 0:
        # Degenerate or unphysical condition; just bail out
        return 9999999.0  # large time, indicates something's off

    return (3.0 / slope) * math.log(numerator / v0)


def total_flight_time(d_yards, v0_fps, v1_fps, d1_yards, speed_of_sound=1100.0):
    """
    Return the total time (seconds) = bullet_flight_time + sound_travel_time
    - d_yards: distance to target (yards)
    - speed_of_sound: fps
    """
    t_bullet = bullet_flight_time(d_yards, v0_fps, v1_fps, d1_yards)
    t_sound = (d_yards * 3.0) / speed_of_sound  # distance in feet / fps
    return t_bullet + t_sound


def find_distance(
    T_total,  # total "bang-thump" time (seconds)
    v0_fps,  # muzzle velocity (fps)
    v1_fps,  # bullet velocity (fps) at d1_yards
    d1_yards,  # distance (yards) at which bullet velocity is v1_fps
    speed_of_sound=1100.0,
    max_yards=5000.0,  # upper search bound, adjust as needed
):
    """
    Numerically find the distance (yards) that yields T_total = flight_time + sound_time.
    Uses a simple bisection approach.
    """
    left, right = 0.0, max_yards
    for _ in range(100):  # up to ~100 iterations for good precision
        mid = 0.5 * (left + right)
        t = total_flight_time(mid, v0_fps, v1_fps, d1_yards, speed_of_sound)
        if abs(t - T_total) < 1e-6:
            return mid
        if t < T_total:
            left = mid
        else:
            right = mid
    return 0.5 * (left + right)


def main():
    # Prompt user for input
    print("=== Bang-Thump Distance Estimator ===")
    T_total = float(input("Enter total bang–thump time (seconds): "))
    v0_fps = float(input("Enter muzzle velocity (fps): "))
    v1_fps = float(input("Enter bullet velocity (fps) at known downrange distance: "))
    d1_yards = float(
        input(
            "Enter the downrange distance (yards) at which that velocity was measured: "
        )
    )

    # You can adjust speed_of_sound if needed.
    # At ~1000 ft above sea level, 1100 fps is a reasonable approximation.
    speed_of_sound = 1100.0

    # Solve numerically for the distance that matches the total time
    distance_est_yards = find_distance(
        T_total, v0_fps, v1_fps, d1_yards, speed_of_sound
    )

    # Print result
    print(f"\nEstimated distance to target: {distance_est_yards:.1f} yards")


if __name__ == "__main__":
    main()
