<%inherit file="base.mako" />
<!doctype html>
<!--[if lt IE 7 ]> <html lang="en" class="no-js ie6"> <![endif]-->
<!--[if IE 7 ]>    <html lang="en" class="no-js ie7"> <![endif]-->
<!--[if IE 8 ]>    <html lang="en" class="no-js ie8"> <![endif]-->
<!--[if IE 9 ]>    <html lang="en" class="no-js ie9"> <![endif]-->
<!--[if (gt IE 9)|!(IE)]><!--> <html lang="en" class="no-js"> <!--<![endif]-->
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
${self.head()}
</head>
  <body>
    <div id="container" class="container container_12">
      <div id="main" role="main">
        <div id="main_block">
          ${self.header()}
          <div id="prose_block" class="grid_8">
            ${next.body()}
          </div>
          <div id="sidebar" class="grid_4">
            ${self.sidebar()}
          </div>
          <div class="clear"></div>
        </div>
      </div>
      ${self.footer()}
    </div>
    ${self.body_scripts()}
  </body>
</html>
<%def name="head()"><%include file="head.mako" /></%def>
<%def name="header()"><%include file="header.mako" /></%def>
<%def name="sidebar()"><%include file="sidebar.mako" /></%def>
<%def name="footer()"><%include file="footer.mako" /></%def>
<%def name="body_scripts()"><%include file="body_scripts.mako" /></%def>
