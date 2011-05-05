<%inherit file="_templates/site.mako" />

<p>Here are a few filter tests:</p>

<p>Normal filter call: </p>
<%self:filter chain="markdown">

This is markdown
----------------

 * Item
 * Item
 * Item

[Blogofile](http://www.blogofile.com) is cool.

</%self:filter>

<p>Run a filter from an absolute plugin reference: </p>
<div id="original_plugin_filter">
<%self:filter chain="bf.config.plugins.plugin_test.filters.filter_to_override">
This will be replaced with text from the plugin
</%self:filter>
</div>

<div id="overriden_plugin_filter">
<p>Run a filter from an overridden filter: </p>
<%self:filter chain="filter_to_override">
This will be replaced with text from the userspace filter
</%self:filter>
</div>

