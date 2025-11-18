---
type: reference
created: 2025-11-09
status: active
priority: high
category: obsidian-setup
tags: [Q4-2025, obsidian, plugins, productivity, automation]
related: [Life-Organization-System, Q4-Success-Framework]
---

# 🔌 Obsidian Plugins - Q4 Setup Guide

This guide contains recommended Obsidian plugins to supercharge your Q4 goal system with automation, visual tracking, and accountability features.

> **✅ Documentation Verified:** 2025-11-09
> - Core plugins (Dataview, Templater, Tasks, Meta Bind, Periodic Notes): Syntax verified against official docs
> - Advanced Progress Bars, Obsidian Tracker: Syntax corrected and verified
> - Charts View, Time Tracker: Syntax needs testing after installation
>
> See [[Plugin-Setup-Corrections]] for detailed verification notes and confidence levels

---

## 🎯 Installation Priority

Install in this order for best results:

### **Phase 1: Core Foundation** (Install First)
1. Dataview - Database queries for dashboards
2. Templater - Advanced template automation
3. Periodic Notes - Auto-create daily/weekly notes
4. Calendar - Visual date navigation

### **Phase 2: Tracking & Accountability** (Install Week 1)
5. Tasks - Recurring task management
6. Obsidian Tracker - Habit heatmaps
7. Meta Bind - Interactive buttons and inputs
8. Super Simple Time Tracker - 100-hour tracking

### **Phase 3: Visualization** (Install Week 2)
9. Advanced Progress Bars - Visual goal tracking
10. Charts View - Data visualization
11. Heatmap Calendar - GitHub-style activity tracking
12. Kanban - Project board view

### **Phase 4: Nice-to-Have** (Optional)
13. Reminder - In-app notifications (desktop only)
14. Full Calendar - Calendar integration (you already have this)
15. Habit Tracker 21 - Additional habit visualization

---

## 📦 Essential Plugins (Phase 1)

### 1. Dataview ⭐⭐⭐⭐⭐

**Why You Need It:**
Powers all dashboards and automated tracking. Think of it as a database for your vault.

**Installation:**
Settings → Community Plugins → Browse → Search "Dataview" → Install → Enable

**Configuration:**
Settings → Dataview:
- ✅ Enable JavaScript Queries
- ✅ Enable Inline JavaScript Queries
- ✅ Enable Inline Queries

**Use Cases for Your Q4 Goals:**
- Auto-generate weekly workout summaries
- Track expense entries across daily notes
- Calculate total hours toward 100-hour tracker
- Show all incomplete tasks for today

**Sample Query for Daily Dashboard:**
```dataview
TABLE WITHOUT ID
  file.link as "Date",
  energy_level as "Energy",
  mood as "Mood",
  habits_completed as "Habits"
FROM "Daily-Notes"
WHERE date(file.name) >= date(today) - dur(7 days)
SORT file.name DESC
```

---

### 2. Templater ⭐⭐⭐⭐⭐

**Why You Need It:**
Automates template creation with dynamic content (dates, calculations, custom scripts).

**Installation:**
Settings → Community Plugins → Browse → "Templater"

**Configuration:**
Settings → Templater:
- Template folder location: `Templates/`
- ✅ Trigger Templater on new file creation
- ✅ Enable System Commands
- Syntax highlighting: ✅ Enabled

**Use Cases:**
- Auto-populate daily notes with yesterday's habits
- Calculate week number for weekly reviews
- Pre-fill workout templates based on day of week
- Auto-link related project files

**Sample Template Code (for Daily Note):**
```
---
date: <% tp.date.now("YYYY-MM-DD") %>
day_of_week: <% tp.date.now("dddd") %>
week: W<% tp.date.now("WW") %>
energy_level:
mood:
---

# <% tp.date.now("dddd, MMMM DD, YYYY") %>

## Quick Links
- Yesterday: [[<% tp.date.yesterday("YYYY-MM-DD-dddd") %>]]
- Tomorrow: [[<% tp.date.tomorrow("YYYY-MM-DD-dddd") %>]]
- This Week: [[Weekly-Plan]]
```

---

### 3. Periodic Notes ⭐⭐⭐⭐⭐

**Why You Need It:**
Auto-creates daily, weekly, monthly notes on schedule. Essential for your Q4 system.

