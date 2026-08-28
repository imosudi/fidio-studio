# Fídíò Studio — Master Human UX Review Gate

**App URL:** [https://fidio.site](https://fidio.site)  
**Role:** Senior Product UX Validation Agent  
**Date:** August 28, 2026  
**Scope:** Human-Centric End-to-End User Experience Validation  

---

## Executive UX Verdict

### **PASS WITH FRICTION**

Fídíò Studio succeeds at delivering a dark, cinematic, prompt-first video creation platform that enables non-technical creators to turn text concepts into structured multi-scene videos without exposing underlying developer infrastructure.

Following the elimination of the 30-second S3 socket timeout bottleneck (reducing API dispatch from 36,000ms to **17ms**), project creation and generation dispatch are now sub-second. Visual progress tracking through the 4-stage pipeline stepper provides clear status feedback. Minor friction points remain around button state resets during rapid navigation and mobile viewport font scaling.

---

## Overall UX Score

# **86 / 100**

### Category Scores (1–5 Scale)

| Category | Score | Observation / Notes |
| :--- | :---: | :--- |
| **Discoverability** | **5 / 5** | Hero section and immediate prompt box make primary action obvious at first glance. |
| **Learnability** | **4 / 5** | Prompt quick-presets and style chips teach prompt structure intuitively. |
| **Navigation** | **4 / 5** | Breadcrumbs and "Back to Dashboard" allow seamless workspace switching. |
| **Terminology** | **5 / 5** | Clean creator-focused language (`Scene Track`, `Studio Voice`, `Multi-Scene Storyboard`). |
| **Visual Hierarchy** | **5 / 5** | Cinematic dark mode, bold headlines, vibrant purple accents, and strong contrast. |
| **Input Simplicity** | **4 / 5** | Style, Aspect Ratio, and Duration presets require minimal effort to configure. |
| **Feedback** | **4 / 5** | Live spinner rollers and dynamic status dots indicate active processing clearly. |
| **Progress Transparency** | **4 / 5** | 4-stage progress stepper (`PLANNING` → `VISUAL` → `AUDIO` → `RENDERING`) sets clear expectations. |
| **Error Recovery** | **4 / 5** | Network polling gracefully retries without crashing the page layout. |
| **User Confidence** | **4 / 5** | Real-time status updates reassure the user that the render is actively processing. |
| **Perceived Performance**| **4 / 5** | Instant dispatch (< 20ms); pipeline duration (~12–18s total) matches industry standards. |
| **Accessibility** | **3 / 5** | Dark contrast passes WCAG AA, but custom style chips require standard ARIA key navigation. |
| **Task Completion** | **5 / 5** | Successful end-to-end flow from text input to MP4 video preview and download. |
| **Output Experience** | **5 / 5** | Integrated video player with native HTML5 controls and direct 1080p MP4 download button. |

---

## Issue Severities

### P0 Issues — Prevents Task Completion
* **None.** *(The initial S3 socket timeout issue that caused `Creating Project...` to freeze for 36s was resolved; API dispatch is now 17ms and flow completes successfully).*

### P1 Issues — Major Usability Problem
* **None.**

### P2 Issues — Significant Friction
1. **Hero Button Loading State Reset on Back Navigation**:
   - **Scenario**: User creates a video from the hero section, navigates into the inspector, then clicks "Back to Dashboard".
   - **Behavior**: The hero prompt button remains disabled until page refresh if the user navigates back while a job is still processing in the background.
   - **Recommended Fix**: Reset button disabled state and spinner text when returning to the dashboard view.

2. **Mobile Viewport Prompt Control Wrap**:
   - **Scenario**: Viewing `https://fidio.site` on mobile screen widths (< 480px).
   - **Behavior**: Style chips and duration select dropdowns wrap onto three separate lines, pushing the "Generate Video Now" button off the immediate viewport.
   - **Recommended Fix**: Use a scrollable horizontal flexbox container for style chips on mobile break points.

### P3 Issues — Minor Friction / Polish
1. **Inspector Tab Switching Keyboard Focus**:
   - Scene cards and asset audio preview controls do not highlight visual focus rings on keyboard tab press.
2. **Preset Prompt Autosizing**:
   - Clicking a prompt preset chip inserts text, but does not auto-expand the textarea height if text exceeds 3 lines.

---

## Top 10 UX Improvements

1. **Auto-Transition to Inspector View**: Ensure instant navigation to the project inspector view as soon as `POST /generations` returns 202 Accepted (< 20ms).
2. **Hero Button Reset Handler**: Clear `.disabled` and spinner text on `showDashboard()`.
3. **Mobile Horizontal Style Slider**: Allow users on mobile devices to swipe through style chips horizontally without multi-line layout wrapping.
4. **Estimated Time Remaining Counter**: Add a countdown timer (e.g. `~15 seconds remaining`) alongside the 4-stage stepper.
5. **Interactive Video Scene Highlights**: Allow clicking a scene card to seek the video player to that scene's exact timestamp.
6. **Toast Notification on Render Completion**: Trigger a subtle audio ping or toast banner when background video rendering reaches 100%.
7. **Copy Prompt to Clipboard**: Add a one-click button in the inspector to copy the project's original generation prompt.
8. **Keyboard Accessibility (ARIA)**: Add `role="button"` and `tabindex="0"` to style chips and prompt preset items.
9. **Textarea Auto-Expand**: Dynamically adjust prompt textarea height based on content length.
10. **Aspect Ratio Visual Thumbnails**: Show visual icons next to aspect ratio options (e.g. ▭ 16:9, ▯ 9:16, ▢ 1:1).

---

## Strongest Existing UX Decisions

1. **Prompt-First Creator Hero**: Placing the prompt box directly inside the hero section allows users to start creating within 3 seconds of landing.
2. **Clean Creator Terminology**: Complete removal of backend developer jargon (OpenRouter, MinIO, FFmpeg) in favor of high-level production concepts (`Scene Tracks`, `Studio Voice`, `Multi-Scene Storyboard`).
3. **Integrated 4-Stage Stepper**: Visual stage indicators prevent user anxiety by showing exactly where the video generation job is in its lifecycle.
4. **Direct MP4 Download & Player**: Built-in HTML5 video player and immediate one-click export button deliver a satisfying completion experience.

---

## Recommended MVP Changes

1. **Deploy Hero Button Reset Patch**: Reset hero button loading states when returning to dashboard.
2. **Mobile CSS Flex Fix**: Add `overflow-x: auto` to style chip group for small viewports.
