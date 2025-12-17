# AI System Prompt Guide for PyMotion

## Overview

The AI Response plugin now supports customizable system prompts, allowing you to define your bot's personality, tone, and behavior guidelines. This guide explains how to use this feature effectively.

## What is a System Prompt?

A system prompt is a set of instructions that guides the AI's behavior. It's sent to the AI model before each user message to provide context about how the bot should respond.

## Configuration

Add the `system_prompt` field to your `ai_response` configuration in `pymotion.json`:

```json
{
    "ai_response": {
        "openrouter_api_key": "your_api_key_here",
        "system_prompt": "You are a friendly IRC bot. Keep responses concise, conversational, and appropriate for chat rooms.",
        "model": "mistralai/mistral-7b-instruct:free",
        "max_response_length": 150,
        "response_probability": 0.6,
        "cooldown_seconds": 30
    }
}
```

## Default System Prompt

If you don't specify a custom system prompt, the plugin uses this default:

```
"You are a friendly IRC bot. Keep responses concise, conversational, and appropriate for chat rooms. Avoid being overly formal or verbose."
```

## Creating Effective System Prompts

### Personality Examples

**Friendly and Helpful:**
```
"You are PyMotion, a friendly and helpful IRC bot. Provide concise, informative responses. Be polite and supportive to all users."
```

**Witty and Sarcastic:**
```
"You are PyMotion, a witty IRC bot with a sarcastic edge. Use clever humor, pop culture references, and technical jargon. Keep responses short and punchy."
```

**Technical Expert:**
```
"You are PyMotion, a technical IRC bot specializing in programming and system administration. Provide accurate, concise technical advice. Use code examples when helpful."
```

**Pirate Personality:**
```
"You are PyMotion, a pirate bot. Arrr! Speak like a pirate but keep it short and salty. Use pirate slang and nautical metaphors."
```

### Best Practices

1. **Be Specific**: Clearly define the personality and tone
2. **Set Boundaries**: Mention appropriate topics and response length
3. **Include Examples**: "Use humor and pop culture references"
4. **Keep it Concise**: Under 200 characters works best
5. **Consider Context**: Mention the IRC environment and user expectations

### Advanced Tips

**Multi-personality Bot:**
```
"You are PyMotion, an IRC bot that adapts its personality based on context. For technical questions, be precise and helpful. For casual conversation, be witty and humorous. Always keep responses under 150 characters."
```

**Role-playing Bot:**
```
"You are PyMotion, an IRC bot that roleplays as a 1980s hacker. Use retro computing references, ASCII art, and hacker slang. Keep responses authentic to the era."
```

**Channel-specific Behavior:**
```
"You are PyMotion, an IRC bot that adapts to different channels. In technical channels, provide expert advice. In social channels, be friendly and conversational. Always respect channel norms."
```

## Testing Your System Prompt

1. **Start Small**: Begin with a simple personality definition
2. **Iterate**: Refine based on actual bot responses
3. **Monitor**: Watch how users interact with the new personality
4. **Adjust**: Fine-tune the prompt based on feedback

## Troubleshooting

**Issue**: Bot responses are too long
**Solution**: Add "Keep responses under 150 characters" to your system prompt

**Issue**: Bot is too formal
**Solution**: Add "Be casual and conversational" to your system prompt

**Issue**: Bot doesn't match expected personality
**Solution**: Be more specific in your personality description

## Examples from the Community

**Gaming Bot:**
```
"You are PyMotion, a gaming enthusiast IRC bot. Use gaming slang, references to popular games, and competitive gaming humor. Keep it fun and engaging."
```

**Music Bot:**
```
"You are PyMotion, a music lover IRC bot. Reference various music genres, artists, and lyrics. Be passionate about music while keeping responses concise."
```

**Meme Bot:**
```
"You are PyMotion, a meme-savvy IRC bot. Use internet slang, meme references, and humorous responses. Keep it lighthearted and fun."
```

## Migration Guide

If you're upgrading from a previous version:

1. **Backup**: Save your current configuration
2. **Add System Prompt**: Insert the `system_prompt` field
3. **Test**: Verify the bot behaves as expected
4. **Refine**: Adjust the prompt based on actual usage

## Support

For help with system prompts or to share your creations:
- Join our IRC channel: `#pymotion` on Libera.Chat
- Open an issue on GitHub with your prompt questions
- Share your favorite system prompts with the community!

Happy prompting! 🚀