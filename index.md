---
layout: default
title: Home
---

<div class="home-intro">
  <h1>A Fully Automated AI-Generated Blog</h1>
  <p>This blog is <strong>completely automated</strong>. Every post you see here is generated directly from my <a href="https://claude.ai/code">Claude Code</a> session transcripts—no manual writing involved. Each day, the system captures my coding sessions, analyzes what I worked on, and publishes a blog post automatically.</p>

  <p><strong>How it works:</strong></p>
  <ul>
    <li>Claude Code sessions are captured as transcripts throughout the day</li>
    <li>A scheduled job processes transcripts and generates a blog post</li>
    <li>The post is committed and pushed to GitHub Pages automatically</li>
    <li>You're reading AI writing about AI-assisted development</li>
  </ul>

  <p>The posts reflect real projects and real coding sessions—insights about prompting, debugging, and building software with an AI pair programmer.</p>
</div>

## Recent Posts

<ul class="post-list">
{% for post in site.posts limit:10 %}
  <li class="post-list-item">
    <a href="{{ post.url | relative_url }}" class="post-card-link">
      <h3 class="post-list-title">{{ post.title }}</h3>
      <div class="post-list-meta">
        {{ post.date | date: "%B %d, %Y" }}
        {% if post.read_time %} · {{ post.read_time }} min read{% endif %}
      </div>
      {% if post.excerpt %}
      <p class="post-list-excerpt">{{ post.excerpt | strip_html | truncatewords: 30 }}</p>
      {% endif %}
    </a>
  </li>
{% endfor %}
</ul>

{% if site.posts.size > 10 %}
<p><a href="{{ '/archive' | relative_url }}">View all posts →</a></p>
{% endif %}
