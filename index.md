---
layout: schedule
title: "FALL 2026 Schedule"
order: 66
mode: "schedule"
---
# FALL 2026 Schedule

<section class="semester-progress" aria-labelledby="semester-progress-heading">
  <div class="semester-progress-heading">
    <h2 id="semester-progress-heading">Semester Progress</h2>
    <output id="semester-progress-label">Loading semester progress…</output>
  </div>
  <div id="semester-progress-bar" class="semester-progress-bar" role="progressbar" aria-labelledby="semester-progress-heading" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" aria-describedby="semester-progress-detail">
    <span id="semester-progress-fill"></span>
  </div>
  <p id="semester-progress-detail"></p>
</section>

---
## Seeking Fall 2026 and Spring 2027 Project community partners!

If you have a project and are interested in being a CMSE495 community partner for **_Fall 2026_** and/or **_Spring 2027_** please reach out to the course instructor (Dr. Dirk Colbry <colbrydi@msu.edu>). For more information on becoming a project community partner please see our [Project community partner Page](./Seeking-Community_Partners)


---

The CMSE 495 data science capstone course is intended to provide students with an opportunity to put together what they have learned across multiple courses to develop a final project that demonstrates their ability to work in a team on real-world problems.

The capstone course has three major goals:
1. Provide students with a high impact, end-to-end project experience where they can apply classroom experiences and data science skills to solve real-world problems. 
2. Provide students with opportunities to learn and practice professional skills (communication, teamwork and leadership) in the context of team-based projects.
3. Provide opportunities for students and faculty in the department to build relationships and network with industry partners, community organizations, and campus colleagues. 

## Navigating This Website

Students should use the schedule to plan for the semester. Links will appear as instructors add assignments for the semester. Please review this page regularly for updates.

Select the [Course Guide](./Guide) in the menu above to navigate to learn more about the course. This guide includes the syllabus as well as general policies and procedures that students must follow.  

The Table of Contents is provided to help student navigate individual pages. 


<div class="calendar-draft-wrap">
  <h1>CMSE495 Calendar Draft</h1>
  <p>This is a preview page built from the schedule source file. Events are shown at 12:30 PM to 1:40 PM in EGR 1145.</p>

  <p>
    Calendar subscription URL:
    <a href="{{ '/CMSE495_Subscribe.ics' | relative_url }}">{{ '/CMSE495_Subscribe.ics' | relative_url }}</a>
  </p>

  <div class="course-calendar" id="course-calendar">
    <div class="calendar-toolbar" aria-label="Calendar navigation">
      <button type="button" id="prev-month">Previous</button>
      <h2 id="calendar-month" aria-live="polite"></h2>
      <button type="button" id="next-month">Next</button>
      <button type="button" id="today">Today</button>
    </div>

    <div class="calendar-grid" role="grid" aria-labelledby="calendar-month">
      <div class="dow">Sun</div>
      <div class="dow">Mon</div>
      <div class="dow">Tue</div>
      <div class="dow">Wed</div>
      <div class="dow">Thu</div>
      <div class="dow">Fri</div>
      <div class="dow">Sat</div>
      <div id="calendar-days"></div>
    </div>
  </div>

  <h3>Events in Selected Day</h3>
  <ul id="day-events"></ul>
</div>

<script id="schedule-data" type="application/json">{{ site.data.schedule | jsonify }}</script>

