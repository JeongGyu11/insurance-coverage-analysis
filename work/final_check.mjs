import {Workbook,SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load('outputs/ABL생명_2507_담보분석.xlsx'));
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:2000})).ndjson);
console.log((await w.inspect({kind:'table',range:'담보데이터!A648:D651',tableMaxRows:4,tableMaxCols:4,maxChars:1800})).ndjson);
