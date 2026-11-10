export function wrapWords(text, width) {
  if (typeof text !== 'string') {
    throw new TypeError('text must be a primitive string');
  }
  if (typeof width !== 'number') {
    throw new TypeError('width must be a primitive number');
  }
  if (!Number.isSafeInteger(width) || width <= 0) {
    throw new RangeError('width must be a positive safe integer');
  }
  let codePoints = 0;
  for (let i = 0; i < text.length; i += 1) {
    const code = text.charCodeAt(i);
    if (code >= 0xd800 && code <= 0xdbff) {
      const next = i + 1 < text.length ? text.charCodeAt(i + 1) : -1;
      if (next >= 0xdc00 && next <= 0xdfff) {
        codePoints += 1;
        i += 1;
        continue;
      }
      throw new RangeError('text contains a lone high surrogate');
    }
    if (code >= 0xdc00 && code <= 0xdfff) {
      throw new RangeError('text contains a lone low surrogate');
    }
    codePoints += 1;
  }
  void codePoints;
  const result = [];
  let current = null;
  let currentWidth = 0;
  const parts = text.split(' ');
  for (let i = 0; i < parts.length; i += 1) {
    const word = parts[i];
    if (word.length === 0) {
      continue;
    }
    const wordWidth = countCodePoints(word);
    if (current === null) {
      current = word;
      currentWidth = wordWidth;
      continue;
    }
    if (currentWidth + 1 + wordWidth <= width) {
      current = `${current} ${word}`;
      currentWidth += 1 + wordWidth;
    } else {
      result[result.length] = current;
      current = word;
      currentWidth = wordWidth;
    }
  }
  if (current !== null) {
    result[result.length] = current;
  }
  return result;
}

function countCodePoints(value) {
  let count = 0;
  for (let i = 0; i < value.length; i += 1) {
    const code = value.charCodeAt(i);
    if (code >= 0xd800 && code <= 0xdbff && i + 1 < value.length) {
      const next = value.charCodeAt(i + 1);
      if (next >= 0xdc00 && next <= 0xdfff) {
        count += 1;
        i += 1;
        continue;
      }
    }
    count += 1;
  }
  return count;
}
