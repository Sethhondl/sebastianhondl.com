---
layout: default
title: Home
---

<div class="home-intro">
  <h1>Welcome to My AI Development Journey</h1>
  <p>This blog documents my daily experiences building software with <a href="https://claude.ai/code">Claude Code</a> as my AI pair programmer. Each post is a reflection on what I worked on, what I learned, and insights about AI-assisted development.</p>

  <p><strong>What you'll find here:</strong></p>
  <ul>
    <li>Real projects and real problems solved with AI assistance</li>
    <li>Insights about effective prompting and collaboration with AI</li>
    <li>Code snippets, techniques, and patterns</li>
    <li>Honest reflections on what works and what doesn't</li>
  </ul>
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
