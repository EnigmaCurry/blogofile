<?xml version="1.0" encoding="UTF-8"?><% from datetime import datetime %>
<rss version="2.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:wfw="http://wellformedweb.org/CommentAPI/"
     >
  <channel>
    <title>${bf.config.blog.name}</title>
    <link>${bf.config.blog.url}</link>
    <description>${bf.config.blog.description}</description>
    <pubDate>${datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>
    <generator>Blogofile</generator>
    <sy:updatePeriod>hourly</sy:updatePeriod>
    <sy:updateFrequency>1</sy:updateFrequency>
% for post in posts[:10]:
    <item>
      <title>${post.title}</title>
      <link>${post.permalink}</link>
      <pubDate>${post.date.strftime("%a, %d %b %Y %H:%M:%S %Z")}</pubDate>
% for category in post.categories:
      <category><![CDATA[${category}]]></category>
% endfor
% if post.guid:
      <guid>${post.guid}</guid>
% else:
      <guid isPermaLink="true">${post.permalink}</guid>
% endif
      <description>${post.title}</description>
      <content:encoded><![CDATA[${post.content}]]></content:encoded>
    </item>
% endfor
  </channel>
</rss>
