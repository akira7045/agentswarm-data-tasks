import {types} from 'node:util';

function isDenseNormalArray(value) {
  if (types.isProxy(value)) return false;
  if (!Array.isArray(value)) return false;
  if (Object.getPrototypeOf(value) !== Array.prototype) return false;
  const keys = Object.keys(value);
  const length = value.length;
  if (keys.length !== length) return false;
  for (let i = 0; i < length; i++) {
    if (!Object.prototype.hasOwnProperty.call(value, i)) return false;
  }
  return true;
}

export function dedupeRows(rows, keyIndex) {
  // Validate ALL shapes and types before bounds.
  if (!isDenseNormalArray(rows)) throw new TypeError('rows must be a dense normal Array');
  const length = rows.length;
  for (let i = 0; i < length; i++) {
    if (!isDenseNormalArray(rows[i])) {
      throw new TypeError('each row must be a dense normal Array');
    }
  }

  if (typeof keyIndex !== 'number') throw new TypeError('keyIndex must be a primitive number');

  for (let i = 0; i < length; i++) {
    const row = rows[i];
    const rowLength = row.length;
    for (let j = 0; j < rowLength; j++) {
      if (typeof row[j] !== 'string') throw new TypeError('row cells must be primitive strings');
    }
  }

  // Bounds.
  if (!Number.isSafeInteger(keyIndex) || keyIndex < 0) {
    throw new RangeError('keyIndex must be a nonnegative safe integer');
  }

  for (let i = 0; i < length; i++) {
    if (!(keyIndex < rows[i].length)) {
      throw new RangeError('every row must have an element at keyIndex');
    }
  }

  // Deduplicate keeping the first row per distinct key, preserving order,
  // returning fresh normal dense copies.
  const seen = new Set();
  const result = [];
  for (let i = 0; i < length; i++) {
    const row = rows[i];
    const key = row[keyIndex];
    if (seen.has(key)) continue;
    seen.add(key);
    const copy = new Array(row.length);
    for (let j = 0; j < row.length; j++) copy[j] = row[j];
    result.push(copy);
  }
  return result;
}
