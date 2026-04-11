#!/usr/bin/env node
/**
 * test-vectors/verify-node.js — CheckMacValue 實作驗證腳本（Node.js 版）
 *
 * 本腳本讀取 test-vectors/check-mac-value.json 並驗證 Node.js 版本之
 * CheckMacValue 實作是否能產出與 JSON 中相同之 MAC。
 *
 * 用法：
 *   node test-vectors/verify-node.js
 *
 * 退出碼：
 *   0 — 全部通過
 *   1 — 至少一項失敗
 *
 * 本腳本只使用 Node.js 內建模組（crypto, fs, path），不依賴任何第三方套件。
 */

'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

/**
 * 仿 .NET URL encoding 規則。
 *
 * Node.js `encodeURIComponent` 與 `querystring.escape` 的保留字元與 .NET
 * 不同，需手動還原 -, _, ., !, *, (, )。
 */
function dotnetUrlEncode(s) {
  // encodeURIComponent 會將空白轉為 %20，但 .NET 是 +
  let encoded = encodeURIComponent(s).replace(/%20/g, '+');
  encoded = encoded.toLowerCase();
  const replacements = {
    '%2d': '-',
    '%5f': '_',
    '%2e': '.',
    '%21': '!',
    '%2a': '*',
    '%28': '(',
    '%29': ')',
  };
  for (const [k, v] of Object.entries(replacements)) {
    encoded = encoded.split(k).join(v);
  }
  return encoded;
}

function computeCheckMac(params, hashKey, hashIv) {
  const filtered = Object.fromEntries(
    Object.entries(params).filter(([k]) => k !== 'CheckMacValue')
  );
  const sortedKeys = Object.keys(filtered).sort();
  const pairs = sortedKeys.map((k) => `${k}=${filtered[k]}`);
  const raw = `HashKey=${hashKey}&${pairs.join('&')}&HashIV=${hashIv}`;
  const encoded = dotnetUrlEncode(raw);
  return crypto.createHash('sha256').update(encoded, 'utf8').digest('hex').toUpperCase();
}

function main() {
  const vectorsPath = path.join(__dirname, 'check-mac-value.json');
  if (!fs.existsSync(vectorsPath)) {
    console.error(`找不到測試向量檔：${vectorsPath}`);
    return 1;
  }

  const data = JSON.parse(fs.readFileSync(vectorsPath, 'utf8'));
  const { hash_key: hashKey, hash_iv: hashIv, vectors } = data;

  const total = vectors.length;
  let passed = 0;
  const failed = [];

  for (const vec of vectors) {
    const expected = vec.expected_mac.toUpperCase();
    const actual = computeCheckMac(vec.params, hashKey, hashIv);
    if (actual === expected) {
      console.log(`[OK]   ${vec.name}`);
      passed += 1;
    } else {
      console.log(`[FAIL] ${vec.name}`);
      console.log(`       expected: ${expected}`);
      console.log(`       actual:   ${actual}`);
      failed.push(vec.name);
    }
  }

  console.log();
  console.log(`結果：${passed}/${total} 通過`);

  if (failed.length > 0) {
    console.log('失敗項目：');
    for (const name of failed) {
      console.log(`  - ${name}`);
    }
    return 1;
  }

  return 0;
}

process.exit(main());