**Installation:**
Requires: Calendar plugin + Natural Language Dates
Then install: Periodic Notes

**Configuration:**
Settings → Periodic Notes:

**Daily Notes:**
- Format: `YYYY-MM-DD-dddd`
- Template: `Templates/Daily-Note.md`
- Folder: `Daily-Notes/`
- ✅ Open daily note on startup

**Weekly Notes:**
- Format: `YYYY-[W]WW-Weekly-Review`
- Template: `Templates/Weekly-Review.md`
- Folder: `Weekly-Reviews/`
- Week starts: Sunday

**Use Cases:**
- Auto-create Sunday weekly review notes
- Never manually create daily notes again
- Consistent naming = easier Dataview queries

---

### 4. Calendar ⭐⭐⭐⭐

**Why You Need It:**
Visual date picker, works with Periodic Notes for quick navigation.

**Installation:**
Settings → Community Plugins → "Calendar"

**Configuration:**
- ✅ Show week number
- First day of week: Sunday
- Dots on calendar: Show task counts

**Use Cases:**
- Quick jump to any daily note
- See which days you have content
- Visual weekly overview

---

## 🎯 Tracking & Accountability (Phase 2)

### 5. Tasks ⭐⭐⭐⭐⭐

**Why You Need It:**
Manages recurring tasks (gym Mon/Wed/Fri, expense tracking daily, etc.)

**Installation:**
Community Plugins → "Tasks"

**Configuration:**
Settings → Tasks:
- ✅ Set done date on every completed task
- ✅ Remove global filter (to see all tasks)
- Recurring tasks: Create on completion ✅
- Date format: `YYYY-MM-DD`

**Task Emoji Reference:**
- 📅 **Due date** (`:date:`) - When task must be completed
- ⏳ **Scheduled date** (`:hourglass_flowing_sand:`) - When you plan to work on it
- 🛫 **Start date** (`:flight_departure:`) - Earliest date task can begin
- 🔁 **Recurrence** (`:repeat:`) - How often task repeats
- ✅ **Done date** (`:white_check_mark:`) - Auto-added when completed
- ⏫ **High priority** | 🔼 **Medium** | 🔽 **Low priority**

**Task Format Examples:**
```markdown
# Basic recurring tasks
- [ ] JCC Workout - Push Day 📅 2025-11-10 🔁 every Monday
- [ ] Track expenses 📅 2025-11-09 🔁 every day
- [ ] XRPL Coding Session 📅 2025-11-11 🔁 every Tuesday, Thursday
- [ ] Weekly Review 📅 2025-11-16 🔁 every Sunday ⏫

# Using scheduled vs due dates
- [ ] Start XRPL Project #1 🛫 2025-11-11 📅 2025-11-15
  (Can't start until Tue, due by Fri)
- [ ] Review meal plan ⏳ 2025-11-13 📅 2025-11-14
  (Scheduled Wed, due Thu)

# With priorities
- [ ] Delete Twitter/YouTube apps 📅 2025-11-10 ⏫
- [ ] Set up expense tracker 📅 2025-11-10 🔼
- [ ] Watch comedy special 📅 2025-11-16 🔽
```

**Emoji Shortcodes (for easy typing):**
Type these in Obsidian: `:date:`, `:repeat:`, `:hourglass_flowing_sand:`

**Query for Today's Tasks:**
```tasks
not done
due today
group by heading
```

**Integration with Your System:**
Add this to your Daily Note template:
```
## ⏰ Recurring Commitments
\```tasks
not done
due today
path includes Active-Week
\```
```

---

### 6. Obsidian Tracker ⭐⭐⭐⭐

**Why You Need It:**
Creates GitHub-style heatmaps for habit tracking. Perfect for visualizing your 4x/week gym consistency.

**Installation:**
Community Plugins → "Tracker"

**Use Cases:**
- Workout frequency heatmap (see 4x/week pattern)
- Screen time reduction visualization
- Expense tracking streak

**Example Tracker (for Fitness Dashboard):**
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

**For Your Daily Note:**
Add to workout section:
```markdown
**Post-Workout:**
- [ ] Total workout time: ___ minutes #workout
- [ ] Calories burned: ___ (est) #fitness-stats
```

