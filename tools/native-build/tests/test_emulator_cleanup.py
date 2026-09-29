import subprocess
import time
from pathlib import Path

import pytest

from branch_native_build import mobile


class FakeEmulatorProcess:
    """Minimal Popen stand-in with scripted wait outcomes."""

    def __init__(self, wait_outcomes: list):
        self.wait_outcomes = list(wait_outcomes)
        self.waits = 0
        self.terminated = False
        self.killed = False

    def wait(self, timeout=None):
        self.waits += 1
        outcome = self.wait_outcomes.pop(0) if self.wait_outcomes else "timeout"
        if outcome == "timeout":
            raise subprocess.TimeoutExpired(cmd="emulator", timeout=timeout)
        return 0

    def terminate(self):
        self.terminated = True

    def kill(self):
        self.killed = True


def test_shutdown_request_is_bounded_and_timeout_is_swallowed(monkeypatch):
    recorded = {}

    def fake_run(command, **kwargs):
        recorded["command"] = command
        recorded["timeout"] = kwargs.get("timeout")
        raise subprocess.TimeoutExpired(cmd=command, timeout=kwargs.get("timeout"))

    monkeypatch.setattr(mobile.subprocess, "run", fake_run)
    monkeypatch.setattr(mobile.native, "sdk", lambda: Path("/sdk"))
    mobile._bound_shutdown_request("emulator-5580")
    assert recorded["timeout"] == 10
    assert recorded["command"][1:] == ["-s", "emulator-5580", "emu", "kill"]
    assert str(recorded["command"][0]).endswith("platform-tools/adb")


def test_graceful_exit_skips_terminate_and_kill(monkeypatch):
    requests = []
    monkeypatch.setattr(mobile, "_bound_shutdown_request", lambda serial: requests.append(serial))
    process = FakeEmulatorProcess([None])
    mobile._stop_owned_emulator(process, "emulator-5580")
    assert requests == ["emulator-5580"]
    assert process.waits == 1
    assert not process.terminated
    assert not process.killed


def test_ignored_termination_escalates_to_kill(monkeypatch):
    monkeypatch.setattr(mobile, "_bound_shutdown_request", lambda serial: None)
    process = FakeEmulatorProcess(["timeout", "timeout", None])
    mobile._stop_owned_emulator(process, "emulator-5580")
    assert process.terminated
    assert process.killed
    assert process.waits == 3


def test_unreapable_process_raises_bounded_error(monkeypatch):
    monkeypatch.setattr(mobile, "_bound_shutdown_request", lambda serial: None)
    process = FakeEmulatorProcess(["timeout", "timeout", "timeout"])
    with pytest.raises(RuntimeError, match="did not exit after kill"):
        mobile._stop_owned_emulator(process, "emulator-5580")
    assert process.killed


def test_cleanup_failure_is_reported_when_primary_failure_is_active(capsys, monkeypatch):
    def broken(process, serial):
        raise RuntimeError("cleanup broke")

    monkeypatch.setattr(mobile, "_stop_owned_emulator", broken)
    with pytest.raises(ValueError, match="primary"):
        try:
            raise ValueError("primary test failure")
        finally:
            mobile._release_owned_emulator(object(), "emulator-5580")
    assert "cleanup broke" in capsys.readouterr().err


def test_cleanup_failure_propagates_without_primary_failure(monkeypatch):
    def broken(process, serial):
        raise RuntimeError("cleanup broke")

    monkeypatch.setattr(mobile, "_stop_owned_emulator", broken)
    with pytest.raises(RuntimeError, match="cleanup broke"):
        mobile._release_owned_emulator(object(), "emulator-5580")


def test_real_isolated_process_exits_within_the_bound(monkeypatch):
    monkeypatch.setattr(mobile, "_bound_shutdown_request", lambda serial: None)
    process = subprocess.Popen(["bash", "-c", "sleep 0.05"])
    try:
        started = time.monotonic()
        mobile._stop_owned_emulator(process, "emulator-5580", grace=5)
        assert process.poll() is not None
        assert time.monotonic() - started < 5
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


def test_real_process_ignoring_sigterm_is_killed_and_reaped(monkeypatch):
    monkeypatch.setattr(mobile, "_bound_shutdown_request", lambda serial: None)
    process = subprocess.Popen(["bash", "-c", "trap '' TERM; sleep 300"])
    try:
        started = time.monotonic()
        mobile._stop_owned_emulator(
            process,
            "emulator-5580",
            grace=0.2,
            terminate_wait=0.2,
            kill_wait=5,
        )
        assert process.poll() is not None
        assert time.monotonic() - started < 5
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


def test_borrowed_device_is_never_stopped(monkeypatch):
    released = []
    monkeypatch.setattr(
        mobile, "_release_owned_emulator", lambda process, serial: released.append(serial)
    )
    monkeypatch.setenv("ANDROID_SERIAL", "emulator-9999")
    monkeypatch.setattr(mobile.native, "sdk", lambda: Path("/nonexistent-sdk"))

    class Booted:
        returncode = 0
        stdout = "1\n"

    monkeypatch.setattr(mobile.subprocess, "run", lambda *args, **kwargs: Booted())
    with mobile.android_device() as serial:
        assert serial == "emulator-9999"
    assert released == []
