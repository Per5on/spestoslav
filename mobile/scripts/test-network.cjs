const fs = require('node:fs'), ts = require('typescript'), assert = require('node:assert/strict');
const output = ts.transpileModule(fs.readFileSync('src/network.ts', 'utf8'), {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const mod={exports:{}};new Function('exports','module',output)(mod.exports,mod);
const {fetchWithRetry}=mod.exports;
const original=global.fetch, ok={status:200,ok:true};
async function main(){
 let calls=0;
 global.fetch=async()=>{if(++calls===1)throw new TypeError('Network unavailable');return ok;};
 assert.equal(await fetchWithRetry('https://test.invalid',{}, {retryDelayMs:0}),ok);assert.equal(calls,2);
 calls=0;
 let cancelledBodies=0;
 global.fetch=async()=>{
  const status=[502,503,504][calls++];
  return {status,ok:false,body:{cancel:async()=>{cancelledBodies++;}}};
 };
 assert.equal((await fetchWithRetry('https://test.invalid',{}, {retries:2,retryDelayMs:0})).status,504);
 assert.equal(calls,3);
 assert.equal(cancelledBodies,2);
 for(const method of ['POST','PUT','PATCH','DELETE']){
  calls=0;global.fetch=async()=>{calls++;throw new TypeError('Network unavailable');};
  await assert.rejects(fetchWithRetry('https://test.invalid',{method},{retries:2,retryDelayMs:0}),TypeError);assert.equal(calls,1);
 }
 calls=0;global.fetch=async()=>{calls++;return {status:404,ok:false};};
 assert.equal((await fetchWithRetry('https://test.invalid',{}, {retryDelayMs:0})).status,404);assert.equal(calls,1);
 const cancelled=new AbortController();cancelled.abort();calls=0;
 await assert.rejects(fetchWithRetry('https://test.invalid',{signal:cancelled.signal}),{name:'AbortError'});assert.equal(calls,0);
 calls=0;global.fetch=async(_url,{signal})=>{if(++calls>1)return ok;return new Promise((_resolve,reject)=>signal.addEventListener('abort',()=>{const e=new Error('Timeout');e.name='AbortError';reject(e);}));};
 assert.equal(await fetchWithRetry('https://test.invalid',{}, {timeoutMs:10,retryDelayMs:0}),ok);assert.equal(calls,2);
 const ongoing=new AbortController();calls=0;
 global.fetch=async()=>{calls++;setTimeout(()=>ongoing.abort(),5);return {status:503,ok:false};};
 await assert.rejects(fetchWithRetry('https://test.invalid',{signal:ongoing.signal},{retryDelayMs:100}),{name:'AbortError'});assert.equal(calls,1);
 calls=0;global.fetch=async(_url,{signal})=>{if(++calls>1)return {status:200,json:async()=>({ready:true})};return {status:200,json:()=>new Promise((_resolve,reject)=>signal.addEventListener('abort',()=>{const e=new Error('Body timeout');e.name='AbortError';reject(e);} ))};};
 assert.deepEqual(await fetchWithRetry('https://test.invalid',{}, {timeoutMs:10,retryDelayMs:0},r=>r.json()),{ready:true});assert.equal(calls,2);
 calls=0;global.fetch=async()=>{calls++;return {status:200,json:async()=>{throw new SyntaxError('Invalid response');}};};
 await assert.rejects(fetchWithRetry('https://test.invalid',{}, {retryDelayMs:0},r=>r.json()),SyntaxError);assert.equal(calls,1);
 console.log('Network checks passed: bounded read retries, timeout recovery, cancellation and no automatic write replay.');
}
main().finally(()=>{global.fetch=original;}).catch(error=>{console.error(error);process.exitCode=1;});