Then create a dashboard note with tracker queries to visualize patterns.

---

### 7. Meta Bind ⭐⭐⭐⭐

**Why You Need It:**
Interactive buttons and inputs. Click to update habit status, increment time trackers, mark workouts complete.

**Installation:**
Community Plugins → "Meta Bind"

**Configuration:**
Run command: "Open Meta Bind Playground" to see examples

**Use Cases for Q4 Goals:**

**100-Hour Tracker Buttons:**
```meta-bind-button
label: +1 Hour (Fitness)
action:
  type: updateMetadata
  bindTarget: fitness_hours
  evaluate: true
  value: x + 1
```

**Habit Toggle:**
```markdown
Morning Phone-Free: `INPUT[toggle:phone_free_morning]`
Digital Sunset: `INPUT[toggle:digital_sunset]`
```

**Energy Level Slider:**
```markdown
Energy (1-5): `INPUT[slider(defaultValue(3), minValue(1), maxValue(5)):energy_level]`
```

**Integration Example (Daily Note):**
```markdown
## 📊 Daily Metrics
- **Energy Level:** `INPUT[slider(defaultValue(3), minValue(1), maxValue(5)):energy_level]`
- **Mood:** `INPUT[select(option(😊, Happy), option(😐, Neutral), option(😔, Low)):mood]`
- **Workout Done:** `INPUT[toggle:workout_completed]`
```

---

### 8. Super Simple Time Tracker ⭐⭐⭐⭐

**Why You Need It:**
Start/stop timers for tracking hours toward your 100-Hour Rule.

**Installation:**
Community Plugins → "Super Simple Time Tracker"

**Use Cases:**
- Track XRPL coding sessions
- Log gym workout duration
- Monitor privacy project time
- Financial learning time

**Usage in Daily Notes:**
````markdown
## 🏋️ Fitness Session

```simple-time-tracker
{
  "entries": [
    {"name": "Workout", "startTime": "07:00", "endTime": "08:30"}
  ]
}
```

**Total:** 1.5 hours → Add to Fitness 100-Hour Tracker
````

**Weekly Summary Query:**
Create a weekly note section that uses Dataview to sum all time tracker entries.

---

## 📊 Visualization (Phase 3)

### 9. Advanced Progress Bars ⭐⭐⭐⭐

**Why You Need It:**
Visual progress toward your 100-hour goals, workout targets, expense tracking days.

**Installation:**
Community Plugins → "Advanced Progress Bars"

**Usage Examples:**

**Syntax:** `Title: Value/Total` (one per line)

**100-Hour Tracker:**
````markdown
## 🎯 Q4 Progress Dashboard

```apb
Fitness Progress: 12/100
XRPL Coding Hours: 8/100
Expense Tracking Streak: 14/30
Digital Privacy Projects: 10/100
```
````

**Date-Based Progress Bar:**
````markdown
```apb
Q4 Goal Period: 2025-11-08||2025-12-31
```
````
Uses `YYYY-MM-DD||YYYY-MM-DD` format, automatically calculates days elapsed.

**Integration with Meta Bind:**
Combine with Meta Bind buttons to increment progress bars with one click!

---

### 10. Charts View ⭐⭐⭐⭐

**Why You Need It:**
Create beautiful charts from your Dataview data. Visualize screen time reduction, workout frequency, expense trends.

**Installation:**
Community Plugins → "Charts View"

**Use Cases:**

**Screen Time Reduction Chart:**
````markdown
```chart
type: line
labels: [Week 1, Week 2, Week 3, Week 4]
series:
  - title: Screen Time (hours/day)
    data: [10, 8, 6, 5]
  - title: Goal
    data: [5, 5, 5, 5]
tension: 0.2
width: 80%
```
````

**Workout Frequency Bar Chart:**
````markdown
```chart
type: bar
labels: [Week 1, Week 2, Week 3, Week 4, Week 5, Week 6, Week 7, Week 8]
series:
  - title: Workouts Completed
    data: [3, 4, 4, 4, 4, 3, 4, 4]
  - title: Goal (4/week)
    data: [4, 4, 4, 4, 4, 4, 4, 4]
```
````

