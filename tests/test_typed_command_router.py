import pytest

from core.typed_command_router import execute_typed_command, parse_typed_command


def test_parse_run_command_json():
    cmd = parse_typed_command('run open_app {"application":"notepad"}')
    assert cmd.action == "open_app"
    assert cmd.parameters == {"application": "notepad"}


def test_parse_slash_command():
    cmd = parse_typed_command('/open_app application=notepad')
    assert cmd.action == "open_app"
    assert cmd.parameters == {"application": "notepad"}


def test_parse_quoted_value():
    cmd = parse_typed_command('/browser_search query="hello world"')
    assert cmd.parameters == {"query": "hello world"}


def test_plain_conversation_is_not_a_command():
    assert parse_typed_command("How are you?") is None


def test_invalid_parameter_is_rejected():
    with pytest.raises(ValueError):
        parse_typed_command("/open_app not-a-pair")


def test_execute_uses_registry_policy_boundary():
    calls = []

    class Registry:
        def has(self, name):
            return name == "demo"

        def run(self, name, params, ctx):
            calls.append((name, params, ctx))
            return "ok"

    assert execute_typed_command('/demo value=true', Registry(), {"confirmed": True}) == "ok"
    assert calls == [("demo", {"value": True}, {"confirmed": True})]


def test_unknown_action_does_not_execute():
    class Registry:
        def has(self, name):
            return False

        def run(self, *args):
            raise AssertionError("must not execute")

    assert execute_typed_command('/missing', Registry()) == "Action 'missing' is not available."
