import { AnthropicApi } from '@anthropic-ai/sdk';
import { NextResponse } from 'next/server';

// Remove the hardcoded API key
// const anthropic = new AnthropicApi({ apiKey: 'sk-ant-api03-...' });

// Use an environment variable instead
const anthropic = new AnthropicApi({ apiKey: process.env.ANTHROPIC_API_KEY });

// ... rest of the code ...