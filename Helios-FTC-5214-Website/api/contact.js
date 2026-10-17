// Vercel serverless function. No packages needed: Node.js built-in fetch.
const DESTINATION = '5214.helios@gmail.com';
const allowedSubjects = new Set([
  'General inquiry', 'Outreach collaboration', 'Sponsorship or support',
  'Competition or robotics', 'Other'
]);
const emailPattern = /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/;
const clean = value => typeof value === 'string' ? value.trim() : '';
const htmlEscape = value => value.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({error:'Only POST requests are supported.'});
  }
  const length = Number(req.headers['content-length'] || 0);
  if (length > 12000) return res.status(413).json({error:'Message is too long.'});
  let data = req.body;
  try { if (typeof data === 'string') data = JSON.parse(data); } catch { return res.status(400).json({error:'Invalid form data.'}); }
  if (!data || typeof data !== 'object' || Array.isArray(data)) return res.status(400).json({error:'Invalid form data.'});
  // Honeypot: bots fill hidden fields, humans do not.
  if (clean(data.company)) return res.status(200).json({ok:true});
  const name = clean(data.name), email = clean(data.email), subject = clean(data.subject), message = clean(data.message);
  if (name.length < 2 || name.length > 120 || !emailPattern.test(email) || email.length > 200 || !allowedSubjects.has(subject) || message.length < 10 || message.length > 5000) {
    return res.status(400).json({error:'Please check all fields and try again.'});
  }
  const apiKey = process.env.RESEND_API_KEY;
  const sender = process.env.RESEND_FROM;
  if (!apiKey || !sender) {
    return res.status(503).json({error:'Email delivery is not configured yet. Please email us directly at 5214.helios@gmail.com.'});
  }
  try {
    const safeName = htmlEscape(name), safeEmail = htmlEscape(email), safeSubject = htmlEscape(subject), safeMessage = htmlEscape(message).replace(/\n/g,'<br>');
    const response = await fetch('https://api.resend.com/emails', {
      method:'POST',
      headers:{Authorization:`Bearer ${apiKey}`, 'Content-Type':'application/json'},
      body:JSON.stringify({
        from:sender,
        to:[DESTINATION],
        reply_to:email,
        subject:`[Helios website] ${subject}`,
        text:`New message to Helios FTC 5214\n\nFrom: ${name}\nEmail: ${email}\nTopic: ${subject}\n\n${message}`,
        html:`<div style="font-family:Arial,sans-serif;line-height:1.6;max-width:640px"><h2>New Helios website inquiry</h2><p><strong>From:</strong> ${safeName}<br><strong>Email:</strong> ${safeEmail}<br><strong>Topic:</strong> ${safeSubject}</p><hr><p>${safeMessage}</p></div>`
      })
    });
    if (!response.ok) {
      console.error('Email provider failure', response.status, await response.text());
      return res.status(502).json({error:'Unable to deliver your message. Please email 5214.helios@gmail.com directly.'});
    }
    return res.status(200).json({ok:true});
  } catch (error) {
    console.error('Contact endpoint failure', error);
    return res.status(502).json({error:'Email could not be sent right now. Please use the email link instead.'});
  }
};
