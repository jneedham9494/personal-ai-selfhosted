---
type: corrections
created: 2025-11-09
status: active
priority: high
category: obsidian-setup
tags: [corrections, documentation, plugins]
---

# ⚠️ Plugin Setup Guide - Corrections & Clarifications

After verifying official documentation, here are the corrections needed for the Obsidian Plugins Q4 Setup Guide.

---

## ✅ Verified Correct

These sections are accurate based on official docs:

### Dataview
- ✅ JavaScript queries ARE supported
- ✅ Configuration settings correct (Enable JS Queries, Inline JS Queries)
- ✅ Query syntax examples are valid

### Templater
- ✅ `tp.date.now("YYYY-MM-DD")` syntax is correct
- ✅ Date formatting using moment.js patterns is accurate
- ✅ Configuration paths correct

### Meta Bind
- ✅ `INPUT[toggle:field]` syntax is correct
- ✅ Buttons use YAML code blocks (meta-bind-button language)
- ✅ Input fields bind to frontmatter properties

### Periodic Notes
- ✅ Requires Calendar + Natural Language Dates plugins
- ✅ Auto-creates daily/weekly/monthly notes
- ✅ Configuration settings accurate

---

## ❌ Corrections Needed

### 1. Tasks Plugin - Emoji Format

**INCORRECT in guide:**
```markdown
- [ ] JCC Workout - Push Day 📅 2025-11-10 🔁 every Monday
```

**CORRECT format (verified from official docs):**
```markdown
- [ ] JCC Workout - Push Day 📅 2025-11-10 🔁 every Monday
```

**Key Points:**
- Due date emoji: 📅 (correct)
- Scheduled date emoji: ⏳ (not mentioned in guide - should add)
- Start date emoji: 🛫 (not mentioned in guide - should add)
- Recurrence emoji: 🔁 (correct)
- Done date emoji: ✅ (not mentioned in guide - should add)
- Priority emojis: ⏫ (high), 🔼 (medium), 🔽 (low)

**Emoji Shortcodes (for easy typing):**
- `:date:` = 📅
- `:hourglass_flowing_sand:` = ⏳
- `:flight_departure:` = 🛫
- `:repeat:` = 🔁
- `:white_check_mark:` = ✅

**Complete Example:**
```markdown
- [ ] Weekly Review 🛫 2025-11-16 📅 2025-11-16 🔁 every Sunday ⏫
```
(Start on Sunday, due on Sunday, recurs weekly, high priority)

**What I missed:**
- Scheduled date (⏳) for tasks you want to work on but not due yet
- Start date (🛫) for tasks that can't start until a certain date
- Priority markers
- Done date (✅) auto-added when task completed

---

### 2. Advanced Progress Bars - Syntax

**INCORRECT in guide:**
````markdown
```progress
title: Fitness Progress
current: 12
max: 100
percentage: true
color: green
```
````

**CORRECT syntax (verified from official docs):**
````markdown
```apb
Fitness Progress: 12/100
```
````

**Key Differences:**
1. Code block language is `apb` NOT `progress`
2. Format is `Title: Value/Total` on a single line
3. No YAML parameters like `current:`, `max:`, `percentage:`, `color:`
4. Much simpler syntax!

**Multiple Bars:**
````markdown
```apb
Fitness Progress: 12/100
XRPL Learning: 8/100
Finance Tracking: 5/100
Digital Privacy: 10/100
```
````

**Date-Based Progress Bars:**
````markdown
```apb
Q4 Goal Period: 2025-11-08||2025-12-31
```
````
- Uses `YYYY-MM-DD||YYYY-MM-DD` format
- Tracks days between dates
- Updates automatically

**What I got wrong:**
- Completely wrong syntax structure
- Wrong code block language
- Non-existent parameters

**Impact:** HIGH - The examples in the guide won't work at all

---

### 3. Obsidian Tracker - Clarifications

**My example in guide:**
````markdown
```tracker
searchType: tag
searchTarget: workout
folder: Daily-Notes
startDate: 2025-11-08
endDate: 2025-12-31
line:
    title: Workout Frequency
    yAxisLabel: Workouts
    lineColor: green
```
````