<style>
  .semester-progress {
    margin: 1.5rem 0;
    padding: 1rem 1.25rem;
    background: #edf4ee;
    border: 1px solid #cad7cd;
    border-radius: 14px;
  }

  .semester-progress-heading {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
  }

  .semester-progress h2,
  #semester-progress-label {
    margin: 0;
    font-family: "Avenir Next", "Segoe UI", sans-serif;
  }

  #semester-progress-label {
    font-weight: 700;
  }

  .semester-progress-bar {
    height: 1rem;
    margin-top: 0.6rem;
    overflow: hidden;
    background: #ffffff;
    border: 1px solid #aebfb2;
    border-radius: 999px;
  }

  #semester-progress-fill {
    display: block;
    width: 0;
    height: 100%;
    background: #1f5c45;
    border-radius: inherit;
    transition: width 0.25s ease;
  }

  #semester-progress-detail {
    margin: 0.45rem 0 0;
    color: #5a665f;
    font-size: 0.92rem;
  }

  .calendar-draft-wrap {
    max-width: 1000px;
    margin: 1.5rem auto;
    padding: 1.25rem;
    background: #fbfdf9;
    border: 1px solid #cad7cd;
    border-radius: 14px;
  }

  .calendar-draft-wrap h1,
  .calendar-draft-wrap h2,
  .calendar-draft-wrap h3 {
    font-family: "Avenir Next", "Segoe UI", sans-serif;
  }

  .course-calendar {
    margin-top: 1rem;
    border: 1px solid #cad7cd;
    border-radius: 12px;
    background: #ffffff;
    overflow: hidden;
  }

  .calendar-toolbar {
    display: grid;
    grid-template-columns: 120px 1fr 120px;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-bottom: 1px solid #cad7cd;
    background: #edf4ee;
  }

  .calendar-toolbar h2 {
    margin: 0;
    text-align: center;
    font-size: 1.15rem;
  }

  .calendar-toolbar button {
    border: 1px solid #1f5c45;
    border-radius: 8px;
    padding: 0.45rem 0.65rem;
    background: #1f5c45;
    color: #ffffff;
    font: inherit;
    cursor: pointer;
  }

  .calendar-toolbar button:hover {
    background: #174534;
  }

  .calendar-toolbar #today {
    grid-column: 2;
    justify-self: center;
    background: #ffffff;
    color: #1f5c45;
  }

  .calendar-toolbar #today:hover {
    background: #edf4ee;
  }

  .calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
  }

  .calendar-grid .dow {
    padding: 0.45rem;
    text-align: center;
    font-family: "Avenir Next", "Segoe UI", sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    background: #f4f8f5;
    border-bottom: 1px solid #cad7cd;
  }

  #calendar-days {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
  }

  .calendar-day {
    min-height: 110px;
    border-right: 1px solid #edf1ee;
    border-bottom: 1px solid #edf1ee;
    padding: 0.35rem;
  }

  .calendar-day:nth-child(7n) {
    border-right: 0;
  }

  .calendar-day.is-outside {
    background: #f9fbfa;
    color: #7d8a82;
  }

  .calendar-day.is-today {
    background: #edf7f1;
  }

  .calendar-day button {
    border: 0;
    background: transparent;
    font: inherit;
    font-weight: 700;
    padding: 0;
    cursor: pointer;
    color: #1b221d;
  }

  .calendar-day ul {
    margin: 0.35rem 0 0;
    padding-left: 1rem;
    font-size: 0.82rem;
    line-height: 1.3;
  }

  .calendar-day li {
    margin: 0.1rem 0;
  }

  #day-events {
    margin-top: 0.5rem;
  }

  #day-events li {
    margin: 0.35rem 0;
  }

  @media (max-width: 800px) {
    .calendar-toolbar {
      grid-template-columns: 1fr 1fr;
    }

    .calendar-toolbar h2 {
      grid-column: 1 / -1;
      order: -1;
    }

    .calendar-toolbar #today {
      grid-column: auto;
    }

    .semester-progress-heading {
      align-items: flex-start;
      flex-direction: column;
      gap: 0.25rem;
    }

    .calendar-day {
      min-height: 90px;
    }

    .calendar-day ul {
      font-size: 0.76rem;
      padding-left: 0.8rem;
    }
  }
</style>

