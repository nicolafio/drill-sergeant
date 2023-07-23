import * as readline from 'readline/promises';
import { stdin, stdout } from 'process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { readFile, writeFile } from 'fs/promises';

import ical from 'node-ical';
import StreamZip from 'node-stream-zip';
import { parse as parseCSV } from 'csv-parse/sync';

const SCRIPT_DIRECTORY = dirname(fileURLToPath(import.meta.url));
const CONFIG_FILE_LOCATION = join(SCRIPT_DIRECTORY, '.config-report-discipline.json');
const REPORT_FILE_LOCATION = join(SCRIPT_DIRECTORY, 'discipline-report.json')
const TIME_ZONE = 'Europe/London';
const T_MINUTES = 5;
const IMPORTANCE_FOR_STARTING_ON_TIME = 0.2;
const IMPORTANCE_FOR_STARTING_WITHIN_T_MINUTES = 0.1;
const IMPORTANCE_FOR_STARTING_ANY_TIME_IN_SCHEDULE = 0.1;
const IMPORTANCE_FOR_SPENDING_TIME =
    1 -
    IMPORTANCE_FOR_STARTING_ON_TIME -
    IMPORTANCE_FOR_STARTING_WITHIN_T_MINUTES -
    IMPORTANCE_FOR_STARTING_ANY_TIME_IN_SCHEDULE;


main();

class CommonEvent {
    constructor(startTimestamp, endTimestamp, issueReference = null) {
        this.start = new Date(startTimestamp);
        this.end = new Date(endTimestamp);
        this.issueReference = issueReference;
        this.durationMilliseconds = this.end - this.start;
        this.day = this.start.toLocaleString('en-US', {
            year: 'numeric',
            month: 'numeric',
            day: 'numeric',
            timeZone: TIME_ZONE
        });
    }

    includesDate(date) {
        return date > this.start && date < this.end;
    }

    overlapsWithEvent(event) {
        return event.includesDate(this.start) || event.includesDate(this.end);
    }
}

async function main() {
    let config;
    try {
        config = await readConfig();
    }
    catch (_) {
        config = await promptConfig();
        const json = JSON.stringify(config, null, 4)
        await writeFile(CONFIG_FILE_LOCATION, json);
    }
    const nowThenData = await readNowThenData(config.nowThenDataFileLocation);
    const iCalData = await ical.async.fromURL(config.iCalURL.replace('webcal://', 'https://'));

    const history =
        [...nowThenData.events.values()]
            .map(o => [o, getIssueReferenceFromNowThenEventData(o, nowThenData)])
            .filter(([_, issueRef]) => issueRef !== null)
            .map(([o, issueRef]) => new CommonEvent(o['Start Date'], o['End Date'], issueRef))
            .sort((a, b) => a.start - b.start);

    const schedule =
        Object.values(iCalData)
            .filter(isICalEvent)
            .map(o => [o, getIssueReferenceFromICalEventData(o)])
            .filter(([_, issueRef]) => issueRef !== null)
            .map(([o, issueRef]) => new CommonEvent(o.start, o.end, issueRef))
            .sort((a, b) => a.start - b.start);

    // Compute aggregate times
    
    const timesToSpendOnIssueOnGivenDayMilliseconds = new Map();
    const timesSpentOnIssueOnGivenDayMilliseconds = new Map();

    for (const events of [schedule, history]) {
        for (const { day, issueReference, durationMilliseconds } of events) {
            let cache;
            if (events === schedule) cache = timesToSpendOnIssueOnGivenDayMilliseconds;
            if (events === history) cache = timesSpentOnIssueOnGivenDayMilliseconds;
            
            if (!cache.has(day)) cache.set(day, new Map());
            
            const totalTimeForIssue = (cache.get(day).get(issueReference) || 0) + durationMilliseconds;
            
            cache.get(day).set(issueReference, totalTimeForIssue);
        }
    }

    // Compute timeliness

    const eventsStartedOnTime = new Set();
    const eventsStartedWithinTMinutes = new Set();
    const eventsStartedAnyTimeInSchedule = new Set();

    for (let i = 0, j = 0; i < schedule.length && j < history.length; schedule[i].end < history[j].end ? i++ : j++) {
        if (schedule[i].issueReference !== history[j].issueReference)
            continue;
        
        if (history[j].includesDate(schedule[i].start))
            eventsStartedOnTime.add(schedule[i]); 

        if (history[j].start <= schedule[i].start + T_MINUTES * 60 * 1000 && history[j].end > schedule[i].start)
            eventsStartedWithinTMinutes.add(schedule[i]);

        if (history[j].overlapsWithEvent(schedule[i]))
            eventsStartedAnyTimeInSchedule.add(schedule[i]);
    }

    // Compute discipline scores.

    const reports = {};

    for (const event of schedule) {
        if (!reports[event.day]) reports[event.day] = {};
        if (!reports[event.day].schedule) reports[event.day].schedule = [];
        reports[event.day].schedule.push(event);
    }

    for (const dayReport of Object.values(reports)) {
        const n = dayReport.schedule.length;

        dayReport.disciplineScore = 0;

        for (const event of dayReport.schedule) {        
            event.timeToSpendOnIssueMilliseconds = timesToSpendOnIssueOnGivenDayMilliseconds.get(event.day).get(event.issueReference);
            event.timeSpentOnIssueMilliseconds = timesSpentOnIssueOnGivenDayMilliseconds.get(event.day)?.get(event.issueReference) || 0;

            const timeCompleted = Math.min(1, event.timeSpentOnIssueMilliseconds / event.timeToSpendOnIssueMilliseconds);

            event.timePercentCompleted = Math.round(10000 * timeCompleted) / 100;
            event.startedOnTime = eventsStartedOnTime.has(event);
            event.startedWithinTMinutes = eventsStartedWithinTMinutes.has(event);
            event.startedWithinAnyTimeInSchedule = eventsStartedAnyTimeInSchedule.has(event);

            event.disciplineScore = IMPORTANCE_FOR_SPENDING_TIME * timeCompleted;
            if (event.startedOnTime) event.disciplineScore += IMPORTANCE_FOR_STARTING_ON_TIME;
            if (event.startedWithinTMinutes) event.disciplineScore += IMPORTANCE_FOR_STARTING_WITHIN_T_MINUTES;
            if (event.startedWithinAnyTimeInSchedule) event.disciplineScore += IMPORTANCE_FOR_STARTING_ANY_TIME_IN_SCHEDULE;

            dayReport.disciplineScore += event.disciplineScore / n;
        }
    }

    const reportsJSON = JSON.stringify(reports, null, 4);

    await writeFile(REPORT_FILE_LOCATION, reportsJSON);
}

