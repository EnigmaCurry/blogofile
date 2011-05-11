<aside>
  <section>
    <h1 class="post_header_gradient theme_font">Latest Posts</h1>
    <ul>
      % for post in bf.config.blog.iter_posts_published(5):
      <li><a href="${post.path}">${post.title}</a></li>
      % endfor
    </ul>
  </section>
  <section>
    <h1 class="post_header_gradient theme_font">From Twitter "example"</h1>
    <div id="on_twitter">
      <div id="tweets"></div>
      <a href="http://search.twitter.com/search?q=example" style="float: right">See more tweets</a>
    </div>
  </section>
</aside>
