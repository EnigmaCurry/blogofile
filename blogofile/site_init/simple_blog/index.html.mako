<%inherit file="_templates/site.mako" />
<p>
 This is the index page.
</p>

Here's the main <a href="${bf.util.site_path_helper(bf.config.blog.path)}">chronological blog page</a><br/><br/>

Here's the last 5 posts:
<ul>
% for post in bf.config.blog.posts[:5]:
    <li><a href="${post.path}">${post.title}</a></li>
% endfor
</ul>