function isICalEvent(iCalEntry) {
    return iCalEntry.type === 'VEVENT';
}

function getIssueReferenceFromNowThenEventData(nowThenEvent, nowThenData) {
    const task = nowThenData.tasks.get(nowThenEvent['TaskKey']);
    const match = task['Name'].match(/^((?:[a-z][a-z_0-9]*\/?)+#[1-9][0-9]*)\s/);
    if (match === null) return null;
    return match[1];
}

function getIssueReferenceFromICalEventData(iCalEvent) {
    return getIssueReferenceFromURL(iCalEvent.url?.val);    
}

function getIssueReferenceFromURL(issueURL) {
    if (typeof issueURL !== 'string') return null;
    const match = issueURL.match(/^https:\/\/git\.nook\.of\.nicolaf\.io\/(.*)\/issues\/([0-9]+)$/);
    if (match === null) return issueURL;
    const [_, projectPath, issueNumber] = match;
    const projectReference = projectPath.toLowerCase().replace(/\/-/g, '');
    return `${projectReference}#${issueNumber}`;
}

async function readNowThenData(fileLocation) {
    const zip = new StreamZip.async({ file: fileLocation });
    const eventsRead = readNowThenDataEntry(zip, 'events.csv');
    const tasksRead = readNowThenDataEntry(zip, 'tasks.csv');
    const [events, tasks] = await Promise.all([eventsRead, tasksRead]);
    return { events, tasks };
}

async function readNowThenDataEntry(zip, entryPath) {
    const csv = await zip.entryData(entryPath);
    const array = parseCSV(csv, { columns: true, skip_empty_lines: true });
    const entries = array.map(item => [item['Primary Key'], item])
    return new Map(entries);
}

async function readConfig() {
    const json = await readFile(CONFIG_FILE_LOCATION, { encoding: 'utf8' });
    return JSON.parse(json);
}

async function promptConfig() {
    const rl = readline.createInterface({ input: stdin, output: stdout });
    const iCalURL = await rl.question('Schedule calendar URL: ');
    const nowThenDataFileLocation = await rl.question('NowThen backup file location: ');
    rl.close();
    return { iCalURL, nowThenDataFileLocation };
}
