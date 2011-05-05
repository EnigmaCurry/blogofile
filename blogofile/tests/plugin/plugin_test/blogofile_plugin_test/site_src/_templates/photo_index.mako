<%inherit file="plugin_base_template" />

This is just a stupid photo gallery as a demonstration plugin for
Blogofile. It's meant to be as simplistic as possible so as to be easy
to read.

<table>
% for photo in photos:
  <tr><td><a href="${photo}.html"><img src="img/${photo}" height="175"></a></td><td>${photo}</td></tr>
% endfor
</table>
