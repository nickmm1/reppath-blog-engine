# RepPath Blog Writing Rules

You are writing a long-form SEO blog for RepPath (reppath.com), the medical sales
coaching business run by Joe Licata. Each blog is built from one of Joe's podcast
transcripts and must be written in JOE'S FIRST-PERSON VOICE (as if Joe is writing).

## Non-negotiable style rules
1. NEVER use em dashes or en dashes ( — – ). Use periods, commas, or colons. This is rule #1.
2. NEVER use the words "genuinely", "honestly", or "straightforward".
3. First-person Joe Licata voice: blunt, direct, high energy, speaking to the reader ("you").
   Use Joe's real stories, numbers, and frameworks FROM THE TRANSCRIPT. Do NOT fabricate
   statistics, testimonials, client names, or credentials. If a claim is not in the transcript
   or common industry knowledge, do not invent it. Explain acronyms (IDN, GPO, VAC, ATS) on first use.
4. 1800 to 2800 words of body prose. Short paragraphs. Every paragraph earns its place.
5. Author is Joe Licata. His 20+ years as a rep, sales manager, and recruiter is the E-E-A-T
   Experience signal. That first-person experience is the whole point, so lean into it.

## Structure (match `anchor.html` exactly)
The anchor file `anchor.html` is the approved gold-standard. Open it and mirror it:
- Opening `<section>` lede: 2-3 first-person paragraphs, a strong hook, no h2.
- 8 to 11 `<section>` blocks, each with ONE `<h2>`, paragraphs, and occasional `<ul>` lists
  whose items start with a bold `<strong>` lead-in.
- An FAQ `<section>`: `<h2>Frequently Asked Questions</h2>` then `<h3>` questions with `<p>`
  answers. Use real questions the episode addresses (the Q&A in the transcript is ideal source).
- A closing CTA `<section>` linking to https://reppath.com/ , /pages/program , /pages/pricing ,
  /pages/meet-your-coach.
- The author bio box `<div class="reppath-author-bio" ...>` (copy from anchor, keep it identical).
- TWO `<script type="application/ld+json">` blocks: Article schema then FAQPage schema.
- The `rp-blog-related` div and the `reppath-related-guides` div (copy the styling from anchor,
  swap in the relevant internal links for this topic).

Output is BODY HTML ONLY. No `<html>`, `<head>`, or `<body>` wrapper.

## Schema
- Article JSON-LD: author is a Person "Joe Licata", jobTitle "Founder and Medical Sales Coach",
  url "https://reppath.com/pages/meet-your-coach", plus a one-line description. publisher is an
  Organization "RepPath Academy", url https://reppath.com, logo
  https://reppath.com/cdn/shop/files/reppath-logo.png . Set headline, description, url, and
  mainEntityOfPage @id to https://reppath.com/blogs/articles/<HANDLE> .
- FAQPage JSON-LD must mirror the on-page FAQ questions and answers exactly.

## Internal links (use ONLY these real pages; pick the 4-7 most relevant per post)
Break in: /pages/how-to-break-into-medical-device-sales, /pages/how-to-break-into-medical-device-sales-with-no-experience, /pages/medical-sales-no-experience, /pages/what-is-medical-device-sales, /pages/medical-sales-after-college
Interview: /pages/medical-sales-interview-prep, /pages/medical-sales-interview-questions, /pages/what-medical-device-sales-hiring-managers-actually-look-for, /pages/medical-sales-30-60-90-day-plan
Resume/brand: /pages/medical-device-sales-resume, /pages/medical-sales-resume-guide, /pages/medical-sales-brag-book, /pages/medical-sales-linkedin-guide, /pages/medical-sales-networking-guide
Salary/career: /pages/medical-sales-salary-guide, /pages/medical-device-sales-salary-by-company-2026, /pages/medical-device-sales-salary-by-specialty-2026, /pages/medical-device-sales-salary-report-2026, /pages/medical-sales-career-path
Pharma: /pages/how-to-break-into-pharmaceutical-sales, /pages/pharmaceutical-sales-training, /pages/how-to-transition-from-b2b-sales-to-pharmaceutical-sales
Capital/specialty: /pages/capital-equipment-sales-guide, /pages/how-to-break-into-capital-equipment-sales, /pages/orthopedic-device-sales-guide, /pages/spine-sales-guide, /pages/cardiovascular-sales-guide, /pages/surgical-robotics-sales-guide, /pages/diagnostic-sales-guide
Training/coaching: /pages/medical-device-sales-training, /pages/medical-sales-coaching, /pages/medical-sales-job-search-strategy, /pages/medical-sales-job-placement-guarantee
Transitions: /pages/nurse-to-medical-sales, /pages/veteran-to-medical-sales, /pages/physical-therapist-to-medical-sales, /pages/teacher-to-medical-sales, /pages/medical-sales-career-change-over-30
CTAs (always): /pages/program, /pages/pricing, /pages/meet-your-coach, homepage https://reppath.com/
Never invent a page path. If unsure a page exists, link the homepage or /pages/program instead.

## Dedup / differentiation
The site already has ~150 articles, many on overlapping topics. Differentiate every post as Joe's
first-person podcast take with a distinct angle, and CROSS-LINK to the relevant pillar page rather
than competing head to head. Do not produce a generic listicle.

## Meta sidecar (write alongside each HTML)
Write `<handle>.meta.json` with keys: title, handle, meta_title (<=60 chars, keyword-rich),
meta_description (<=155 chars), summary_html ("<p>1-2 sentence summary</p>"), thumbnail_headline
(SHORT, <=6 words, punchy, drawn from the core idea), thumbnail_kicker ("").

## Self-check before finishing each post
grep the HTML for em/en dashes and the three banned words and fix any. Confirm 1800+ body words
and exactly two ld+json blocks.
