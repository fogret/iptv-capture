
async function searchChannels(q) {
  const res = await fetch('channels.json');
  const channels = await res.json();
  q = q.toLowerCase();
  return channels.filter(ch => ch.name.toLowerCase().includes(q));
}