**Expense Tracking Pie Chart:**
````markdown
```chart
type: pie
labels: [Food, Transport, Entertainment, Subscriptions, Other]
data: [400, 150, 100, 80, 120]
```
````

---

### 11. Heatmap Calendar ⭐⭐⭐

**Why You Need It:**
GitHub-style contribution graph for daily habits. Shows your consistency at a glance.

**Installation:**
Community Plugins → "Heatmap Calendar"

**Usage:**
````markdown
```heatmap-calendar
title: Workout Consistency (Q4 2025)
dataviewQuery: |
  TABLE WITHOUT ID
    file.day as date,
    length(file.tasks.completed) as value
  FROM "Daily-Notes"
  WHERE contains(file.tags, "#workout")
startDate: 2025-11-08
endDate: 2025-12-31
```
````

**Shows:**
- Dark green = Workout completed
- Light green = Partial activity
- Gray = No workout
- Visual pattern of 4x/week consistency

---

### 12. Kanban ⭐⭐⭐

**Why You Need It:**
Visual board for managing your 4 Q4 goals and sub-projects.

**Installation:**
Community Plugins → "Kanban"

**Use Cases:**

**Privacy Projects Board:**
Create note: `Digital-Privacy-Kanban.md`
````markdown
---
kanban-plugin: board
---

## 📋 To Do

- [ ] Project #00: Gmail Login Migration
- [ ] Project #02: Data Broker Removal
- [ ] Project #05: Browser Hardening


## 🏗️ In Progress

- [ ] Delete Twitter/YouTube apps
- [ ] Set up Screen Time limits


## ✅ Done

- [x] Research privacy projects
- [x] Create Digital Wellness goal doc

````

**Q4 Goals Overview Board:**
- Column 1: Not Started
- Column 2: Foundation (Week 1-2)
- Column 3: Building Momentum (Week 3-5)
- Column 4: Refinement (Week 6-8)
- Column 5: Complete

Drag cards between columns as you progress!

---

## 🔔 Nice-to-Have (Phase 4)

### 13. Reminder ⭐⭐⭐

**Why You Need It:**
In-app notifications for time-sensitive tasks.

**Limitations:**
- ⚠️ Only works when Obsidian is open
- ⚠️ Desktop only (not mobile push notifications)

**Installation:**
Community Plugins → "Reminder"

**Usage Format:**
```markdown
- [x] JCC Workout (@2025-11-10 06:45)
- [x] Digital Sunset - Put phone away (@2025-11-09 21:00)
- [ ] Weekly Review (@2025-11-16 10:00)
```

**Best Practice:**
Use Apple Calendar for true mobile reminders (from earlier discussion), but Reminder plugin works great when working in Obsidian.

---

## 🎯 Recommended Dashboard Setup

Create: `Dashboards/Q4-Goals-Dashboard.md`

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
Q4 Goal Period: 2025-11-08||2025-12-31
```

**Update Instructions:** Edit these numbers weekly during Sunday review

---

## 📅 This Week's Tasks

```tasks
not done
due after yesterday
due before in 7 days
group by due
```

---

## 🏋️ Workout Consistency (Last 30 Days)

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

**How to use:** Add `#workout` tag to daily notes on workout days

---

## 📱 Screen Time Trend

⚠️ **Note:** Charts View syntax below - verify after installation

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

```progress
title: Consecutive Days Tracking
current: 14
max: 60
percentage: true
color: orange
```

**Current Streak:** 14 days | **Target:** 60 days (Nov 8 - Dec 31)

---

## 🧠 Anti-Quit System Status

**Quit Urges This Week:** 0
**72-Hour Rule Used:** 0 times
**Stealth Mode Status:** ✅ Active (No public sharing)

**Days Until 100 Hours (Minimum Commitment):**
- Fitness: ~88 days (4h/week pace)
- XRPL: ~92 days (3h/week pace)
- Finance: ~95 days (2h/week pace)
- Privacy: ~90 days (5h/week pace)

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

## ⚠️ System Health Checks

**Time Management:**
- [ ] Phone-free mornings (6-7am): ___/7 days
- [ ] Digital sunset (9pm): ___/7 nights
- [ ] Sunday review completed: ___

**Anti-Quit:**
- [ ] Updated 100-Hour Tracker: ___
- [ ] Still in Stealth Mode: ___
- [ ] No impulse quits: ___

