import type { VercelRequest, VercelResponse } from '@vercel/node';
import OpenAI from 'openai';
import { OpenAIStream, StreamingTextResponse } from 'ai';

const openai = new OpenAI({
  apiKey: process.env.GROQ_API_KEY,
  baseURL: 'https://api.groq.com/openai/v1',
});

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const prompt = typeof req.query.prompt === 'string' ? req.query.prompt : '';
  if (!prompt) {
    res.status(400).json({ error: 'Missing `prompt` query parameter' });
    return;
  }

  const response = await openai.chat.completions.create({
    model: 'llama3-70b-8192',
    stream: true,
    messages: [{ role: 'user', content: prompt }],
  });

  const stream = OpenAIStream(response);
  return new StreamingTextResponse(stream);
}