<script>
  (function () {
    const classTime = "12:30 PM - 1:40 PM";
    const classLocation = "EGR 1145";
    const baseUrl = "{{ site.baseurl | default: '' }}";

    const raw = document.getElementById("schedule-data");
    const events = JSON.parse(raw.textContent || "[]");

    const monthLabel = document.getElementById("calendar-month");
    const daysContainer = document.getElementById("calendar-days");
    const dayEvents = document.getElementById("day-events");
    const prevBtn = document.getElementById("prev-month");
    const nextBtn = document.getElementById("next-month");
    const todayBtn = document.getElementById("today");
    const progressBar = document.getElementById("semester-progress-bar");
    const progressFill = document.getElementById("semester-progress-fill");
    const progressLabel = document.getElementById("semester-progress-label");
    const progressDetail = document.getElementById("semester-progress-detail");

    const byDate = events.reduce((acc, event) => {
      if (!event.date) {
        return acc;
      }
      if (!acc[event.date]) {
        acc[event.date] = [];
      }
      acc[event.date].push(event);
      return acc;
    }, {});

    function parseISODate(str) {
      const parts = str.split("-").map(Number);
      return new Date(parts[0], parts[1] - 1, parts[2]);
    }

    function formatISODate(date) {
      const y = date.getFullYear();
      const m = String(date.getMonth() + 1).padStart(2, "0");
      const d = String(date.getDate()).padStart(2, "0");
      return `${y}-${m}-${d}`;
    }

    const sortedDates = Object.keys(byDate).sort();
    const todayDate = new Date();
    todayDate.setHours(0, 0, 0, 0);
    const today = formatISODate(todayDate);
    const firstScheduleDate = sortedDates[0];
    const lastScheduleDate = sortedDates[sortedDates.length - 1];
    const nextScheduledDate = sortedDates.find((date) => date >= today);
    const isDuringSemester = firstScheduleDate && today >= firstScheduleDate && today <= lastScheduleDate;
    const initialSelectedDate = isDuringSemester ? today : (nextScheduledDate || today);
    const initialMonthDate = parseISODate(initialSelectedDate);
    let currentMonth = new Date(initialMonthDate.getFullYear(), initialMonthDate.getMonth(), 1);
    let selectedDate = initialSelectedDate;

    function renderSemesterProgress() {
      if (!firstScheduleDate || !lastScheduleDate) {
        progressLabel.textContent = "Schedule dates are not available.";
        progressDetail.textContent = "";
        return;
      }

      const firstDate = parseISODate(firstScheduleDate);
      const lastDate = parseISODate(lastScheduleDate);
      const totalDays = Math.max(1, Math.round((lastDate - firstDate) / 86400000));
      const elapsedDays = Math.round((todayDate - firstDate) / 86400000);
      const percent = Math.min(100, Math.max(0, Math.round((elapsedDays / totalDays) * 100)));
      const dateRange = `${firstDate.toLocaleDateString(undefined, { month: "short", day: "numeric" })}–${lastDate.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}`;

      progressFill.style.width = `${percent}%`;
      progressBar.setAttribute("aria-valuenow", String(percent));
      progressLabel.textContent = `${percent}% complete`;
      progressDetail.textContent = `Semester schedule: ${dateRange}.`;
    }

    function renderSelectedDay() {
      const selected = byDate[selectedDate] || [];
      dayEvents.innerHTML = "";

      if (selected.length === 0) {
        const empty = document.createElement("li");
        empty.textContent = `No scheduled items for ${selectedDate}.`;
        dayEvents.appendChild(empty);
        return;
      }

      selected.forEach((event) => {
        const li = document.createElement("li");

        if (event.url) {
          const link = document.createElement("a");
          link.href = `${baseUrl}${event.url}`;
          link.textContent = event.title;
          li.appendChild(link);
        } else {
          li.textContent = event.title;
        }

        li.appendChild(document.createTextNode(` (${classTime}, ${classLocation})`));
        dayEvents.appendChild(li);
      });
    }

    function renderMonth() {
      daysContainer.innerHTML = "";

      const year = currentMonth.getFullYear();
      const month = currentMonth.getMonth();
      const firstDay = new Date(year, month, 1);
      const startWeekday = firstDay.getDay();
      const monthLabelText = firstDay.toLocaleDateString(undefined, { month: "long", year: "numeric" });
      monthLabel.textContent = monthLabelText;

      const gridStart = new Date(year, month, 1 - startWeekday);
      for (let i = 0; i < 42; i += 1) {
        const dayDate = new Date(gridStart.getFullYear(), gridStart.getMonth(), gridStart.getDate() + i);
        const iso = formatISODate(dayDate);

        const dayBox = document.createElement("div");
        dayBox.className = "calendar-day";

        if (dayDate.getMonth() !== month) {
          dayBox.classList.add("is-outside");
        }
        if (iso === today) {
          dayBox.classList.add("is-today");
        }

        const dayButton = document.createElement("button");
        dayButton.type = "button";
        dayButton.textContent = String(dayDate.getDate());
        dayButton.setAttribute("aria-label", `Show events for ${iso}`);
        dayButton.addEventListener("click", function () {
          selectedDate = iso;
          renderSelectedDay();
        });
        dayBox.appendChild(dayButton);

        const todaysEvents = byDate[iso] || [];
        if (todaysEvents.length > 0) {
          const list = document.createElement("ul");
          todaysEvents.slice(0, 2).forEach((event) => {
            const li = document.createElement("li");
            if (event.url) {
              const link = document.createElement("a");
              link.href = `${baseUrl}${event.url}`;
              link.textContent = event.title;
              li.appendChild(link);
            } else {
              li.textContent = event.title;
            }
            list.appendChild(li);
          });

          if (todaysEvents.length > 2) {
            const extra = document.createElement("li");
            extra.textContent = `+${todaysEvents.length - 2} more`;
            list.appendChild(extra);
          }
          dayBox.appendChild(list);
        }

        daysContainer.appendChild(dayBox);
      }
    }

    prevBtn.addEventListener("click", function () {
      currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1);
      renderMonth();
    });

    nextBtn.addEventListener("click", function () {
      currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1);
      renderMonth();
    });

    todayBtn.addEventListener("click", function () {
      selectedDate = today;
      currentMonth = new Date(todayDate.getFullYear(), todayDate.getMonth(), 1);
      renderMonth();
      renderSelectedDay();
    });

    renderSemesterProgress();
    renderMonth();
    renderSelectedDay();
  })();
</script>

<!-- TOC_START -->
<div class="page-toc">
<h2>On this page</h2>

<details>
<summary>FALL 2026 Schedule</summary>
<ul>

<li><a href="#seeking-fall-2026-and-spring-2027-project-community-partners">Seeking Fall 2026 and Spring 2027 Project community partners!</a></li>
<li><a href="#navigating-this-website">Navigating This Website</a></li>
</ul>
</details>
</div>
<!-- TOC_END -->