**Enneagram Awareness:**
- [ ] Noticed comparison urges: ___ times
- [ ] Used daily mantra: ___/7 days
- [ ] Competed with self (not others): ___

---

*Dashboard auto-updates via Dataview queries*
*Manual progress bars: Update weekly during Sunday review*
````

---

## 🚀 Quick Setup Checklist

Copy this checklist to a new note and check off as you install:

### Week 1: Foundation
- [ ] Install Dataview
- [ ] Install Templater
- [ ] Install Periodic Notes + Calendar + Natural Language Dates
- [ ] Configure daily note auto-creation
- [ ] Test: Does daily note auto-create tomorrow morning?

### Week 1: Tracking
- [ ] Install Tasks plugin
- [ ] Convert recurring commitments to Tasks format
- [ ] Add Tasks query to daily note template
- [ ] Install Super Simple Time Tracker
- [ ] Add time tracker blocks to daily notes

### Week 2: Visualization
- [ ] Install Advanced Progress Bars
- [ ] Create Q4 Goals Dashboard with progress bars
- [ ] Install Obsidian Tracker
- [ ] Add workout heatmap to fitness dashboard
- [ ] Install Charts View
- [ ] Create screen time reduction chart

### Week 2: Interactivity
- [ ] Install Meta Bind
- [ ] Run "Open Meta Bind Playground" command
- [ ] Add habit toggles to daily note template
- [ ] Create 100-hour tracker increment buttons
- [ ] Test: Click button to increment hours

### Week 3: Optional
- [ ] Install Heatmap Calendar for GitHub-style tracking
- [ ] Install Kanban for project board view
- [ ] Install Reminder for in-app notifications
- [ ] Customize dashboard layout

---

## 🎓 Learning Resources

**Dataview:**
- Official docs: https://blacksmithgu.github.io/obsidian-dataview/
- Example queries: Search "dataview examples" in Obsidian forum

**Templater:**
- Official docs: https://silentvoid13.github.io/Templater/
- Date formatting: https://momentjs.com/docs/#/displaying/format/

**Tasks:**
- Official docs: https://publish.obsidian.md/tasks/
- Recurring tasks: https://publish.obsidian.md/tasks/Getting+Started/Recurring+Tasks

**Meta Bind:**
- Official docs: https://www.moritzjung.dev/obsidian-meta-bind-plugin-docs/
- Playground: Run command in Obsidian

---

## 💡 Pro Tips

### Tip 1: Start Small
Don't install all plugins at once. Follow the phased approach:
- Week 1: Core foundation only
- Week 2: Add tracking
- Week 3: Add visualization
- This prevents overwhelm and lets you learn each plugin properly

### Tip 2: Mobile Limitations
Most advanced plugins work best on desktop. For mobile:
- ✅ Basic Dataview queries work
- ✅ Tasks queries work
- ❌ Charts may not render
- ❌ Meta Bind buttons limited
- ❌ Reminder notifications don't work

Use mobile for: Reading, basic task checking, quick notes
Use desktop for: Dashboard views, progress updates, weekly reviews

### Tip 3: Template Your Dashboards
Create reusable dashboard templates for:
- Daily goal check-in
- Weekly progress review
- Monthly deep dive
- Q4 final retrospective

### Tip 4: Automate Updates
Use Templater + Periodic Notes to auto-populate:
- Yesterday's uncompleted tasks → Today's note
- This week's hours → Weekly review template
- Month's totals → Monthly retrospective

