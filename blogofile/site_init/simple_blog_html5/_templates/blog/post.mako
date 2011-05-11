<%page args="post"/>

<% 
   category_links = []
   for category in post.categories:
       if post.draft:
           #For drafts, we don't write to the category dirs, so just write the categories as text
           category_links.append(category.name)
       else:
           category_links.append("<a href='%s'>%s</a>" % (category.path, category.name))
%>

<div class="blog_post">
  <article>
    <header class="post_header_gradient">
      <div class="date theme_font2">
        <div class="year">${post.date.year}</div>
        <div class="day">${post.date.day}</div>
        <div class="month">${post.date.strftime("%b")}</div>
      </div>
      <a name="${post.slug}"></a>
      <h1 class="blog_post_title theme_font"><a href="${post.permapath()}" rel="bookmark" title="Permanent Link to ${post.title}">${post.title}</a></h2>
    </header>
    <div class="post_body">
      <div class="post_prose">
        ${self.post_prose(post)}
      </div>
    </div>
    <footer class="post_footer_gradient">
      <div class="right">
       <span class="blog_post_categories">${", ".join(category_links)}</span>
       % if bf.config.blog.disqus.enabled:
       | <a href="${post.permalink}#disqus_thread">View Comments</a>
       % endif
      </div>
    </footer>
  </article>
</div>

<%def name="post_prose(post)">
${post.content}
</%def>
