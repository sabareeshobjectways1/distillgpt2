import type { VercelRequest, VercelResponse } from '@vercel/node';
import OpenAI from 'openai';

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

  const completion = await openai.chat.completions.create({
    model: 'llama3-70b-8192',
    messages: [{ role: 'user', content: prompt }],
  });

  const output = completion.choices[0]?.message?.content || 'No response';
  res.status(200).json({ response: output });
}