### Tip 5: Backup Your Vault
With all these plugins, backup becomes critical:
- Use Obsidian Sync OR
- Use iCloud (you're already doing this) OR
- Use Git for version control

---

## 🆘 Troubleshooting

### "Plugin not working after install"
1. Settings → Community Plugins → Reload
2. Restart Obsidian
3. Check plugin settings (some need configuration)

### "Dataview query shows no results"
- Check folder path in FROM clause
- Verify frontmatter field names match exactly
- Use Dataview: Show Query Debug in settings

### "Tasks plugin not creating recurring tasks"
- Must mark current task complete to generate next occurrence
- Check date format: `📅 YYYY-MM-DD`
- Recurrence format: `🔁 every Monday`

### "Meta Bind buttons not working"
- Check syntax in "Open Meta Bind Playground"
- Verify frontmatter field exists in note
- Refresh note (Ctrl/Cmd + R)

### "Charts not rendering"
- Verify Charts View plugin installed AND enabled
- Check code block language: `chart` (not `charts`)
- Validate data array format

---

## 🔄 Integration with Personal AI Assistant

Your Telegram bot can interact with these plugins via:

**1. Conversation → Obsidian Auto-Save**
Bot already saves conversations. Enhance with:
```markdown
---
type: ai-conversation
date: 2025-11-09
tags: [ai-conversation, claude]
topics: [workout-planning, meal-prep]
mood: motivated
---

# AI Conversation - 2025-11-09

**Topics Discussed:** Workout planning, meal prep
**Key Insights:** Focus on compound movements, prep on Sunday
**Action Items:**
- [ ] Try 5x5 strength program 📅 2025-11-10
- [ ] Buy meal prep containers 📅 2025-11-11

[Conversation content...]
```

Now Dataview can query all workout-related conversations!

**2. Nudging → Task Creation**
Bot sends nudge → Creates task in today's daily note:
```markdown
- [ ] NUDGE: Have you logged today's expenses? 📅 2025-11-09 ⏰ 20:00
```

**3. Pattern Analysis → Dashboard Updates**
Bot detects quit-urge → Logs to tracking note:
```markdown
## 2025-11-09 - Quit Urge Detected
**Goal:** XRPL
**Trigger:** Code not working, frustration
**Response:** Used 72-Hour Rule ✅
**Status:** Urge passed, continued
```

Dashboard shows: "Quit Urges Successfully Navigated: 3"

---

## 📅 Next Steps

1. **This Week (Nov 9-15):**
   - [ ] Install Phase 1 plugins (Dataview, Templater, Periodic Notes, Calendar)
   - [ ] Configure daily note auto-creation
   - [ ] Test one Dataview query
   - [ ] Add Tasks format to recurring commitments

2. **Week 2 (Nov 16-22):**
   - [ ] Install Phase 2 plugins (Tasks, Tracker, Meta Bind, Time Tracker)
   - [ ] Create Q4 Goals Dashboard
   - [ ] Add progress bars for 100-hour tracking
   - [ ] Build workout heatmap

3. **Week 3 (Nov 23-29):**
   - [ ] Install Phase 3 plugins (Charts, Heatmap Calendar, Kanban)
   - [ ] Create screen time reduction chart
   - [ ] Build privacy projects Kanban board
   - [ ] Customize dashboard layout

4. **Week 4+ (Nov 30 onward):**
   - [ ] Refine queries based on actual use
   - [ ] Add automation scripts with Templater
   - [ ] Integrate with Personal AI Assistant bot
   - [ ] Share learnings (after Stealth Mode ends Week 8)

---

## 🎯 Success Metrics

**You'll know the setup is working when:**

1. ✅ Daily notes auto-create every morning
2. ✅ Dashboard shows accurate 100-hour progress
3. ✅ Heatmap shows your 4x/week workout pattern
4. ✅ Tasks automatically recur when you complete them
5. ✅ You can click a button to log hours (Meta Bind)
6. ✅ Charts visualize your screen time reduction trend
7. ✅ Sunday review takes 50% less time (auto-populated data)
8. ✅ You spend more time DOING goals, less time TRACKING goals

**Target:** 80% automation, 20% manual updates

---

*Last Updated: 2025-11-09*
*Next Review: After Phase 1 installation (Nov 15)*

---

## Quick Links

**Related Docs:**
- [[Life-Organization-System]] - Your overall life system
- [[Q4-Success-Framework]] - How systems integrate
- [[Quarterly-Goals-2025-Q4]] - Your Q4 goals

**Plugin Docs:**
- Dataview: https://blacksmithgu.github.io/obsidian-dataview/
- Templater: https://silentvoid13.github.io/Templater/
- Tasks: https://publish.obsidian.md/tasks/
- Meta Bind: https://www.moritzjung.dev/obsidian-meta-bind-plugin-docs/

**Community:**
- Obsidian Forum: https://forum.obsidian.md/
- r/ObsidianMD: https://reddit.com/r/ObsidianMD
