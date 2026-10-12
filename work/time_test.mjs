import {Workbook} from '@oai/artifact-tool';
const w=Workbook.create(),s=w.worksheets.add('Test');
s.getRange('A1:A4').setNumberFormat('@');
s.getRange('A1:A4').values=[['2026-10-06 10:58:52+09:00'],['2026-10-06 10:58:52 +09:00'],['2026-10-06T10:58:52+09:00'],['2026-10-06T10:58:52+0900']];
console.log((await w.inspect({kind:'table',range:'Test!A1:A4',tableMaxRows:4,maxChars:1500})).ndjson);
