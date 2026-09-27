"""Science and engineering reasoning tools for Robin.

The tools deliberately use explicit formulas rather than eval() so numerical
work is reproducible and safer. They are intended for educational/design
assistance; real-world safety-critical work still needs qualified review.
"""
from __future__ import annotations
import math

def _num(p, key):
    return float(p[key])

def _fmt(x):
    if not math.isfinite(x):
        return "undefined"
    return f"{x:.8g}"

def engineering_calculate(parameters: dict, **_) -> str:
    kind = str(parameters.get("calculation", "")).strip().lower()
    try:
        if kind == "force":
            a = _num(parameters, "acceleration")
            m = _num(parameters, "mass")
            return f"Force = m*a = {_fmt(m*a)} N."
        if kind == "power_electrical":
            v, i = _num(parameters, "voltage"), _num(parameters, "current")
            return f"Electrical power = V*I = {_fmt(v*i)} W."
        if kind == "ohms_law":
            v = parameters.get("voltage")
            i = parameters.get("current")
            r = parameters.get("resistance")
            supplied = sum(x is not None for x in (v, i, r))
            if supplied != 2:
                return "Ohm's law needs exactly two of voltage, current, and resistance."
            if v is None:
                return f"Voltage = I*R = {_fmt(_num(parameters,'current')*_num(parameters,'resistance'))} V."
            if i is None:
                return f"Current = V/R = {_fmt(_num(parameters,'voltage')/_num(parameters,'resistance'))} A."
            return f"Resistance = V/I = {_fmt(_num(parameters,'voltage')/_num(parameters,'current'))} ohm."
        if kind == "torque":
            return f"Torque = force*lever_arm = {_fmt(_num(parameters,'force')*_num(parameters,'lever_arm'))} N*m."
        if kind == "mechanical_power":
            return f"Mechanical power = torque*angular_speed = {_fmt(_num(parameters,'torque')*_num(parameters,'angular_speed'))} W."
        if kind == "energy":
            return f"Kinetic energy = 0.5*m*v^2 = {_fmt(0.5*_num(parameters,'mass')*_num(parameters,'velocity')**2)} J."
        if kind == "heat":
            return f"Heat = m*c*deltaT = {_fmt(_num(parameters,'mass')*_num(parameters,'specific_heat')*_num(parameters,'delta_temperature'))} J."
        if kind == "stress":
            return f"Normal stress = force/area = {_fmt(_num(parameters,'force')/_num(parameters,'area'))} Pa."
        if kind == "strain":
            return f"Engineering strain = delta_length/original_length = {_fmt(_num(parameters,'delta_length')/_num(parameters,'original_length'))}."
        if kind == "density":
            return f"Density = mass/volume = {_fmt(_num(parameters,'mass')/_num(parameters,'volume'))} kg/m^3."
        if kind == "resistor_series":
            values = [float(x) for x in parameters.get("resistances", [])]
            return f"Series resistance = {_fmt(sum(values))} ohm."
        if kind == "resistor_parallel":
            values = [float(x) for x in parameters.get("resistances", [])]
            if not values or any(x == 0 for x in values):
                return "Parallel resistance needs non-zero resistor values."
            return f"Parallel resistance = {_fmt(1/sum(1/x for x in values))} ohm."
        if kind == "unit":
            value = _num(parameters, "value")
            src, dst = str(parameters["from"]).lower(), str(parameters["to"]).lower()
            factors = {
                ("mm","m"): 1e-3, ("m","mm"): 1e3,
                ("cm","m"): 1e-2, ("m","cm"): 1e2,
                ("km","m"): 1e3, ("m","km"): 1e-3,
                ("in","mm"): 25.4, ("mm","in"): 1/25.4,
                ("ft","m"): 0.3048, ("m","ft"): 3.280839895,
                ("rpm","rad/s"): 2*math.pi/60, ("rad/s","rpm"): 60/(2*math.pi),
                ("c","k"): 1.0, ("k","c"): 1.0
            }
            if (src,dst) in factors:
                result = value*factors[(src,dst)]
                if {src,dst} == {"c","k"}:
                    result = value + (273.15 if src == "c" else -273.15)
                return f"{value:g} {src} = {_fmt(result)} {dst}."
            return "That unit conversion is not in the built-in safe table; use a suitable unit-aware calculator or ask Robin to search for the conversion."
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as e:
        return f"I need valid numeric parameters for that calculation: {e}"
    return "Supported calculations include force, torque, mechanical_power, energy, heat, stress, strain, density, Ohm's law, electrical power, series/parallel resistance, and common engineering unit conversions."

TOOL = {
    "name": "engineering_calculate",
    "description": "Perform explicit physics, mechanics, electrical, electronics, and engineering calculations using safe formulas.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "calculation": {"type":"STRING","description":"Calculation type: force, torque, mechanical_power, energy, heat, stress, strain, density, ohms_law, power_electrical, resistor_series, resistor_parallel, unit."},
            "mass": {"type":"NUMBER"}, "acceleration": {"type":"NUMBER"},
            "force": {"type":"NUMBER"}, "lever_arm": {"type":"NUMBER"},
            "torque": {"type":"NUMBER"}, "angular_speed": {"type":"NUMBER"},
            "velocity": {"type":"NUMBER"}, "specific_heat": {"type":"NUMBER"},
            "delta_temperature": {"type":"NUMBER"}, "area": {"type":"NUMBER"},
            "delta_length": {"type":"NUMBER"}, "original_length": {"type":"NUMBER"},
            "volume": {"type":"NUMBER"}, "voltage": {"type":"NUMBER"},
            "current": {"type":"NUMBER"}, "resistance": {"type":"NUMBER"},
            "resistances": {"type":"ARRAY","items":{"type":"NUMBER"}},
            "value": {"type":"NUMBER"}, "from": {"type":"STRING"}, "to": {"type":"STRING"}
        },
        "required": ["calculation"]
    },
    "handler": engineering_calculate
}
