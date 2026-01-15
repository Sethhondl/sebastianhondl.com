---
layout: default
title: Archive
---

# All Posts

{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}

{% for year in posts_by_year %}
## {{ year.name }}

<ul class="post-list">
{% for post in year.items %}
  <li class="post-list-item">
    <a href="{{ post.url | relative_url }}" class="post-card-link">
      <span class="post-list-meta">{{ post.date | date: "%b %d" }}</span>
      <span class="post-list-title">{{ post.title }}</span>
    </a>
  </li>
{% endfor %}
</ul>
{% endfor %}
