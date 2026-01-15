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
    <span class="post-list-meta">{{ post.date | date: "%b %d" }}</span>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
  </li>
{% endfor %}
</ul>
{% endfor %}