**Status:** MOSTLY CORRECT but needs clarification

**Required Parameters:**
- `searchType` (tag|frontmatter|wiki|text|dvField|table|task|fileMeta)
- `searchTarget` (what to search for)
- At least ONE output type: line|bar|summary|bullet|month|pie

**Verified SearchTypes:**
1. **tag** - Searches for `#tagName` or `#tagName:value`
2. **frontmatter** - Searches frontmatter properties
3. **text** - Uses regex patterns like `walked\s+(?<value>[0-9]+)\s+steps`
4. **task** - Searches task content
5. **dvField** - Dataview inline fields
6. **table** - Data from tables
7. **fileMeta** - File metadata (size, creation date, etc.)

**Better Example (Tag-based):**
````markdown
```tracker
searchType: tag
searchTarget: workout
folder: Daily-Notes
startDate: 2025-11-08
endDate: 2025-12-31
month:
    mode: circle
    color: green
    showCircle: true
    threshold: 1
```
````

**Better Example (Text with Regex):**
````markdown
```tracker
searchType: text
searchTarget: 'workout time:\s+(?<value>[0-9]+)\s+minutes'
folder: Daily-Notes
line:
    title: Workout Duration (minutes)
    lineColor: green
    showPoint: true
```
````

Then in daily notes:
```markdown
workout time: 90 minutes #workout
```

**What needs clarification:**
- SearchType options are broader than I showed
- Regex patterns are powerful for extracting values from text
- Month view has specific parameters (mode, threshold, showCircle)
- Tags can have values: `#workout:90` means workout = 90 (minutes)

---

### 4. Heatmap Tracker vs Obsidian Tracker

**Issue in guide:** I confused TWO different plugins

**Plugin 1: Heatmap Tracker (by mokkiebear)**
- NEW plugin (Nov 2024)
- Syntax uses frontmatter properties:
````markdown
```heatmap-tracker
property: <frontmatter_property_key>
```
````

**Plugin 2: Obsidian Tracker (by pyrochlore)**
- Established plugin (v1.15+)
- Syntax as shown above with searchType/searchTarget

**What I got wrong:**
- Mixed up two different plugins
- Showed Tracker syntax but called it Heatmap Tracker in some places

**Recommendation:**
Use **Obsidian Tracker** (pyrochlore) - It's more mature, has more features, and extensive documentation with 26+ examples in the GitHub repo.

---

## 📝 Additional Findings

### Charts View Plugin

**Status:** NOT VERIFIED - Could not access complete documentation

**What I showed:**
````markdown
```chart
type: line
labels: [Week 1, Week 2, Week 3, Week 4]
series:
  - title: Screen Time (hours/day)
    data: [10, 8, 6, 5]
```
````

**Confidence Level:** MEDIUM - Syntax looks right based on community examples, but couldn't verify against official docs

**Recommendation:** Test this syntax after installing, may need adjustments

---

### Super Simple Time Tracker

**Status:** NOT FULLY VERIFIED

**What I showed:**
````markdown
```simple-time-tracker
{
  "entries": [
    {"name": "Workout", "startTime": "07:00", "endTime": "08:30"}
  ]
}
```
````

**Confidence Level:** LOW - This might not be the correct JSON structure

**Need to verify:**
- Exact JSON schema
- Whether it's manual entries or start/stop buttons
- How to query total time across multiple notes

**Recommendation:** Check plugin after installation before relying on this syntax

---

## 🎯 Priority Corrections for Guide

### Critical (Fix Immediately):
1. ✅ Advanced Progress Bars syntax - **COMPLETELY WRONG**
2. ✅ Tasks plugin - Add missing emojis (⏳, 🛫, ✅, priority)
3. ⚠️ Clarify Heatmap Tracker vs Obsidian Tracker

### Important (Fix Soon):
4. ⚠️ Verify Charts View syntax with actual installation
5. ⚠️ Verify Super Simple Time Tracker JSON structure
6. ℹ️ Add more Obsidian Tracker examples (text regex, multiple targets)

### Nice to Have:
7. ℹ️ Add link to Obsidian Tracker examples folder (26 working examples)
8. ℹ️ Add emoji shortcode reference for Tasks plugin
9. ℹ️ Expand Meta Bind button examples

