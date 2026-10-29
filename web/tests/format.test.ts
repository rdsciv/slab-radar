import { test } from 'node:test';
import assert from 'node:assert/strict';
import { pct, roundHalfUp, dollars, signedPts, interval } from '../lib/format.ts';

test('percent rounds half-up like GemRate (15/24 = 62.5% → 63%)', () => {
  assert.equal(pct(15 / 24), '63%');
  assert.equal(pct(0.5), '50%');
  assert.equal(pct(null), '—');
});

test('negative half rounds away from zero and never prints -0', () => {
  assert.equal(roundHalfUp(-2.5), -3);
  assert.equal(signedPts(-0.001), '0 pts');
  assert.equal(signedPts(0.118), '+12 pts');
});

test('prices: whole dollars, $5 steps above $500', () => {
  assert.equal(dollars(39.6), '$40');
  assert.equal(dollars(1497), '$1,495');
  assert.equal(dollars(1498), '$1,500');
});

test('interval renders explicitly when missing', () => {
  assert.equal(interval({ value: 0.2, provenance: 'MODEL', n: 4, lo: null, hi: null }), 'no interval');
  assert.equal(interval({ value: 0.19, provenance: 'MODEL', n: 152, lo: 0.13, hi: 0.251 }), '13%–25%');
});
