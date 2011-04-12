<p id="credits">
    Powered by <a href="http://www.blogofile.com">Blogofile</a>.
    <a href="${bf.util.site_path_helper(bf.config.blog.path,'feed')}">Blog RSS Feed</a>.
    % if bf.config.blog.disqus.enabled:
    <a href="http://${bf.config.blog.disqus.name}.disqus.com/latest.rss">Comments RSS Feed</a>.
    % endif
</p>