---

## ✏️ Corrected Dashboard Example

Here's a corrected version of the Q4 Goals Dashboard with accurate syntax:

````markdown
---
type: dashboard
tags: [Q4-2025, dashboard, tracking]
---

# 🎯 Q4 Goals Dashboard

**Last Updated:** `= date(today)`

---

## 📊 100-Hour Tracker

```apb
Fitness (Workouts + Movement): 12/100
XRPL Learning & Development: 8/100
Finance (Tracking + Learning): 5/100
Digital Privacy Projects: 10/100
```

---

## 📅 This Week's Tasks

```tasks
not done
due after yesterday
due before in 7 days
group by due
```

---

## 🏋️ Workout Consistency (Last 60 Days)

```tracker
searchType: tag
searchTarget: workout
folder: Daily-Notes
startDate: 2025-11-08
endDate: 2025-12-31
month:
    mode: circle
    color: green
    showCircle: true
    threshold: 1
    dimNotInMonth: false
```

**How to use:** Add `#workout` to daily notes on workout days

---

## 📱 Screen Time Trend

⚠️ **Note:** Charts View syntax needs verification after installation

```chart
type: line
labels: [Week 1, Week 2, Week 3, Week 4, Week 5, Week 6, Week 7, Week 8]
series:
  - title: Daily Screen Time (avg)
    data: [10, 8.5, 7, 6, 5.5, 5, 4.5, 4]
  - title: Goal (<5h)
    data: [5, 5, 5, 5, 5, 5, 5, 5]
tension: 0.3
width: 100%
legendPosition: bottom
```

---

## 💰 Expense Tracking Streak

```apb
Consecutive Days Tracking: 14/60
```

**Target:** 60 days (Nov 8 - Dec 31)

---

## 📈 Weekly Progress Summary

```dataview
TABLE WITHOUT ID
  file.link as "Week",
  workouts as "Workouts",
  xrpl_hours as "XRPL (h)",
  expense_days as "$ Days",
  screen_time_avg as "Screen (h)"
FROM "Weekly-Reviews"
WHERE date(file.name) >= date(today) - dur(8 weeks)
SORT file.name DESC
LIMIT 8
```

---
````

---

## 🔗 Official Documentation Links

### Verified Correct:
- **Dataview:** https://blacksmithgu.github.io/obsidian-dataview/
- **Templater:** https://silentvoid13.github.io/Templater/
- **Meta Bind:** https://www.moritzjung.dev/obsidian-meta-bind-plugin-docs/
- **Tasks:** https://publish.obsidian.md/tasks/ (couldn't load full content but structure verified)

### Need Verification:
- **Charts View:** https://github.com/caronchen/obsidian-chartsview-plugin
- **Super Simple Time Tracker:** (plugin page in Obsidian community)
- **Advanced Progress Bars:** https://cactuzhead.github.io/Advanced-Progress-Bars/

### Recommended Reading:
- **Obsidian Tracker Examples:** https://github.com/pyrochlore/obsidian-tracker/tree/master/examples (26 working examples with data)
- **Obsidian Tracker Docs:** https://github.com/pyrochlore/obsidian-tracker/blob/master/docs/

---

## 🚀 Next Steps

1. **Update main guide** with corrected Advanced Progress Bars syntax
2. **Expand Tasks plugin section** with all emoji options
3. **Test Charts View** syntax after installation
4. **Test Super Simple Time Tracker** and document actual syntax
5. **Add note** about Heatmap Tracker vs Obsidian Tracker distinction
6. **Link to official examples** for Obsidian Tracker (GitHub repo)

---

## 💡 Lessons Learned

1. **Always verify against official docs** - Not community posts or forum examples
2. **Test before documenting** - Some plugins have changed syntax over versions
3. **Link to source docs** - So users can verify if unsure
4. **Note confidence level** - Be transparent about what's verified vs assumed
5. **Plugin names matter** - Multiple plugins with similar names (Tracker vs Heatmap Tracker)

---

*Last verified: 2025-11-09*
*Verification method: Official documentation web fetches*
*Confidence: High for corrected sections, Medium for Charts View, Low for Time Tracker*
