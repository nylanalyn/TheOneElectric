# AI Response Plugin for PyMotion

This guide explains how to set up and use the AI Response plugin that integrates OpenRouter AI capabilities into your PyMotion IRC bot.

## Features

- **Intelligent Responses**: Uses OpenRouter AI models to generate context-aware replies
- **IRC-Optimized**: Automatically truncates responses to fit within 150-character IRC message limits
- **Channel Control**: Whitelist/blacklist channels where AI should operate
- **Smart Triggering**: Only responds to relevant messages (questions, direct mentions, opinion requests)
- **Rate Limiting**: Built-in cooldowns to prevent spam
- **Context Awareness**: Maintains conversation history for better responses

## Setup Instructions

### 1. Install Required Dependencies

The AI plugin requires the `httpx` library for HTTP requests:

```bash
pip install httpx>=0.27.0
```

### 2. Get OpenRouter API Key

1. Sign up at [https://openrouter.ai](https://openrouter.ai)
2. Navigate to the API Keys section
3. Generate a new API key
4. Copy the key for configuration

### 3. Configure the Plugin

Add the AI plugin configuration to your `pymotion.json` file:

```json
{
  "ai_response": {
    "openrouter_api_key": "your-api-key-here",
    "openrouter_api_url": "https://openrouter.ai/api/v1/chat/completions",
    "model": "mistralai/mistral-7b-instruct:free",
    "max_response_length": 150,
    "response_probability": 0.6,
    "cooldown_seconds": 30,
    "enabled_channels": [],
    "disabled_channels": []
  }
}
```

### 4. Enable the Plugin

Make sure the AI plugin is in your enabled plugins list:

```json
"plugins": {
  "enabled": ["shutup", "admin", "greetings", "random_responses", "ai_response"],
  "disabled": []
}
```

### 5. Replace Test Plugin with Production Version

The repository includes a test version (`ai_response_test.py`) that works without dependencies. To use the real AI functionality:

```bash
# Remove the test version
rm plugins/ai_response_test.py

# Rename the production version
mv plugins/ai_response.py plugins/ai_response_prod.py
cp plugins/ai_response_prod.py plugins/ai_response.py

# Update the bot configuration to use "ai_response" instead of "ai_response_test"
```

## Configuration Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `openrouter_api_key` | Your OpenRouter API key | `""` |
| `openrouter_api_url` | OpenRouter API endpoint | `"https://openrouter.ai/api/v1/chat/completions"` |
| `model` | AI model to use | `"mistralai/mistral-7b-instruct:free"` |
| `max_response_length` | Maximum IRC message length | `150` |
| `response_probability` | Chance to respond when triggered (0.0-1.0) | `0.6` |
| `cooldown_seconds` | Minimum time between responses per user | `30` |
| `enabled_channels` | Whitelist of channels (empty = all) | `[]` |
| `disabled_channels` | Blacklist of channels | `[]` |

## Available AI Models

OpenRouter offers many models. Here are some good options:

- `mistralai/mistral-7b-instruct:free` - Free, fast, good quality
- `openai/gpt-3.5-turbo` - Paid, high quality
- `anthropic/claude-3-haiku` - Paid, excellent quality
- `google/gemini-pro` - Paid, good balance

## Usage Examples

### Direct Messages
```
User: PyMotion: What do you think about Python?
Bot: Python is an awesome programming language! I'm written in Python myself.
```

### Questions
```
User: PyMotion, tell me about artificial intelligence
Bot: AI is fascinating! I use AI to generate intelligent responses like this one.
```

### Opinion Requests
```
User: What's your opinion on IRC bots?
Bot: That's an interesting question! I think it depends on the context and perspective.
```

## Trigger Patterns

The AI plugin responds to these patterns:

- `botname: message` - Direct messages
- `botname, message` - Direct messages with comma
- `botname message` - Messages starting with bot name
- Messages containing bot name + question mark
- "What do you think..."
- "Your opinion..."
- "Tell me about..."

## Channel Management

### Allow Only Specific Channels
```json
"enabled_channels": ["#ai", "#bots", "#tech"],
"disabled_channels": []
```

### Block Specific Channels
```json
"enabled_channels": [],
"disabled_channels": ["#offtopic", "#spam"]
```

## Rate Limiting

The plugin includes several mechanisms to prevent spam:

1. **Per-User Cooldown**: `cooldown_seconds` prevents the same user from getting multiple AI responses too quickly
2. **Response Probability**: `response_probability` controls how often the bot responds when triggered
3. **Message Filtering**: Ignores empty messages and negative commands like "shut up"

## Troubleshooting

### API Key Issues
- **Error**: "OpenRouter API key not configured"
- **Solution**: Make sure your API key is correctly set in the configuration

### Connection Problems
- **Error**: "My brain seems to be offline"
- **Solution**: Check your internet connection and OpenRouter API status

### Rate Limits
- **Error**: HTTP 429 responses
- **Solution**: Increase cooldown times or reduce response probability

## Migration from Test to Production

When you're ready to switch from the test version to the real AI:

1. Install httpx: `pip install httpx>=0.27.0`
2. Replace the test plugin with the production version
3. Add your OpenRouter API key to the configuration
4. Restart the bot

## Security Considerations

- **API Key Protection**: Never commit your API key to version control
- **Rate Limits**: Monitor your OpenRouter usage to avoid unexpected charges
- **Channel Control**: Use channel whitelists/blacklists to control where AI operates
- **Response Filtering**: The plugin automatically filters inappropriate triggers

## Support

For issues with the AI plugin:
1. Check OpenRouter status: [https://status.openrouter.ai](https://status.openrouter.ai)
2. Verify your API key is valid
3. Check bot logs for detailed error messages
4. Ensure httpx is properly installed

## Example Configuration

Here's a complete example configuration:

```json
{
  "server": "irc.libera.chat",
  "port": 6697,
  "ssl": true,
  "nick": "PyMotionAI",
  "aliases": ["pymotion", "pybot"],
  "realname": "PyMotion with AI",
  "channels": [
    {"name": "#ai", "key": null},
    {"name": "#bots", "key": null}
  ],
  "plugins": {
    "enabled": ["shutup", "admin", "greetings", "ai_response"],
    "disabled": []
  },
  "ai_response": {
    "openrouter_api_key": "sk-your-key-here",
    "model": "mistralai/mistral-7b-instruct:free",
    "max_response_length": 150,
    "response_probability": 0.7,
    "cooldown_seconds": 45,
    "enabled_channels": ["#ai", "#bots"],
    "disabled_channels": []
  }
}
```

## Performance Tips

- Use the free `mistralai/mistral-7b-instruct:free` model for testing
- For production, consider paid models for better quality
- Adjust `response_probability` based on channel activity
- Use longer `cooldown_seconds` in busy channels
- Monitor OpenRouter usage in your account dashboard

Enjoy your AI-powered IRC bot! 🚀