---
type: dashboard
tags: [Q4-2025, dashboard, tracking]
created: 2025-11-09
---

# 🎯 Q4 Goals Dashboard

**Last Updated:** 2025-11-09
**Q4 Period:** November 8 - December 31, 2025 (8 weeks)

---

## 📊 100-Hour Tracker

> **Note:** After installing Advanced Progress Bars plugin, these will show as visual progress bars.
> For now, showing as text format.

**Current Progress (Manual Update):**
- **Fitness:** 1.5 / 100 hours (1.5%)
- **XRPL Learning:** 0 / 100 hours (0%)
- **Finance:** 0.5 / 100 hours (0.5%)
- **Digital Privacy:** 0 / 100 hours (0%)
- **Q4 Days Elapsed:** 2 / 54 days (4%)

**Update Instructions:** Edit these numbers weekly during Sunday review

---

## 📅 Recent Daily Notes

```dataview
TABLE WITHOUT ID
  file.link as "Date",
  energy_level as "Energy",
  mood as "Mood",
  habits_completed as "Habits"
FROM "Daily-Notes"
WHERE file.name != "Daily-Notes"
SORT file.name DESC
LIMIT 7
```

**What this shows:** Last 7 daily notes with energy, mood, and habit completion

**If you see a blank box:**
- ✅ Dataview is installed and enabled
- ⚠️ Needs data: This query looks for files in `Daily-Notes/` folder with frontmatter fields

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
WHERE file.name != "Weekly-Reviews"
SORT file.name DESC
LIMIT 8
```

**What this shows:** Last 8 weekly reviews with goal metrics

---

## 🏋️ Workout Days This Week

```dataview
LIST
FROM "Daily-Notes"
WHERE contains(tags, "workout")
  AND date(file.name) >= date(today) - dur(7 days)
SORT file.name DESC
```

**What this shows:** Daily notes tagged with #workout in the last 7 days

**To use:** Add `#workout` tag to daily notes when you complete a workout

---

## ✅ Today's Completed Tasks

```dataview
TASK
WHERE completed
  AND date(file.name) = date(today)
FROM "Daily-Notes" OR "Active-Week"
```

**What this shows:** All completed tasks from today

---

## 📊 Habit Completion Rate (Last 7 Days)

```dataview
TABLE WITHOUT ID
  file.link as "Date",
  habits_completed as "Completed",
  round((habits_completed / 14) * 100, 0) + "%" as "Rate"
FROM "Daily-Notes"
WHERE habits_completed != null
SORT file.name DESC
LIMIT 7
```

**What this shows:** Daily habit completion rate (assuming 14 total habits per day)

---

## 🧠 Anti-Quit System Status

**Manual Tracking (Update Weekly):**

**Quit Urges This Week:** 0
**72-Hour Rule Used:** 0 times
**Stealth Mode Status:** ✅ Active (No public sharing)

**Days Until 100 Hours (at current pace):**
- Fitness: ~67 weeks remaining (need 1.5h/week → speed up to 4h/week!)
- XRPL: Not started (target: 3h/week)
- Finance: ~200 weeks remaining (need 0.5h/week → speed up to 2h/week!)
- Privacy: Not started (target: 5h/week)

**Calculation:** 100 hours ÷ hours per week = weeks remaining

---

## ⚠️ System Health Checks

**Update these weekly during Sunday review:**

### Time Management:
- [ ] Phone-free mornings (6-7am): 1/7 days this week
- [ ] Digital sunset (9pm): 0/7 nights this week
- [ ] Sunday review completed: ⬜ (complete this!)

### Anti-Quit:
- [ ] Updated 100-Hour Tracker: ✅ (see above)
- [ ] Still in Stealth Mode: ✅
- [ ] No impulse quits: ✅

### Enneagram Awareness:
- [ ] Noticed comparison urges: 0 times this week
- [ ] Used daily mantra: 0/7 days (need to start!)
- [ ] Competed with self (not others): ✅

---

## 🎯 This Week's Focus (Week 2: Nov 10-16)

### Must Complete:
- [ ] 4 workouts (Mon/Wed/Fri + Sat)
- [ ] Track expenses 7/7 days
- [ ] Delete Twitter/YouTube apps
- [ ] Set up Screen Time limits
- [ ] First XRPL coding session

### Stretch Goals:
- [ ] Sign Pre-Commitment Contracts
- [ ] Install Phase 2 plugins (Tasks, Tracker, Meta Bind)
- [ ] Start Gmail migration planning

---

## 📝 Quick Notes

**Dashboard Usage Tips:**

1. **After installing Dataview:**
   - The table queries above will auto-populate with your data
   - No manual updates needed for queries

2. **Manual updates required:**
   - 100-Hour Tracker numbers (weekly)
   - System Health Checks (weekly)
   - This Week's Focus checkboxes (weekly)

3. **To test if Dataview works:**
   - Look at "Recent Daily Notes" section
   - Should show 3 sample notes (Nov 7, 8, 9)
   - If blank: Check Dataview settings enabled

4. **Future enhancements:**
   - Advanced Progress Bars will visualize 100-hour tracker
   - Obsidian Tracker will show workout heatmap
   - Charts View will show screen time trends

---

## 🔗 Quick Links

**Goal Documents:**
- [[Quarterly-Goals-2025-Q4]] - Master Q4 goals
- [[Q4-Success-Framework]] - System integration
- [[Weekly-Plan]] - Current week plan

**Project Tracking:**
- [[Health-and-Fitness-Goals]] - Fitness details
- [[Financial-Goals]] - Finance details
- [[Digital-Wellness-Privacy-Goal]] - Digital wellness
- [[Learn-XRPL-Ledger]] - XRPL learning

**Setup:**
- [[Obsidian-Plugins-Q4-Setup-Guide]] - Plugin installation guide
- [[Plugin-Setup-Corrections]] - Verified syntax reference

---

## 🚀 Getting Started

**New to this dashboard? Start here:**

1. ✅ **Install Dataview plugin** (if you haven't already)
   - Settings → Community Plugins → Browse → "Dataview"
   - Install → Enable
   - Settings → Dataview → Enable all 3 checkboxes

2. ✅ **Verify tables are working**
   - Scroll up to "Recent Daily Notes" section
   - Should see 3 sample notes
   - If blank, Dataview needs configuration

3. ✅ **Create today's daily note**
   - Use template: [[Daily-Note]]
   - Save in `Daily-Notes/` folder
   - Fill in frontmatter (energy_level, mood, etc.)

4. ✅ **Update 100-Hour Tracker weekly**
   - Every Sunday during weekly review
   - Add hours spent on each goal this week
   - Track progress toward 100-hour commitment

5. ✅ **Complete System Health Checks weekly**
   - Review all three sections (Time Management, Anti-Quit, Enneagram)
   - Check boxes for what you accomplished
   - Identify areas needing attention

---

*Dashboard auto-updates via Dataview queries*
*Manual updates: 100-Hour Tracker, Health Checks (weekly)*
*Next dashboard review: Sunday, November 16, 2025*
