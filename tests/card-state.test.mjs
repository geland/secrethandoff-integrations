// Pure card logic, runnable without a signed-in Claude host. Use the installed
// TypeScript dev dependency, or set SECRETHANDOFF_TEST_TYPESCRIPT to its module.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';

const require = createRequire(import.meta.url);
const ts = require(process.env.SECRETHANDOFF_TEST_TYPESCRIPT || 'typescript');
const source = await readFile(new URL('../hooks/card.tsx', import.meta.url),'utf8');
const compiled = ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React,target:ts.ScriptTarget.ES2022}}).outputText;
const scope = {exports:{}};
vm.runInNewContext(compiled, scope);
const {statusOf, resultState, toolKind, cardOf, bandText} = scope.exports;

test('Claude card prefers structured state and preserves prose compatibility', () => {
  for (const [state,tone] of [['ready','ok'],['pending','wait'],['confirmation_required','wait'],['declined','stop'],['cancelled','stop'],['expired','stop'],['forgotten','stop'],['missing','stop'],['error','error']]) assert.equal(statusOf('request_secret',false,false,false,'Unrelated wording.',{status:state,presentation:'browser_page'}).tone,tone);
  assert.equal(statusOf('request_secret',false,false,false,'X is ready.',{status:'cancelled'}).tone,'stop');
  assert.equal(statusOf('request_secret',false,false,false,'X is ready.').tone,'ok');
  assert.match(statusOf('wait_for_secret',false,false,false,'Waiting for the user to fill X on their other device.').text,/other device/);
  assert.equal(statusOf('request_secret',false,true,false,'X is ready.',{status:'ready'}).tone,'error');
  assert.equal(statusOf('request_secret',false,false,true,'X is ready.',{status:'ready'}).tone,'stop');
  assert.match(statusOf('request_secret',true,false,false,'').text,/Waiting for Secret Handoff/);
  assert.match(statusOf('wait_for_secret',false,false,false,'',{status:'pending',presentation:'remote_link'}).text,/other device/);
});

test('wait cards identify existing requests without inventing a reason or policy', () => {
  assert.equal(toolKind('mcp__secrethandoff__wait_for_secret'),'wait_for_secret');
  assert.equal(toolKind('mcp__plugin_secrethandoff_secrethandoff__wait_for_secret'),'wait_for_secret');
  const card = cardOf('wait_for_secret',{name:'TEST_TOKEN'},{tone:'wait',text:'Waiting.'});
  assert.equal(card.title,'Wait for TEST_TOKEN');
  assert.equal(card.rows.length,0);
});

test('the host output supplies state only through structuredContent', () => {
  const state={status:'ready'};
  assert.equal(resultState({structuredContent:state}),state);
  assert.equal(resultState([{type:'text',text:'X is ready.'}]),undefined);
});

test('command cards identify the folder and avoid guessing the approval surface', () => {
  assert.equal(statusOf('run_with_secret',true,false,false,'').text,'Waiting for your command approval.');
  const card=cardOf('run_with_secret',{command:['true'],secrets:['TEST_TOKEN:X'],dir:'/tmp'},{tone:'wait',text:'Waiting.'});
  assert.equal(card.rows.find(r=>r.label==='Folder').value,'/tmp');
  assert.match(statusOf('run_with_secret',false,false,false,'exit code: 0',{status:'command_finished',presentation:'client_permission'}).text,/Exit code 0/);
  assert.match(statusOf('run_with_secret',false,false,false,'Waiting for the user to approve the command in their browser.').text,/browser/);
  assert.match(bandText({kind:'run_with_secret',command:'true'}),/outside this status card/);
});

test('command cards show execution outcomes when compatibility text is absent', () => {
  const read=(data,error=false)=>statusOf('run_with_secret',false,error,false,'',data);
  for (const [code,tone] of [[0,'ok'],[7,'error']]) {
    const result=read({status:'command_finished',executed:true,exit_code:code},code!==0);
    assert.equal(result.tone,tone);
    assert.equal(result.text,`The command ran. Exit code ${code}.`);
  }
  assert.match(read({status:'command_finished',executed:true,exit_code:-1,timed_out:true},true).text,/timed out/);
  assert.match(read({status:'command_finished',executed:true,exit_code:-1,cancelled:true},true).text,/cancelled and stopped/);
  for (const [state,tone] of [['command_pending','wait'],['command_denied','stop'],['command_expired','stop'],['command_cancelled','stop'],['command_not_started','error']]) assert.equal(read({status:state,executed:false},state==='command_not_started').tone,tone);
  assert.match(read({status:'command_not_started',message:'Missing executable.'},true).text,/Missing executable/);
});
