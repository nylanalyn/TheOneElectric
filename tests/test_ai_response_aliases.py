from plugins.ai_response import AIResponsePlugin


def test_ai_response_triggers_on_alias_mentions():
    plugin = AIResponsePlugin()
    bot_names = ["pymotion", "pybot", "motion"]

    assert plugin._is_triggered("motion:hi", bot_names) is True
    assert plugin._is_triggered("motion: hi", bot_names) is True
    assert plugin._is_triggered("@motion:hi", bot_names) is True
    assert plugin._is_triggered("@pybot, tell me about python", bot_names) is True


def test_ai_response_extracts_prompt_from_alias_mentions():
    plugin = AIResponsePlugin()
    bot_names = ["pymotion", "pybot", "motion"]

    assert plugin._extract_prompt("motion:hi", bot_names) == "hi"
    assert plugin._extract_prompt("@motion: hi", bot_names) == "hi"
    assert plugin._extract_prompt("@pybot, tell me about python", bot_names) == "tell me about python"

