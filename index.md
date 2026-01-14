---
layout: default
title: Home
---

<div class="home-intro">

# Welcome to My AI Development Journey

This blog documents my daily experiences building software with [Claude Code](https://claude.ai/code) as my AI pair programmer. Each post is a reflection on what I worked on, what I learned, and insights about AI-assisted development.

**What you'll find here:**
- Real projects and real problems solved with AI assistance
- Insights about effective prompting and collaboration with AI
- Code snippets, techniques, and patterns
- Honest reflections on what works and what doesn't

</div>

## Recent Posts

<ul class="post-list">
{% for post in site.posts limit:10 %}
  <li class="post-list-item">
    <h3 class="post-list-title">
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    </h3>
    <div class="post-list-meta">
      {{ post.date | date: "%B %d, %Y" }}
      {% if post.read_time %} · {{ post.read_time }} min read{% endif %}
    </div>
    {% if post.excerpt %}
    <p class="post-list-excerpt">{{ post.excerpt | strip_html | truncatewords: 30 }}</p>
    {% endif %}
  </li>
{% endfor %}
</ul>

{% if site.posts.size > 10 %}
<p><a href="{{ '/archive' | relative_url }}">View all posts →</a></p>
{% endif %}
