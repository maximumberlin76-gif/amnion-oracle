# tests/test_safety_gate.py

from controller.safety_gate import SafetyGate


def test_allow_when_all_ok():
    gate = SafetyGate(
        min_coherence=0.80,
        max_temperature=39.0,
        max_pressure=2.0,
    )

    obs = {"temperature": 22.0, "pressure": 1.0, "coherence": 0.95}
    res = gate.evaluate(obs)

    assert res["allow"] is True
    assert res["reasons"] == []


def test_block_when_low_coherence():
    gate = SafetyGate(
        min_coherence=0.90,
        max_temperature=39.0,
        max_pressure=2.0,
    )

    obs = {"temperature": 22.0, "pressure": 1.0, "coherence": 0.85}
    res = gate.evaluate(obs)

    assert res["allow"] is False
    assert "low:coherence" in res["reasons"]


def test_block_when_over_temperature():
    gate = SafetyGate(
        min_coherence=0.80,
        max_temperature=30.0,
        max_pressure=2.0,
    )

    obs = {"temperature": 35.0, "pressure": 1.0, "coherence": 0.95}
    res = gate.evaluate(obs)

    assert res["allow"] is False
    assert "over:temperature" in res["reasons"]


def test_block_when_over_pressure():
    gate = SafetyGate(
        min_coherence=0.80,
        max_temperature=39.0,
        max_pressure=1.0,
    )

    obs = {"temperature": 22.0, "pressure": 1.5, "coherence": 0.95}
    res = gate.evaluate(obs)

    assert res["allow"] is False
    assert "over:pressure" in res["reasons"]


def test_missing_fields_block():
    gate = SafetyGate()

    obs = {"temperature": 22.0}
    res = gate.evaluate(obs)

    assert res["allow"] is False
    # ожидаем, что твой SafetyGate отдаёт причины в таком формате
    assert "missing:pressure" in res["reasons"]
    assert "missing:coherence" in res["reasons"]


def test_emergency_stop_blocks():
    gate = SafetyGate()

    obs = {"temperature": 22.0, "pressure": 1.0, "coherence": 0.95, "emergency_stop": True}
    res = gate.evaluate(obs)

    assert res["allow"] is False
    assert "emergency_stop=true" in res["reasons"]
  
